# Requisitos da APS (UNIP 2026/2)

## Trabalho escrito

A4, Arial 12, espaçamento 1,5, margens esquerda e direita de 2,5 cm. Versão física em espiral com capa transparente.

| Seção | Páginas |
|---|---|
| Objetivo | 1 a 2 |
| Introdução | 2 a 8 |
| Fundamentos das técnicas de reconhecimento facial | 10 a 20 |
| Plano de desenvolvimento | 5 a 15 |
| Projeto / estrutura do programa | 18 a 35 |

Incluir capa (curso, tema, nomes e RAs), índice, relatório de código, bibliografia e a ficha de APS com as atividades em ordem cronológica.

## Entregas

- Grupos de 3 a 5 integrantes; nota: 30% apresentação e 70% trabalho escrito.
- Acompanhamento e relatório de código no Teams.
- Demonstração do programa e entrega final no site da UNIP.
- Prazo de postagem: **12/11/2026**.

## Fases do enunciado no código

| Fase | Onde |
|---|---|
| Aquisição | `processamento_imagens/aquisicao.py` e câmera do site |
| Pré-processamento | `processamento_imagens/pipeline.py` |
| Segmentação | `processamento_imagens/alinhamento.py` (YuNet) |
| Extração de características | `Reconhecimento Facial/alinhado.py` (SFace) |
| Classificação e permissões | `alinhado.py` (1:N) e `api.py` (níveis 1 a 3) |
