"""YuNet localiza cinco pontos; alignCrop produz o padrão geométrico SFace."""

from pathlib import Path
from typing import Protocol

import cv2
import numpy as np

from .configuracao import Configuracao
from .modelos import caminhos_modelos


class Preparador(Protocol):
    def detectar(self, bgr: np.ndarray) -> np.ndarray | None: ...
    def alinhar(self, bgr: np.ndarray, deteccao: np.ndarray) -> np.ndarray: ...


class PreparadorSFace:
    def __init__(self, config: Configuracao, pasta_modelos: str | Path | None = None):
        caminhos = caminhos_modelos(pasta_modelos)
        ausentes = [str(p) for p in caminhos.values() if not p.is_file()]
        if ausentes:
            raise ValueError(
                "Modelos não encontrados. Execute: python -m processamento_imagens preparar-modelos. "
                "Arquivos ausentes: " + ", ".join(ausentes)
            )
        self.detector = cv2.FaceDetectorYN.create(
            str(caminhos["yunet"]), "", (320, 320),
            config.confianca_deteccao, config.limiar_nms, 5000,
        )
        self.alinhador = cv2.FaceRecognizerSF.create(str(caminhos["sface"]), "")

    def detectar(self, bgr: np.ndarray) -> np.ndarray | None:
        self.detector.setInputSize((bgr.shape[1], bgr.shape[0]))
        _, rostos = self.detector.detect(bgr)
        return rostos

    def alinhar(self, bgr: np.ndarray, deteccao: np.ndarray) -> np.ndarray:
        return self.alinhador.alignCrop(bgr, np.ascontiguousarray(deteccao, dtype=np.float32))
