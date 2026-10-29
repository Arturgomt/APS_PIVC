# Prototipo com entrada ja alinhada

**Para instalar e rodar o projeto passo a passo, comece pelo [README.md](README.md).**
Este arquivo mantém as notas técnicas de integração.

Use `alinhado.py`. O arquivo anterior `app.py` e uma demonstracao separada com webcam.
Este novo modulo nao abre a camera nem detecta ou alinha rostos.

## Relacao com a APS

O enunciado pede identificacao/autenticacao facial em tempo real e permissoes em
tres niveis. Este modulo cobre extracao de caracteristicas e classificacao, as
duas ultimas etapas do diagrama do enunciado. O processamento anterior pertence
ao outro modulo da equipe. O ID retornado permite consultar as permissoes gerais,
de diretores por divisao ou do ministro em um componente separado. Identificar
um candidato nao concede acesso automaticamente. A politica por divisao e a
eventual hierarquia de niveis precisam ser definidas pela equipe.

`exemplo_integracao.py` mostra a funcao a chamar com cada rosto recebido. O teste
com arquivos exercita o mesmo metodo que recebe matrizes em memoria no fluxo ao
vivo. A captura, transporte entre processos, prova de vida e interface de permissoes
nao estao implementados neste modulo; o sistema completo ainda precisa integra-los.

## Contrato com quem processa a imagem

- Um rosto por entrada, com alinhamento geometrico compativel com SFace.
- Matriz NumPy uint8, BGR, shape (112,112,3), valores entre 0 e 255.
- Para arquivos, use PNG ou JPEG. A leitura converte o arquivo para BGR.
- Para matrizes RGB em memoria, converta com `cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)`.
- Nao forneca imagem normalizada em floats ou um frame inteiro de camera.
- O recorte deve seguir a mesma referencia geometrica de `FaceRecognizerSF.alignCrop`;
  ter 112x112 pixels, sozinho, nao garante compatibilidade. Uma imagem alinhada
  para outro modelo pode precisar ser preparada novamente pelo colega.
- Cadastro e consulta devem passar pelo mesmo processamento. Combinem uma imagem
  de exemplo e validem a integracao antes de coletar os cadastros.

## Instalar e usar (PowerShell, Python 3.11)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe alinhado.py baixar-modelo
.\.venv\Scripts\python.exe alinhado.py cadastrar --id pessoa_001 artur_1.png artur_2.png
.\.venv\Scripts\python.exe alinhado.py cadastrar --id pessoa_002 maria_1.png maria_2.png
.\.venv\Scripts\python.exe alinhado.py identificar consulta.png
.\.venv\Scripts\python.exe alinhado.py --limiar 0.5 --margem 0.05 identificar consulta.png
.\.venv\Scripts\python.exe alinhado.py excluir --id pessoa_001
```

Os nomes das imagens sao exemplos: substitua pelos arquivos reais alinhados.
Use varias amostras de boa qualidade por pessoa, idealmente quantidade semelhante
entre pessoas. Novos IDs sao registrados sem retreinar o modelo. IDs existentes
nao sao sobrescritos: exclua explicitamente antes de recadastrar.

## Integracao Python

```python
from alinhado import RecognitionService, read_image

service = RecognitionService()  # instanciar uma vez e reutilizar
rosto_bgr = read_image('consulta.png')  # ou matriz recebida do colega
resultado = service.identify(rosto_bgr)
print(resultado)
```

Saida ilustrativa: `{"status":"candidato","person_id":"pessoa_001","similarity":0.72}`.
Tambem retorna `desconhecido`, `inconclusivo` ou `sem_cadastros`, com ID nulo.
O score e similaridade de cosseno, nao uma probabilidade nem certeza de identidade.
O candidato so e retornado quando passa o limiar e a margem em relacao a segunda
pessoa. Busca exata linear por todas as amostras, com a maior similaridade por pessoa.

## Limites

Limiar 0.5 e margem 0.05 sao experimentais. Calibre com dados separados do cadastro
e avalie falsos reconhecimentos, rejeicoes e pessoas desconhecidas em sessoes novas.
Nao ha prova de vida, filtro robusto de qualidade ou validacao de identidade no cadastro.
Nao usar para liberar acesso. O modulo e local e de um unico processo; nao e uma API
HTTP nem suporta escritores simultaneos no JSON. A base fica em
`cadastros_alinhados.json`, sem criptografia, com dados biometricos sensiveis.
Restrinja o acesso, use participantes autorizados e exclua os dados apos os testes.
Nenhuma imagem e gravada pelo programa; somente IDs e embeddings. Downloads iniciais
acessam a internet; inferencia e comparacao sao locais.

Modelo e licenca: https://github.com/opencv/opencv_zoo/tree/main/models/face_recognition_sface
API: https://docs.opencv.org/4.9.0/d0/dd4/tutorial_dnn_face.html

## Testes de logica

```powershell
.\.venv\Scripts\python.exe -m unittest -v test_alinhado.py
```

Os testes usam vetores sinteticos e simulam a extracao para verificar persistencia.
Cobrem candidatos, desconhecidos, ambiguidades, entrada invalida, cadastro duplicado
e exclusao. Nao medem a precisao com pessoas reais nem substituem a calibracao.
