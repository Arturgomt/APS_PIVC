"""Download explícito e verificado dos pesos oficiais do OpenCV Zoo."""

import hashlib
from pathlib import Path
import tempfile
from urllib.request import urlopen

REVISAO = "48b10fa505aeb51fbd127fc60a5c660040e823b7"
PASTA_PADRAO = Path(__file__).resolve().parents[1] / "modelos"
MODELOS = {
    "yunet": {
        "arquivo": "face_detection_yunet_2023mar.onnx",
        "diretorio": "face_detection_yunet",
        "sha256": "8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4",
    },
    "sface": {
        "arquivo": "face_recognition_sface_2021dec.onnx",
        "diretorio": "face_recognition_sface",
        "sha256": "0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79",
    },
}


def caminhos_modelos(pasta: str | Path | None = None) -> dict[str, Path]:
    raiz = Path(pasta) if pasta is not None else PASTA_PADRAO
    return {chave: raiz / dados["arquivo"] for chave, dados in MODELOS.items()}


def sha256(arquivo: Path) -> str:
    resumo = hashlib.sha256()
    with arquivo.open("rb") as origem:
        while bloco := origem.read(1024 * 1024):
            resumo.update(bloco)
    return resumo.hexdigest()


def preparar_modelos(pasta: str | Path | None = None) -> dict[str, Path]:
    caminhos = caminhos_modelos(pasta)
    for chave, destino in caminhos.items():
        esperado = MODELOS[chave]
        if destino.exists():
            if sha256(destino) != esperado["sha256"]:
                raise ValueError(f"Modelo com hash divergente: {destino}. Preserve-o separadamente e refaça o download.")
            continue
        destino.parent.mkdir(parents=True, exist_ok=True)
        url = (
            f"https://media.githubusercontent.com/media/opencv/opencv_zoo/{REVISAO}"
            f"/models/{esperado['diretorio']}/{esperado['arquivo']}"
        )
        temporario = None
        try:
            with tempfile.NamedTemporaryFile(dir=destino.parent, suffix=".part", delete=False) as arquivo:
                temporario = Path(arquivo.name)
                with urlopen(url, timeout=60) as resposta:
                    while bloco := resposta.read(1024 * 1024):
                        arquivo.write(bloco)
            if sha256(temporario) != esperado["sha256"]:
                raise ValueError(f"Download do modelo {chave} não corresponde ao hash oficial.")
            temporario.replace(destino)
        finally:
            if temporario is not None:
                temporario.unlink(missing_ok=True)
    return caminhos
