# APS PIVC — Projeto do grupo

## Executar processamento e reconhecimento juntos

O ponto de entrada integrado é **`aps.py`**. O processamento já entrega o rosto
alinhado ao SFace em memória; o JSON exibido é apenas o resumo do resultado.

```powershell
cd "C:\APS - PIVC\APS_PIVC"
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m processamento_imagens preparar-modelos
```

Instalação e download são feitos uma vez. Nesta cópia, o ambiente foi preparado
durante a revisão. Use fotos originais dos participantes, com um único rosto:

```powershell
# Substitua os arquivos de exemplo pelas suas fotos reais.
.\.venv\Scripts\python.exe aps.py --cadastrar pessoa_001 --entrada dados/artur_1.jpg dados/artur_2.jpg
.\.venv\Scripts\python.exe aps.py --entrada dados/consulta.jpg
.\.venv\Scripts\python.exe aps.py --webcam --camera 0
```

Cadastro e consulta passam pelo mesmo processamento. A identificação pela câmera
usa os cadastros anteriores; este comando não cadastra pela webcam. Q/Esc ou fechar
a janela encerra a sessão. Sem fotos cadastradas, o reconhecimento responde
`sem_cadastros`. Os arquivos ilustrados acima não acompanham o projeto.

O comando seleciona automaticamente `Reconhecimento Facial/alinhado.py`, usa
`modelos/` e grava referências em `dados/cadastros_alinhados.json`. Não misture essa
base com a base da demonstração antiga `Reconhecimento Facial/app.py`.

```powershell
.\.venv\Scripts\python.exe aps.py --help
.\.venv\Scripts\python.exe aps.py --limiar 0.5 --margem 0.05 --entrada dados/consulta.jpg
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

O limiar e a margem são experimentais; precisam ser calibrados. Consulte
[a integração](docs/INTEGRACAO.md) e [a revisão técnica](docs/REVISAO_INTEGRACAO.md).
O fluxo integrado devolve candidatos, não autorizações de acesso. A API do front-end,
o banco SQL e os três níveis de permissão continuam fora deste módulo.

| Componente | Guia |
|---|---|
| Front-end IRIS / Vite publicado pelo grupo | [Documentação do front-end](docs/FRONTEND.md) |
| Captura, qualidade e alinhamento facial em Python | Instruções abaixo |

Este guia detalha o módulo de processamento. Os arquivos de front-end já publicados pelo grupo são preservados. A conexão HTTP entre a interface e os módulos Python ainda depende da aplicação de integração da equipe.

Entrega da pessoa 3: captura por webcam ou arquivo, ajuste proporcional de resolução, controle de qualidade, detecção YuNet e alinhamento facial **compatível com o módulo SFace recebido do grupo**.

**Saída:** um rosto BGR `uint8` com formato **(112, 112, 3)**, alinhado por `FaceRecognizerSF.alignCrop`. A imagem segue em memória para `RecognitionService.identify`. O processamento não determina identidade nem concede acesso.

## Executar

Abra um terminal na pasta deste projeto. É necessário Python 3.11 ou superior.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m processamento_imagens preparar-modelos
.venv\Scripts\python.exe -m processamento_imagens webcam --camera 0
```

O último comando acima abre somente o processamento. Para identificar pessoas,
use `aps.py --webcam` conforme o início deste guia. Não é necessário ativar o ambiente
nem alterar a política do PowerShell. Em Linux/macOS, use `.venv/bin/python`.

O download explícito prepara YuNet e SFace na pasta `modelos/`, verifica SHA-256 e fixa a revisão oficial. Depois disso, o processamento funciona sem rede. Modelos ausentes geram uma orientação; abrir a webcam não dispara downloads.

**Q**, **Esc** ou fechar a janela encerra a sessão. As caixas e os cinco pontos faciais aparecem no frame. Verde indica uma amostra preparada, ainda sem identificação da pessoa.

Para processar uma foto ou exportar as etapas:

```powershell
.venv\Scripts\python.exe -m processamento_imagens imagem --entrada dados/foto.png
.venv\Scripts\python.exe -m processamento_imagens imagem --entrada dados/foto.png --saida saidas --salvar-imagens
.venv\Scripts\python.exe -m processamento_imagens webcam --saida saidas --salvar-imagens
```

