# Demonstração anterior com webcam

**Para o projeto atual, que recebe rostos já alinhados, siga o [README.md](README.md).**
As instruções abaixo são somente da demonstração anterior `app.py` com câmera.

Requer Python 3.11 ou 3.12, webcam e internet para baixar dependencias e modelos.
No PowerShell, abra esta pasta e execute:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py baixar-modelos
.\.venv\Scripts\python.exe app.py cadastrar --nome "Artur"
.\.venv\Scripts\python.exe app.py cadastrar --nome "Maria"
.\.venv\Scripts\python.exe app.py identificar
```

No cadastro, pressione ESPACO cinco vezes, variando levemente a posicao do rosto.
Mantenha apenas a pessoa a cadastrar no quadro. Q ou Esc encerra. Sair antes das
cinco amostras cancela o novo cadastro. Um nome existente tem suas amostras
substituidas ao completar o novo cadastro. Prefira nomes/identificadores unicos.
Se necessario, acrescente `--camera 1`. Nomes acentuados sao salvos corretamente,
mas a fonte do OpenCV pode nao exibi-los corretamente no video.

```powershell
.\.venv\Scripts\python.exe app.py identificar --limiar 0.5 --margem 0.05
.\.venv\Scripts\python.exe app.py excluir --nome "Artur"
```

## Divisao do processamento

Camera -> detectar rosto (YuNet) -> alinhar e recortar (SFace) -> gerar embedding
(SFace) -> comparar com todas as pessoas -> aplicar limiar e margem.

`FacePipeline.prepare_faces` e a parte a substituir pela implementacao do colega.
`FacePipeline.embed` recebe uma imagem BGR uint8 de 112x112 alinhada conforme SFace.
Apenas redimensionar um recorte nao garante o mesmo alinhamento. Combinem os pontos
faciais e a transformacao geometrica. O mesmo preparo deve ser usado no cadastro
e na identificacao. `identify` recebe um embedding normalizado e busca na base.

## Limites e validacao

- Limiar 0.5 e margem 0.05 sao escolhas experimentais, sem validacao neste ambiente.
  Similaridade nao e probabilidade. Maior limiar tende a reduzir falsas aceitacoes,
  mas aumenta rejeicoes. Avalie com pessoas conhecidas e desconhecidas, em sessoes
  diferentes das do cadastro. Meça erros, latencia e efeito do tamanho da base.
- O prototipo nao tem prova de vida, verificacao de identidade no cadastro,
  controle de qualidade robusto, estabilizacao temporal nem autenticacao.
  Nao usar para liberar acesso ou tomar decisoes reais.
- A comparacao e exata e linear: cada frame consulta todas as amostras. Adequado
  como demonstracao de base pequena; medir antes de aumentar a escala.
- Nao grava fotos nem videos. Embeddings e nomes ficam em `cadastros.json`,
  sem criptografia. Sao dados sensiveis: use participantes autorizados em ambiente
  controlado, restrinja acesso e exclua ao terminar. Nao envie esse arquivo ao Git.
- Execucao local; apenas o download inicial acessa os servidores de modelos.
- Verifique as licencas dos pesos antes de distribuir ou usar comercialmente:
  https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet
  https://github.com/opencv/opencv_zoo/tree/main/models/face_recognition_sface

Referencia de API: https://docs.opencv.org/4.9.0/d0/dd4/tutorial_dnn_face.html
