"""Aquisição, qualidade e alinhamento facial compatível com SFace."""

from .configuracao import CONTRATO_SFACE, Configuracao
from .integracao import reconhecer
from .pipeline import ProcessadorFacial
from .tipos import Resultado, Status

__all__ = ["CONTRATO_SFACE", "Configuracao", "ProcessadorFacial", "Resultado", "Status", "reconhecer"]
