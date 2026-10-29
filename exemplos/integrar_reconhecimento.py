"""Cadastro e identificação integrados por arquivo ou webcam."""

import argparse
import importlib.util
import json
from pathlib import Path
import sys

import cv2

from processamento_imagens import CONTRATO_SFACE, ProcessadorFacial, reconhecer
from processamento_imagens.aquisicao import ErroAquisicao, Webcam, ler_imagem
from processamento_imagens.modelos import caminhos_modelos

RAIZ = Path(__file__).resolve().parents[1]
MODULO_PADRAO = RAIZ / "Reconhecimento Facial" / "alinhado.py"


def carregar_servico(modulo: str | Path, banco: str | Path, pasta_modelos=None, *, threshold=0.5, margin=0.05):
    caminho = Path(modulo).resolve()
    if not caminho.is_file():
        raise ValueError(f"Módulo do colega não encontrado: {caminho}")
    especificacao = importlib.util.spec_from_file_location("aps_reconhecimento_externo", caminho)
    if especificacao is None or especificacao.loader is None:
        raise ValueError("Informe o caminho para o arquivo alinhado.py do colega.")
    colega = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(colega)
    if getattr(colega, "VERSION", None) != CONTRATO_SFACE:
        raise ValueError("O contrato do módulo recebido difere do contrato SFace desta entrega.")
    return colega.RecognitionService(database=Path(banco),
                                     model_path=caminhos_modelos(pasta_modelos)["sface"],
                                     threshold=threshold, margin=margin)


def _webcam(args, processador, servico):
    nome, quantidade, ultimo = "APS PIVC - Identificacao", 0, None
    try:
        with Webcam(args.camera) as camera:
            while True:
                frame = camera.ler()
                ultimo = reconhecer(processador.processar(frame), servico)
                quantidade += 1
                if not args.sem_janela:
                    exibicao = frame.copy()
                    for rosto in ultimo["processamento"]["rostos"]:
                        x, y, w, h = rosto["caixa_original_xywh"]
                        cv2.rectangle(exibicao, (x, y), (x + w, y + h), (0, 180, 255), 2)
                    reconhecimento = ultimo["reconhecimento"]
                    rotulo = ultimo["processamento"]["status"]
                    if reconhecimento is not None:
                        rotulo = reconhecimento["status"]
                        if reconhecimento.get("person_id") is not None:
                            rotulo += ": " + str(reconhecimento["person_id"])
                    cv2.putText(exibicao, rotulo, (16, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.putText(exibicao, "Q/ESC: sair | Identificacao sem autorizacao de acesso", (16, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.imshow(nome, exibicao)
                    if cv2.waitKey(1) & 0xFF in (27, ord("q")) or cv2.getWindowProperty(nome, cv2.WND_PROP_VISIBLE) < 1:
                        break
                if args.max_frames is not None and quantidade >= args.max_frames:
                    break
    finally:
        if not args.sem_janela:
            cv2.destroyAllWindows()
    print(json.dumps(ultimo, ensure_ascii=False, indent=2))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modulo", default=str(MODULO_PADRAO), help="Módulo de reconhecimento; padrão: cópia incluída no projeto.")
    parser.add_argument("--limiar", type=float, default=0.5)
    parser.add_argument("--margem", type=float, default=0.05)
    parser.add_argument("--modelos", help="Pasta dos modelos preparados pela sua parte.")
    parser.add_argument("--banco", default=str(RAIZ / "dados" / "cadastros_alinhados.json"))
    fonte = parser.add_mutually_exclusive_group(required=True)
    fonte.add_argument("--entrada", nargs="+", help="Fotos originais; serão processadas antes do reconhecimento.")
    fonte.add_argument("--webcam", action="store_true")
    parser.add_argument("--cadastrar", metavar="ID", help="Cadastra o ID com todas as fotos de --entrada.")
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--max-frames", type=int)
    parser.add_argument("--sem-janela", action="store_true")
    args = parser.parse_args(argv)
    if not -1 <= args.limiar <= 1 or not 0 <= args.margem <= 2:
        parser.error("Limiar deve estar em [-1,1] e margem em [0,2].")
    if args.camera < 0 or (args.max_frames is not None and args.max_frames <= 0):
        parser.error("Índice da câmera deve ser >= 0 e limite de frames deve ser positivo.")
    if args.webcam and args.sem_janela and args.max_frames is None:
        parser.error("Webcam sem janela requer --max-frames.")
    if args.cadastrar and args.webcam:
        parser.error("Neste exemplo, o cadastro utiliza fotos com --entrada.")
    if args.entrada and not args.cadastrar and len(args.entrada) != 1:
        parser.error("Para identificar, informe uma foto; para cadastrar, use --cadastrar ID.")
    try:
        processador = ProcessadorFacial(pasta_modelos=args.modelos)
        servico = carregar_servico(args.modulo, args.banco, args.modelos, threshold=args.limiar, margin=args.margem)
        if args.webcam:
            return _webcam(args, processador, servico)
        resultados = [processador.processar(ler_imagem(p)) for p in args.entrada]
        if args.cadastrar:
            imagens = [r.entrada_reconhecimento for r in resultados]
            if any(imagem is None for imagem in imagens):
                print(json.dumps({"status": "cadastro_rejeitado", "capturas": [r.resumo() for r in resultados]}, ensure_ascii=False, indent=2))
                return 2
            servico.register(args.cadastrar, imagens)
            print(json.dumps({"status": "cadastrado", "person_id": args.cadastrar, "amostras": len(imagens)}, ensure_ascii=False))
            return 0
        saida = reconhecer(resultados[0], servico)
        print(json.dumps(saida, ensure_ascii=False, indent=2))
        return 0 if saida["reconhecimento"] and saida["reconhecimento"]["status"] == "candidato" else 2
    except (ErroAquisicao, ValueError, OSError, cv2.error) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