Na webcam, **S** exporta o frame quando `--saida` estiver definido; o último frame também é exportado no encerramento normal. Sem `--salvar-imagens`, apenas JSON é gravado. Sem `--saida`, nenhum arquivo de captura é criado.

## Pastas do processamento

```text
APS_PIVC/
├── processamento_imagens/   Código da sua parte
│   ├── aquisicao.py        Webcam e leitura de arquivos
│   ├── configuracao.py     Parâmetros e contrato SFace
│   ├── alinhamento.py      YuNet e alignCrop
│   ├── pipeline.py         Coordenação e qualidade
│   ├── tipos.py            Resultados, estados e imagem de saída
│   ├── modelos.py          Preparação dos pesos oficiais
│   ├── integracao.py       Passagem ao serviço do colega
│   ├── saida.py            Exportações opcionais
│   └── cli.py              Comandos e janela da webcam
├── exemplos/               Cadastro e consulta com alinhado.py externo
├── tests/                  Testes automatizados
├── docs/                   Diretrizes, integração e texto técnico
├── scripts/                Gerador do relatório de código
├── modelos/                Pesos locais; somente o README vai ao Git
├── dados/                  Imagens e cadastros locais
├── saidas/                 Resultados e relatório para o Teams
└── .local/                 Backup, enunciado e material recebido para análise
```

Os dados, pesos, resultados, backup e ambiente virtual ficam fora do Git. Os READMEs das pastas explicam onde colocar cada arquivo.

## Integrar ao reconhecimento do grupo

```python
from processamento_imagens import ProcessadorFacial, reconhecer
from processamento_imagens.aquisicao import ler_imagem

# servico é uma instância de RecognitionService do módulo alinhado.py do colega.
processador = ProcessadorFacial()
resultado = processador.processar(ler_imagem("dados/foto.png"))
# resposta = reconhecer(resultado, servico)
```

`reconhecer` só chama o serviço se a captura tiver exatamente um rosto, qualidade aprovada e alinhamento válido. O serviço incluído em `Reconhecimento Facial/alinhado.py` recebe o caminho do modelo explicitamente. Veja os comandos em [docs/INTEGRACAO.md](docs/INTEGRACAO.md).

## Qualidade e demonstração das etapas

O fluxo de identidade utiliza BGR preservado, com resize proporcional e alinhamento geométrico. Brilho e nitidez são medidos no recorte cinza antes de qualquer filtro. As versões suavizada e com CLAHE são exportações didáticas da APS; não substituem a imagem colorida enviada ao SFace.

Limites iniciais: brilho médio entre 40 e 215; variância do Laplaciano a partir de 60; lado mínimo da face 60 pixels; confiança YuNet a partir de 0,9. Ajuste os limites com a câmera do grupo:

```powershell
.venv\Scripts\python.exe -m processamento_imagens webcam --nitidez-minima 60 --brilho-minimo 40 --brilho-maximo 215 --confianca-deteccao 0.9
.venv\Scripts\python.exe -m processamento_imagens --help
```

Os estados são `ok`, `imagem_invalida`, `sem_rosto`, `multiplos_rostos`, `qualidade_insuficiente` e `alinhamento_invalido`. Uma captura rejeitada entrega `entrada_reconhecimento = None`. No comando `imagem`, códigos 0/2/1 indicam amostra preparada/captura rejeitada/erro operacional. Na webcam, 0 indica encerramento normal; consulte o JSON para o estado da última amostra.

## Testar e entregar

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe scripts/relatorio_codigo.py
```

- [Contrato, cadastro e identificação](docs/INTEGRACAO.md)
- [Requisitos da APS e divisão das fases](docs/DIRETRIZES.md)
- [Texto técnico para o trabalho escrito](docs/RELATORIO_PROCESSAMENTO.md)
- [Resultados e roteiro de validação](docs/VALIDACAO.md)
- [Organização e envio ao GitHub](docs/GITHUB.md)

**Mudança da versão 0.1 para 0.2:** a saída antiga cinza 128×128 `float32` foi substituída pelo contrato BGR 112×112 `uint8`. Os parâmetros Haar e `--tamanho-rosto` foram retirados; o tamanho SFace é fixo. As capturas exportadas anteriormente não devem ser usadas como referências desta versão; faça o cadastro com o preparo atual.
