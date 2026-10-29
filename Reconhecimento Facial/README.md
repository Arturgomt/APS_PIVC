# Reconhecimento facial com rostos alinhados

Este protótipo identifica uma pessoa entre os cadastros existentes (busca 1:N).
Ele recebe um rosto já processado e alinhado, gera um embedding com SFace e compara
esse vetor com as referências cadastradas. Execute **`alinhado.py`**.

O programa funciona pelo terminal: não abre câmera, janela ou página web. A captura
e o alinhamento pertencem ao outro módulo da equipe. `app.py` é uma demonstração
anterior com webcam e não é usado nos passos deste README.

## 1. O que você precisa

- Windows com PowerShell.
- Python 3.11 ou 3.12 instalado. A execução local foi verificada com Python 3.12.
- Internet para instalar as bibliotecas e baixar o modelo na primeira execução.
- Imagens reais de rostos **já alinhados ao padrão SFace**, para cadastro e consulta.

O programa executa na CPU; não exige GPU. Se precisar instalar o Python, use a
[página oficial de downloads](https://www.python.org/downloads/windows/).

Verifique a versão disponível:

```powershell
py --version
```

## 2. Abrir a pasta do projeto

Abra o PowerShell e entre na pasta que contém `alinhado.py` e `requirements.txt`.
Na localização atual deste projeto, o comando é:

```powershell
cd "C:\Users\Artur Gomes\Documents\Codex\2026-10-23\pre-2\outputs\reconhecimento-facial"
Get-ChildItem
```

Se mover a pasta ou usar outro computador, ajuste o caminho do `cd`.
Todos os comandos seguintes devem ser executados **dentro dessa pasta**.

## 3. Criar o ambiente e instalar as dependências

Com Python 3.12:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Se você tiver Python 3.11, troque somente o primeiro comando por
`py -3.11 -m venv .venv`. Se o comando `py` não existir, mas `python --version`
mostrar Python 3.11 ou 3.12, use `python -m venv .venv`.

Os comandos usam diretamente o Python do ambiente. Não é necessário executar
`Activate.ps1` nem alterar a política de execução do PowerShell.

Verifique a instalação:

```powershell
.\.venv\Scripts\python.exe -c "import cv2, numpy; print('OpenCV:', cv2.__version__); print('NumPy:', numpy.__version__)"
```

## 4. Baixar o modelo

```powershell
.\.venv\Scripts\python.exe alinhado.py baixar-modelo
```

Aguarde a mensagem `Modelo disponivel.`. O arquivo será salvo em
`models/face_recognition_sface_2021dec.onnx`. Se já existir, o download será pulado.
Não é necessário baixar o YuNet para este módulo.

## 5. Organizar as imagens

Crie uma pasta para suas imagens de teste:

```powershell
New-Item -ItemType Directory -Force imagens
```

Copie para ela os arquivos fornecidos pelo colega responsável pelo processamento.
Exemplo de organização — **as imagens abaixo não acompanham o projeto**:

```text
reconhecimento-facial/
├── alinhado.py
├── requirements.txt
├── models/
│   └── face_recognition_sface_2021dec.onnx
└── imagens/
    ├── artur_1.png
    ├── artur_2.png
    ├── maria_1.png
    ├── maria_2.png
    └── consulta.png
```

Cada arquivo deve conter um único rosto, com **112 × 112 pixels e alinhamento
geométrico compatível com `FaceRecognizerSF.alignCrop` do SFace**. PNG e JPEG são
aceitos. Apenas redimensionar uma foto para 112 × 112 não garante esse alinhamento.

Na integração em memória, a entrada deve ser uma matriz NumPy `uint8`, BGR,
com formato `(112, 112, 3)` e valores de 0 a 255. A leitura dos arquivos já entrega
BGR. Cadastro e consulta precisam passar pelo mesmo processamento.

## 6. Cadastrar as pessoas

Cadastre as referências de cada pessoa com um identificador único:

```powershell
.\.venv\Scripts\python.exe alinhado.py cadastrar --id pessoa_001 "imagens/artur_1.png" "imagens/artur_2.png"
.\.venv\Scripts\python.exe alinhado.py cadastrar --id pessoa_002 "imagens/maria_1.png" "imagens/maria_2.png"
```

Substitua os caminhos pelas suas imagens. Cada cadastro aceita uma ou mais imagens;
prefira várias amostras de boa qualidade e uma quantidade semelhante por pessoa.

Resposta esperada para o primeiro comando:

```json
{"status": "cadastrado", "person_id": "pessoa_001"}
```

O programa cria `cadastros_alinhados.json` automaticamente, ao lado de `alinhado.py`.
Ele guarda IDs e embeddings, não cópias das imagens. Não é necessário treinar
novamente o modelo ao cadastrar alguém. Não edite esse JSON manualmente.

## 7. Identificar um rosto

Use uma nova imagem alinhada, preferencialmente de outra captura:

```powershell
.\.venv\Scripts\python.exe alinhado.py identificar "imagens/consulta.png"
```

Exemplo ilustrativo de resposta, que depende das suas imagens:

```json
{"status": "candidato", "person_id": "pessoa_001", "similarity": 0.72}
```

| Status | Significado |
| --- | --- |
| `candidato` | Um ID passou os critérios de similaridade e separação entre candidatos. |
| `desconhecido` | Nenhum cadastro atingiu o limite mínimo. |
| `inconclusivo` | Os dois melhores candidatos ficaram próximos demais. |
| `sem_cadastros` | A base está vazia; cadastre pessoas primeiro. |

Nos três últimos casos, `person_id` é `null`. `similarity` é similaridade de
cosseno, **não porcentagem de certeza**; fica `null` quando não há cadastros.

Para experimentar outros critérios, coloque as opções **antes** de `identificar`:

```powershell
.\.venv\Scripts\python.exe alinhado.py --limiar 0.5 --margem 0.05 identificar "imagens/consulta.png"
```

Esses são os valores padrão experimentais. O limiar define a similaridade mínima;
a margem define a diferença mínima entre as duas melhores pessoas. Precisam de
calibração com imagens diferentes das usadas no cadastro, incluindo desconhecidos.

## 8. Excluir ou atualizar um cadastro

Para excluir:

```powershell
.\.venv\Scripts\python.exe alinhado.py excluir --id pessoa_001
```

Para atualizar, exclua explicitamente o ID e execute novamente o comando de cadastro
com as novas imagens. Um ID existente não é sobrescrito automaticamente.

## 9. Integrar com o código do colega

Salve o código de integração na mesma pasta de `alinhado.py`, ou configure o import
no projeto da equipe. Crie o serviço uma vez e reutilize-o para os rostos recebidos:

```python
from alinhado import RecognitionService

servico = RecognitionService()

def ao_receber_rosto(rosto_bgr):
    # rosto_bgr vem do processamento: uint8, BGR, 112x112, alinhado ao SFace.
    resultado = servico.identify(rosto_bgr)
    return resultado
```

Um exemplo executável com arquivo está incluído:

```powershell
.\.venv\Scripts\python.exe exemplo_integracao.py "imagens/consulta.png"
```

O retorno é o mesmo usado na integração em tempo real. O sistema completo ainda
precisa conectar a captura, o processamento e a consulta de permissões. Na APS,
este módulo cobre extração de características e classificação; o ID poderá ser
usado para consultar os três níveis de permissão em outro módulo. Um candidato
reconhecido não recebe autorização de acesso automaticamente.

Cada instância carrega os cadastros ao iniciar. Se outro processo alterar a base,
reinicie o serviço para carregar as alterações. O protótipo não suporta gravações
simultâneas de vários processos.

## 10. Executar os testes

```powershell
.\.venv\Scripts\python.exe -m unittest -v test_alinhado.py
```

Resultado esperado: oito testes e `OK`. Eles verificam decisão, entradas inválidas,
persistência, duplicidade e exclusão. Usam dados sintéticos e simulam a extração,
portanto não precisam de imagens pessoais nem do download do modelo.

Também foi verificado localmente que o SFace real carrega, gera um embedding de
128 valores e permite cadastrar e consultar uma imagem sintética. Isso verifica
o funcionamento técnico, não a precisão do reconhecimento de pessoas.

## Problemas comuns

| Problema | Como resolver |
| --- | --- |
| `py` não reconhecido ou versão não encontrada | Verifique a instalação do Python; use a alternativa da etapa 3. |
| Python da `.venv` não encontrado | Confirme a pasta atual e crie o ambiente conforme a etapa 3. |
| `No module named cv2` ou `numpy` | Instale as dependências com o Python da `.venv` e execute com esse mesmo Python. |
| `Baixe o modelo` | Execute a etapa 4. |
| Falha de rede no download | Verifique internet/proxy e repita o download; não é necessário desativar a verificação de certificados. |
| Arquivo de imagem não encontrado | Confira o nome, a extensão e a pasta; coloque caminhos com espaços entre aspas. |
| Entrada deve ter shape `(112,112,3)` | Peça uma imagem no contrato correto ao responsável pelo processamento. |
| Identificador já cadastrado | Use outro ID ou exclua o cadastro antes de refazê-lo. |
| Base incompatível com o modelo | Confira a versão usada e refaça os cadastros para o modelo/preparo correto, preservando a base anterior separadamente se necessário. |
| Resultado sempre desconhecido | Confira alinhamento e qualidade, cadastros e consistência do processamento antes de ajustar o limiar. |
| Janela da câmera não abriu | É esperado: este módulo recebe rostos já preparados e mostra a resposta no terminal. |

## Limites e dados locais

O projeto é uma demonstração acadêmica. Não tem prova de vida, validação de
identidade no cadastro, filtro robusto de qualidade ou proteção de produção.
Não deve ser usado para liberar acesso real. O JSON contém dados biométricos sem
criptografia: restrinja o acesso, use participantes autorizados e exclua os dados
ao encerrar os testes. Não publique imagens, embeddings ou cadastros no Git.

Depois dos downloads iniciais, a inferência e a comparação são locais. A base e
o modelo ficam ao lado do módulo; caminhos de imagens relativos são resolvidos
a partir da pasta atual do terminal.

Para detalhes técnicos adicionais, consulte [ROSTOS-ALINHADOS.md](ROSTOS-ALINHADOS.md).
Modelo e licença: [SFace no OpenCV Zoo](https://github.com/opencv/opencv_zoo/tree/main/models/face_recognition_sface).
