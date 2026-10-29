"""Resultados e contrato compartilhados com o módulo de reconhecimento."""

from dataclasses import dataclass, field
from enum import Enum

import numpy as np

from .configuracao import CONTRATO_SFACE, FORMATO_SFACE


class Status(str, Enum):
    OK = "ok"
    IMAGEM_INVALIDA = "imagem_invalida"
    SEM_ROSTO = "sem_rosto"
    MULTIPLOS_ROSTOS = "multiplos_rostos"
    QUALIDADE_INSUFICIENTE = "qualidade_insuficiente"
    ALINHAMENTO_INVALIDO = "alinhamento_invalido"


@dataclass
class Qualidade:
    brilho_medio: float
    variancia_laplaciano: float
    problemas: list[str] = field(default_factory=list)

    @property
    def aprovada(self) -> bool:
        return not self.problemas

    def resumo(self) -> dict:
        return {
            "aprovada": self.aprovada,
            "brilho_medio": round(self.brilho_medio, 3),
            "variancia_laplaciano": round(self.variancia_laplaciano, 3),
            "problemas": self.problemas,
        }


@dataclass
class Rosto:
    caixa_original: tuple[int, int, int, int]
    caixa_processada: tuple[int, int, int, int]
    pontos_original: list[list[float]]
    confianca_deteccao: float
    qualidade: Qualidade
    imagem_alinhada_bgr: np.ndarray | None = field(default=None, repr=False)

    def resumo(self) -> dict:
        return {
            "caixa_original_xywh": list(self.caixa_original),
            "caixa_processada_xywh": list(self.caixa_processada),
            "pontos_original_xy": self.pontos_original,
            "confianca_deteccao": round(self.confianca_deteccao, 6),
            "formato_rosto_hwc": list(self.imagem_alinhada_bgr.shape) if self.imagem_alinhada_bgr is not None else None,
            "qualidade": self.qualidade.resumo(),
        }


@dataclass
class Resultado:
    status: Status
    mensagem: str
    rostos: list[Rosto] = field(default_factory=list)
    original_hw: tuple[int, int] | None = None
    processada_hw: tuple[int, int] | None = None
    tempo_ms: float = 0.0
    etapas: dict[str, np.ndarray] = field(default_factory=dict, repr=False)

    @property
    def pronto_para_reconhecimento(self) -> bool:
        if self.status != Status.OK or len(self.rostos) != 1 or not self.rostos[0].qualidade.aprovada:
            return False
        imagem = self.rostos[0].imagem_alinhada_bgr
        return isinstance(imagem, np.ndarray) and imagem.shape == FORMATO_SFACE and imagem.dtype == np.uint8

    @property
    def entrada_reconhecimento(self) -> np.ndarray | None:
        """Cópia contígua BGR uint8 (112,112,3), ou None se a captura foi rejeitada."""
        if not self.pronto_para_reconhecimento:
            return None
        return self.rostos[0].imagem_alinhada_bgr.copy(order="C")

    def resumo(self) -> dict:
        return {
            "status": self.status.value,
            "mensagem": self.mensagem,
            "contrato_reconhecimento": CONTRATO_SFACE,
            "pronto_para_reconhecimento": self.pronto_para_reconhecimento,
            "original_hw": self.original_hw,
            "processada_hw": self.processada_hw,
            "tempo_ms": round(self.tempo_ms, 3),
            "quantidade_rostos": len(self.rostos),
            "rostos": [rosto.resumo() for rosto in self.rostos],
        }
