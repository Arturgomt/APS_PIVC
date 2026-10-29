"""Parâmetros de captura e qualidade; o contrato SFace tem tamanho fixo."""

from dataclasses import dataclass
from math import isfinite
from numbers import Real

CONTRATO_SFACE = "sface-2021dec-aligned-112-bgr-v1"
FORMATO_SFACE = (112, 112, 3)


@dataclass(frozen=True)
class Configuracao:
    largura_maxima: int = 960
    tamanho_minimo_rosto: int = 60
    confianca_deteccao: float = 0.9
    limiar_nms: float = 0.3
    brilho_minimo: float = 40.0
    brilho_maximo: float = 215.0
    nitidez_minima: float = 60.0
    clip_limit: float = 2.0

    def __post_init__(self):
        for nome in ("largura_maxima", "tamanho_minimo_rosto"):
            if type(getattr(self, nome)) is not int or getattr(self, nome) <= 0:
                raise ValueError(f"{nome} deve ser um inteiro positivo.")
        for nome in ("confianca_deteccao", "limiar_nms", "brilho_minimo",
                     "brilho_maximo", "nitidez_minima", "clip_limit"):
            valor = getattr(self, nome)
            if isinstance(valor, bool) or not isinstance(valor, Real) or not isfinite(valor):
                raise ValueError(f"{nome} deve ser um número finito.")
        if not 0 < self.confianca_deteccao <= 1 or not 0 < self.limiar_nms <= 1:
            raise ValueError("Confiança e limiar NMS devem estar em (0, 1].")
        if not 0 <= self.brilho_minimo < self.brilho_maximo <= 255:
            raise ValueError("Brilho deve satisfazer 0 <= mínimo < máximo <= 255.")
        if self.nitidez_minima < 0 or self.clip_limit <= 0:
            raise ValueError("Nitidez mínima deve ser >= 0 e clip_limit deve ser > 0.")
