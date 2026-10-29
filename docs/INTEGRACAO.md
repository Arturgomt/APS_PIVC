# Integração com o reconhecimento recebido

## Contrato da versão 0.2

O `alinhado.py` fornecido pelo grupo declara `VERSION = 'sface-2021dec-aligned-112-bgr-v1'`. Esta entrega produz exatamente esse contrato: um rosto BGR `uint8`, formato `(112, 112, 3)`, pixels entre 0 e 255 e alinhamento geométrico feito pelo próprio `FaceRecognizerSF.alignCrop` do OpenCV. Não é um vetor de características; o serviço SFace gera o embedding depois de receber a imagem.

O módulo incluído está em `Reconhecimento Facial/alinhado.py`. `aps.py` usa essa
cópia por padrão; não há dependência de RAR ou de `.local/reconhecimento-recebido/`.

## Chamada em memória

```python
from processamento_imagens import ProcessadorFacial, reconhecer
from processamento_imagens.aquisicao import Webcam
from exemplos.integrar_reconhecimento import carregar_servico, MODULO_PADRAO, RAIZ

processador = ProcessadorFacial()
servico = carregar_servico(MODULO_PADRAO, RAIZ / "dados" / "cadastros_alinhados.json")

with Webcam(0) as camera:
    for _ in range(30):
        resposta = reconhecer(processador.processar(camera.ler()), servico)
        print(resposta["reconhecimento"])
```

Criar os objetos uma vez evita recarregar modelos por frame. `reconhecer` retorna `processamento` e `reconhecimento`. O segundo campo é `None` quando a captura é rejeitada; caso contrário, contém a resposta original do colega (`candidato`, `desconhecido`, `inconclusivo` ou `sem_cadastros`). Nenhum desses estados concede acesso automaticamente.

## Exemplo completo com o arquivo do colega

Prepare os modelos uma vez. Na raiz do projeto, execute:

```powershell
.venv\Scripts\python.exe -m processamento_imagens preparar-modelos
.venv\Scripts\python.exe aps.py --cadastrar pessoa_001 --entrada dados/pessoa_001_a.png dados/pessoa_001_b.png
.venv\Scripts\python.exe aps.py --entrada dados/consulta.png
.venv\Scripts\python.exe aps.py --webcam --camera 0
```

As fotos acima são exemplos e precisam ser fornecidas pelos participantes. São fotos de entrada, ainda não alinhadas: o exemplo aplica a mesma preparação no cadastro e na consulta. Todas as amostras precisam passar na qualidade antes de o cadastro ser enviado ao serviço. O cadastro por este exemplo é feito com fotos; a identificação também pode usar webcam.

`--modulo` é opcional e só deve apontar para código Python confiável. Um módulo
alternativo precisa declarar o mesmo contrato e aceitar `model_path`, `database`,
`threshold` e `margin` no construtor de `RecognitionService`. A integração passa
o caminho de SFace explicitamente, sem alterar variáveis globais do módulo.

O padrão de persistência é `dados/cadastros_alinhados.json`, alterável com `--banco CAMINHO`. Essa base pertence ao reconhecimento recebido e contém IDs e embeddings. Não há banco SQL ou permissões nesta entrega. Reutilize o mesmo `--banco` em cadastro e consulta. Alterações por outro processo exigem recarregar o serviço, conforme o contrato do colega.

Para execução limitada, sem janela:

```powershell
.venv\Scripts\python.exe aps.py --webcam --sem-janela --max-frames 30
```

No exemplo, consulta de foto retorna 0 para candidato, 2 para captura rejeitada ou identidade não determinada e 1 para erro. Cadastro retorna 0 quando salvo e 2 quando alguma captura é rejeitada. A sessão de webcam retorna 0 no encerramento normal e mostra o resultado da última captura. Q/Esc ou fechar a janela encerra a webcam.

## Entrada e saída da sua parte

`processar` recebe uma matriz BGR H×W×3 ou BGRA H×W×4, sempre `uint8`. Imagem cinza é rejeitada pela API: converter artificialmente o antigo recorte cinza para três canais não recupera a informação de cor. A leitura de arquivos e a webcam já entregam BGR. Dados RGB de outra biblioteca precisam de conversão explícita para BGR.

| Campo | Uso |
|---|---|
| `resultado.entrada_reconhecimento` | Cópia contígua da imagem SFace, ou `None` |
| `resultado.pronto_para_reconhecimento` | Um rosto, qualidade aprovada e alinhamento válido |
| `resultado.rostos[i].imagem_alinhada_bgr` | Recorte alinhado; pode existir mesmo em captura rejeitada por qualidade/múltiplos rostos, para diagnóstico |
| `caixa_original` | `(x, y, largura, altura)` na imagem recebida |
| `caixa_processada` | Mesma convenção na imagem redimensionada |
| `pontos_original` | Cinco pontos na ordem do YuNet: dois olhos, nariz e dois cantos da boca |
| `confianca_deteccao` | Pontuação do detector, não confiança de identidade |
| `etapas` | Imagens didáticas, apenas com `incluir_etapas=True` |
| `resumo()` | Metadados serializáveis, incluindo a versão do contrato |

As caixas usam origem no canto superior esquerdo e limites de fim exclusivo. Os pontos são convertidos para a imagem original. As faces são ordenadas pela posição, sem associação de identidade entre frames. Uma detecção ou alinhamento inválido bloqueia toda a captura; o módulo não ignora uma segunda detecção inválida para liberar a primeira.

O consumidor deve usar `entrada_reconhecimento` ou a função `reconhecer`, preservando a verificação de qualidade. Cadastro e consulta precisam usar os mesmos modelos e preparação. Refaça referências produzidas pelo antigo fluxo cinza 128×128.

Referência: [OpenCV — detecção, alinhamento e reconhecimento](https://docs.opencv.org/4.13.0/d0/dd4/tutorial_dnn_face.html).
