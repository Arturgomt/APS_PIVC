# Resultados gerados

Cada exportação cria uma subpasta com `resultado.json`. Com `--salvar-imagens`, também são gravadas as etapas didáticas e `rosto_01_alinhado_bgr.png`, no contrato SFace. As etapas com caixas e pontos são ilustrações; o PNG alinhado não contém essas anotações.

`python scripts/relatorio_codigo.py` gera aqui `relatorio_codigo.txt` para o Teams. Resultados locais ficam fora do Git; somente este README é versionado.

Resultados da versão anterior usam rosto cinza 128×128 e não são entradas compatíveis com o reconhecedor SFace. O histórico anterior foi preservado em `.local/historico/saidas-v0.1/` durante a organização desta cópia local.
