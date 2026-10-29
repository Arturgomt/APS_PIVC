"""Execute depois de cadastrar referencias: python exemplo_integracao.py rosto.png"""
import argparse
import json

from alinhado import RecognitionService, read_image


def reconhecer_rosto_recebido(service, rosto_alinhado):
    """O colega pode chamar esta funcao a cada rosto entregue pelo processamento.

    Entrada: matriz BGR uint8 (112,112,3), alinhada ao SFace.
    Saida: status, person_id e similarity. Nao concede permissoes de acesso.
    Reutilizar a instancia service entre os frames evita recarregar o modelo.
    """
    return service.identify(rosto_alinhado)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('imagem', help='Arquivo de rosto previamente alinhado')
    args = parser.parse_args()
    service = RecognitionService()
    result = reconhecer_rosto_recebido(service, read_image(args.imagem))
    print(json.dumps(result, ensure_ascii=False, indent=2))
