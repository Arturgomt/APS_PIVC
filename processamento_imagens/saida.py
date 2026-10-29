"""Exportações opcionais; PNG alinhado preserva BGR e não contém anotações."""

from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4

import cv2

from .tipos import Resultado


def salvar_png(caminho: Path, imagem) -> None:
    ok, dados = cv2.imencode(".png", imagem)
    if not ok:
        raise OSError(f"Falha ao codificar imagem: {caminho}")
    dados.tofile(caminho)


def exportar(resultado: Resultado, destino: str | Path, *,
             salvar_imagens: bool = False, configuracao: dict | None = None) -> Path:
    instante = datetime.now(timezone.utc)
    pasta = Path(destino) / (instante.strftime("%Y%m%dT%H%M%S%fZ") + "_" + uuid4().hex[:8])
    pasta.mkdir(parents=True, exist_ok=False)
    resumo = resultado.resumo()
    resumo["exportado_em_utc"] = instante.isoformat()
    resumo["imagens_salvas"] = salvar_imagens
    if configuracao is not None:
        resumo["configuracao"] = configuracao
    if salvar_imagens:
        for nome, imagem in resultado.etapas.items():
            salvar_png(pasta / f"{nome}.png", imagem)
        for i, rosto in enumerate(resultado.rostos, start=1):
            if rosto.imagem_alinhada_bgr is not None:
                salvar_png(pasta / f"rosto_{i:02d}_alinhado_bgr.png", rosto.imagem_alinhada_bgr)
    (pasta / "resultado.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")
    return pasta
