# Enviar sua parte ao GitHub

Repositório do grupo: https://github.com/Arturgomt/APS_PIVC

Branch da entrega: `feat/processamento-imagens`. Os passos abaixo orientam a conferência e a publicação de alterações nesse módulo.

## Conferir

Abra o terminal na raiz deste projeto, fora do DSpace:

```powershell
git branch --show-current
git status --short
.venv\Scripts\python.exe -m unittest discover -s tests -v
git diff --check
```

Na versão 0.2, conferir também o alinhamento na webcam e a comunicação com o reconhecedor pelo roteiro de `INTEGRACAO.md` e `VALIDACAO.md`. Os pesos ONNX, fotos, cadastros, resultados, `.local/` e `.venv/` não pertencem ao commit.

## Preparar o commit

```powershell
git add .gitignore .github README.md requirements.txt pyproject.toml processamento_imagens exemplos tests scripts docs modelos/README.md dados/README.md saidas/README.md
git diff --cached --stat
git diff --cached --check
git diff --cached --name-only
git commit -m "Adiciona processamento facial alinhado para integração SFace"
git push -u origin feat/processamento-imagens
```

Os READMEs de `modelos/`, `dados/` e `saidas/` são versionados para orientar a organização; seus demais conteúdos são ignorados. O módulo externo permanece na cópia privada de análise. O exemplo aceita o caminho para `alinhado.py` disponibilizado pelo grupo.

O push exige autenticação e permissão de escrita. Depois, abrir a comparação:

https://github.com/Arturgomt/APS_PIVC/compare/main...feat/processamento-imagens

Título sugerido: **Adiciona aquisição, qualidade e alinhamento compatível com SFace**.

Descrição sugerida:

> Implementa a parte de processamento de imagens da APS: captura por webcam ou arquivo, resize proporcional, detecção YuNet, cinco pontos faciais, controle de qualidade e alinhamento SFace BGR uint8 112×112. Inclui exportações didáticas, exemplo de integração com o RecognitionService recebido, documentação e relatório de código.
>
> Validação local: 39 testes aprovados com os ensaios reais opcionais habilitados, incluindo equivalência com alignCrop e cadastro/consulta/recarga/exclusão no serviço externo. A validação biométrica com participantes e a demonstração física da nova versão seguem no roteiro de validação.

O GitHub não substitui o acompanhamento e o relatório de código no Teams, a dissertação e ficha de APS, a demonstração e a entrega final no site da UNIP.
