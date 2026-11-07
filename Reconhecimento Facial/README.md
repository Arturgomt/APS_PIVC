# Reconhecimento facial (SFace)

`alinhado.py` compara um rosto com os cadastrados (busca 1:N). O site usa este módulo
pela `api.py`; os comandos abaixo servem para testar só esta parte.

A entrada é um rosto já alinhado: imagem BGR `uint8`, 112×112, preparada pelo
`processamento_imagens` (`FaceRecognizerSF.alignCrop`).

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe alinhado.py baixar-modelo
.\.venv\Scripts\python.exe alinhado.py cadastrar --id pessoa_001 rosto1.png rosto2.png
.\.venv\Scripts\python.exe alinhado.py identificar consulta.png
.\.venv\Scripts\python.exe alinhado.py excluir --id pessoa_001
.\.venv\Scripts\python.exe -m unittest -v test_alinhado.py
```

| Resposta | Significado |
|---|---|
| `candidato` | Passou do limiar (0,5) e da margem (0,05) |
| `desconhecido` | Nenhum cadastro passou do limiar |
| `inconclusivo` | Duas pessoas ficaram próximas demais |
| `sem_cadastros` | Base vazia |

`app.py` é a versão antiga, com webcam própria (`app.py cadastrar --nome X`, `app.py identificar`).
