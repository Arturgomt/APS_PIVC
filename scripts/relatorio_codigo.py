"""Gera o relatório numerado da sua parte para disponibilização no Teams."""

import argparse
from datetime import datetime, timezone
import hashlib
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saida", default="saidas/relatorio_codigo.txt")
    args = parser.parse_args()
    raiz = Path(__file__).resolve().parents[1]
    arquivos = [
        *sorted((raiz / "processamento_imagens").glob("*.py")),
        *sorted((raiz / "exemplos").glob("*.py")),
        Path(__file__).resolve(),
    ]
    partes = [
        "APS PIVC — Relatório de código: processamento e alinhamento SFace",
        "Gerado em UTC: " + datetime.now(timezone.utc).isoformat(),
        "Contagem de linhas físicas, incluindo comentários e linhas vazias.",
        "Escopo: sua parte, exemplos e gerador. Exclui testes, pesos, dados e código externo.",
        "",
    ]
    total = 0
    for arquivo in arquivos:
        dados = arquivo.read_bytes()
        linhas = dados.decode("utf-8").splitlines()
        total += len(linhas)
        partes.extend([
            f"ARQUIVO: {arquivo.relative_to(raiz).as_posix()}",
            f"LINHAS: {len(linhas)}",
            "SHA-256: " + hashlib.sha256(dados).hexdigest(),
            *[f"{numero:04d} | {linha}" for numero, linha in enumerate(linhas, start=1)],
            "",
        ])
    partes.append(f"TOTAL DE LINHAS FÍSICAS: {total}")
    destino = Path(args.saida)
    if not destino.is_absolute():
        destino = raiz / destino
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(partes) + "\n", encoding="utf-8")
    print(f"Relatório gerado: {destino} ({total} linhas)")


if __name__ == "__main__":
    main()
