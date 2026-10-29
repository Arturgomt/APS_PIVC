"""Execução por imagem ou webcam: python -m processamento_imagens --help."""

import argparse
from dataclasses import asdict
import json
import sys
import unicodedata
from urllib.error import URLError

import cv2

from .aquisicao import ErroAquisicao, Webcam, ler_imagem
from .configuracao import Configuracao
from .modelos import preparar_modelos
from .pipeline import ProcessadorFacial
from .saida import exportar
from .tipos import Status


def parser() -> argparse.ArgumentParser:
    principal = argparse.ArgumentParser(description="APS PIVC: captura e alinhamento facial SFace.")
    comandos = principal.add_subparsers(dest="comando", required=True)
    modelos = comandos.add_parser("preparar-modelos", help="Baixa e verifica YuNet e SFace; executar uma vez.")
    modelos.add_argument("--modelos", help="Pasta dos modelos, opcional.")
    for nome in ("imagem", "webcam"):
        comando = comandos.add_parser(nome)
        comando.add_argument("--modelos", help="Pasta contendo os dois modelos ONNX.")
        comando.add_argument("--saida", help="Diretório opcional para relatórios JSON.")
        comando.add_argument("--salvar-imagens", action="store_true", help="Exporta etapas e rostos alinhados; requer --saida.")
        comando.add_argument("--largura-maxima", type=int, default=960)
        comando.add_argument("--nitidez-minima", type=float, default=60.0)
        comando.add_argument("--confianca-deteccao", type=float, default=0.9)
        comando.add_argument("--brilho-minimo", type=float, default=40.0)
        comando.add_argument("--brilho-maximo", type=float, default=215.0)
        if nome == "imagem":
            comando.add_argument("--entrada", required=True)
        else:
            comando.add_argument("--camera", type=int, default=0)
            comando.add_argument("--sem-janela", action="store_true")
            comando.add_argument("--max-frames", type=int, help="Limita a execução; obrigatório com --sem-janela.")
    return principal


def _relatorio(resultado, config, args):
    resumo = resultado.resumo()
    resumo["configuracao"] = asdict(config)
    if args.saida:
        resumo["pasta_saida"] = str(exportar(
            resultado, args.saida, salvar_imagens=args.salvar_imagens, configuracao=asdict(config),
        ))
    print(json.dumps(resumo, ensure_ascii=False, indent=2))


def _webcam(args, config, processador):
    quantidade, ultimo = 0, None
    nome_janela = "APS PIVC - Processamento SFace"
    try:
        with Webcam(args.camera) as camera:
            while True:
                frame = camera.ler()
                ultimo = processador.processar(frame, incluir_etapas=args.salvar_imagens)
                quantidade += 1
                if not args.sem_janela:
                    exibicao = frame.copy()
                    for rosto in ultimo.rostos:
                        x, y, w, h = rosto.caixa_original
                        cor = (0, 180, 0) if ultimo.pronto_para_reconhecimento else (0, 160, 255)
                        cv2.rectangle(exibicao, (x, y), (x + w, y + h), cor, 2)
                        for px, py in rosto.pontos_original:
                            cv2.circle(exibicao, (round(px), round(py)), 2, (0, 180, 255), -1)
                    mensagem = unicodedata.normalize("NFKD", ultimo.mensagem).encode("ascii", "ignore").decode("ascii")
                    cv2.putText(exibicao, mensagem, (16, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(exibicao, "Q/ESC: sair | S: salvar se --saida", (16, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.imshow(nome_janela, exibicao)
                    tecla = cv2.waitKey(1) & 0xFF
                    if tecla == ord("s") and args.saida:
                        _relatorio(ultimo, config, args)
                    if tecla in (ord("q"), 27) or cv2.getWindowProperty(nome_janela, cv2.WND_PROP_VISIBLE) < 1:
                        break
                if args.max_frames is not None and quantidade >= args.max_frames:
                    break
    finally:
        if not args.sem_janela:
            cv2.destroyAllWindows()
    if ultimo is not None:
        _relatorio(ultimo, config, args)
    return 0


def main(argv=None) -> int:
    argumentos = parser()
    args = argumentos.parse_args(argv)
    if args.comando != "preparar-modelos":
        if args.salvar_imagens and not args.saida:
            argumentos.error("--salvar-imagens requer --saida.")
        if args.comando == "webcam":
            if args.camera < 0 or (args.max_frames is not None and args.max_frames <= 0):
                argumentos.error("--camera deve ser >= 0 e --max-frames deve ser positivo.")
            if args.sem_janela and args.max_frames is None:
                argumentos.error("--sem-janela requer --max-frames.")
    try:
        if args.comando == "preparar-modelos":
            caminhos = preparar_modelos(args.modelos)
            print(json.dumps({k: str(v) for k, v in caminhos.items()}, ensure_ascii=False, indent=2))
            return 0
        config = Configuracao(
            largura_maxima=args.largura_maxima, nitidez_minima=args.nitidez_minima,
            confianca_deteccao=args.confianca_deteccao,
            brilho_minimo=args.brilho_minimo, brilho_maximo=args.brilho_maximo,
        )
        imagem = ler_imagem(args.entrada) if args.comando == "imagem" else None
        processador = ProcessadorFacial(config, pasta_modelos=args.modelos)
        if args.comando == "webcam":
            return _webcam(args, config, processador)
        resultado = processador.processar(imagem, incluir_etapas=args.salvar_imagens)
        _relatorio(resultado, config, args)
        return 0 if resultado.status == Status.OK else 2
    except (ErroAquisicao, ValueError, OSError, URLError, cv2.error) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Execução interrompida.", file=sys.stderr)
        return 130
