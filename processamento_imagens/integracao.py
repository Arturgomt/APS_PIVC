"""Passagem da amostra ao serviço externo, sem conceder permissão de acesso."""

from typing import Protocol

import numpy as np

from .tipos import Resultado


class ServicoReconhecimento(Protocol):
    def identify(self, aligned_bgr: np.ndarray) -> dict: ...


def reconhecer(resultado: Resultado, servico: ServicoReconhecimento) -> dict:
    entrada = resultado.entrada_reconhecimento
    return {
        "processamento": resultado.resumo(),
        "reconhecimento": servico.identify(entrada) if entrada is not None else None,
    }
