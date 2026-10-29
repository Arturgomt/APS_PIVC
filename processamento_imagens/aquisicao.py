"""Leitura de arquivos e acesso à webcam, com liberação garantida."""

from pathlib import Path

import cv2
import numpy as np


class ErroAquisicao(RuntimeError):
    pass


def ler_imagem(caminho: str | Path) -> np.ndarray:
    arquivo = Path(caminho)
    if not arquivo.is_file():
        raise ErroAquisicao(f"Arquivo não encontrado: {arquivo}")
    try:
        # imdecode + fromfile permite caminhos com acentos no Windows.
        dados = np.fromfile(arquivo, dtype=np.uint8)
        imagem = cv2.imdecode(dados, cv2.IMREAD_COLOR) if dados.size else None
    except (OSError, cv2.error) as exc:
        raise ErroAquisicao(f"Não foi possível ler a imagem: {arquivo}") from exc
    if imagem is None:
        raise ErroAquisicao(f"Arquivo vazio, corrompido ou em formato não suportado: {arquivo}")
    return imagem


class Webcam:
    def __init__(self, indice: int = 0, largura: int = 1280, altura: int = 720):
        if type(indice) is not int or indice < 0:
            raise ValueError("O índice da câmera deve ser um inteiro não negativo.")
        if largura <= 0 or altura <= 0:
            raise ValueError("A resolução solicitada deve ser positiva.")
        self.indice, self.largura, self.altura = indice, largura, altura
        self._captura = None

    def __enter__(self):
        self._captura = cv2.VideoCapture(self.indice)
        try:
            if not self._captura.isOpened():
                raise ErroAquisicao(
                    f"Câmera {self.indice} indisponível. Confira conexão, permissões e outros aplicativos."
                )
            # A câmera pode negociar uma resolução diferente da solicitada.
            self._captura.set(cv2.CAP_PROP_FRAME_WIDTH, self.largura)
            self._captura.set(cv2.CAP_PROP_FRAME_HEIGHT, self.altura)
        except Exception:
            self._captura.release()
            self._captura = None
            raise
        return self

    def ler(self) -> np.ndarray:
        if self._captura is None:
            raise ErroAquisicao("Abra a webcam com 'with Webcam() as camera'.")
        ok, frame = self._captura.read()
        if not ok or frame is None or frame.size == 0:
            raise ErroAquisicao("Falha na captura do frame da webcam.")
        return frame

    def __exit__(self, exc_type, exc_value, traceback):
        if self._captura is not None:
            self._captura.release()
            self._captura = None
