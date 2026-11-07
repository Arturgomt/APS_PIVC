# Aquisição, qualidade e alinhamento facial

## Objetivo

O módulo de processamento prepara capturas faciais para o sistema de identificação e autenticação biométrica da APS PIVC. Sua saída é uma imagem facial padronizada, acompanhada do estado da captura e de métricas de qualidade. A identificação e a interpretação das permissões são realizadas pelos componentes seguintes.

A versão atual foi adaptada ao serviço `RecognitionService` fornecido pelo grupo. O contrato de entrada desse serviço exige uma imagem BGR de três canais, tipo `uint8`, com 112×112 pixels e alinhamento geométrico compatível com SFace. O processamento não produz diretamente o embedding de identidade.

## Aquisição e resolução

A captura utiliza `VideoCapture` do OpenCV. O dispositivo é selecionado por índice; abertura e leitura são verificadas e a câmera é liberada ao encerrar a sessão, inclusive em falhas. A resolução solicitada é 1280×720, mas o programa utiliza as dimensões efetivamente negociadas pelo hardware.

Arquivos de referência são lidos por `numpy.fromfile` e `cv2.imdecode`, permitindo caminhos com acentos no Windows. Arquivos vazios, inexistentes ou corrompidos geram mensagens de aquisição específicas. A API de processamento recebe matrizes coloridas BGR ou BGRA `uint8`; imagens BGRA são convertidas para BGR.

A largura é reduzida ao máximo configurado de 960 pixels, mantendo a proporção. Entradas menores não são ampliadas nesse passo. O fator de escala também é utilizado para converter caixas e pontos faciais às coordenadas da captura original.

## Detecção, pontos e segmentação

O detector YuNet fornece uma caixa facial, cinco pontos de referência e uma pontuação de detecção. Os pontos correspondem aos olhos, nariz e cantos da boca. A pontuação filtra candidatos a rosto; não representa uma probabilidade de identidade.

A segmentação utiliza a região facial detectada. A imagem BGR e os pontos retornados pelo YuNet são entregues ao método `FaceRecognizerSF.alignCrop`. Ele realiza o preparo geométrico e produz a imagem 112×112 esperada pelo SFace. O alinhamento depende da posição dos pontos, portanto não equivale a redimensionar um recorte retangular.

Dados não finitos, pontos fora da imagem, geometria degenerada e saídas fora do contrato são rejeitados. Se uma detecção apresentar problema, a captura não é encaminhada ao reconhecimento. Mais de um rosto também bloqueia a amostra, evitando selecionar automaticamente uma pessoa.

## Qualidade e iluminação

A qualidade utiliza o recorte cinza da imagem redimensionada, antes de qualquer filtro ou equalização. O brilho médio resume a intensidade; a variância do Laplaciano serve como indicador heurístico de nitidez. O tamanho da face também é considerado.

Os valores iniciais aceitam brilho de 40 a 215, variância do Laplaciano a partir de 60 e lado mínimo de 60 pixels. Resolução, textura, ruído e condições da câmera influenciam as métricas. Esses valores precisam ser calibrados com capturas dos participantes em condições de desenvolvimento e avaliados com capturas diferentes.

Escala de cinza, filtro gaussiano 3×3 e CLAHE com grade 8×8 e limite 2,0 permanecem disponíveis nas exportações didáticas. Permitem demonstrar operações de processamento digital sem alterar a imagem BGR usada pelo detector e pelo alinhamento de identidade. A imagem enviada ao SFace não é substituída por cinza nem normalizada para `float32` pelo módulo de processamento.

## Contrato e integração

O resultado contém dimensões original e processada, caixas, cinco pontos em coordenadas originais, confiança de detecção, métricas e estado. A propriedade `entrada_reconhecimento` só disponibiliza uma cópia BGR contígua quando existe exatamente um rosto com qualidade e alinhamento aprovados.

A função `reconhecer` recebe esse resultado e uma instância do serviço externo. Ela chama `identify` apenas para amostras válidas e preserva a resposta do colega, sem criar uma decisão de acesso. O exemplo executável também permite cadastrar amostras com `register`, aplicando o mesmo processamento usado na consulta.

Os modelos são carregados uma vez e reutilizados. O download ocorre somente mediante comando explícito, com revisão oficial fixada e verificação SHA-256. As capturas, referências e pesos ficam em diretórios excluídos do Git. A exportação de pixels é opcional; o relatório JSON inclui a identificação do contrato de preparação.

## Interdisciplinaridade

O módulo reúne visão computacional na detecção e no alinhamento; matemática nas coordenadas, transformações e estatísticas; engenharia de software na modularização, testes e contrato de integração; e segurança da informação na distinção entre detecção, identidade candidata e autorização. A interface orienta enquadramento, qualidade e repetição da captura.

## Verificação e limites

Os testes incluem entradas inválidas, qualidade, preservação de cor, coordenadas, bloqueio de múltiplas faces, falhas de alinhamento, aquisição simulada, exportações e passagem ao serviço. Ensaios opcionais com modelos reais verificam equivalência de pixels com `alignCrop` do OpenCV e cadastro, consulta, recarga e exclusão no reconhecedor recebido.

Cadastrar e consultar a mesma imagem é somente um teste técnico da integração. Não mede a precisão com pessoas em sessões diferentes. A demonstração física da nova versão e a avaliação com amostras separadas, incluindo desconhecidos, precisam ser realizadas pelo grupo. O sistema completo ainda deve associar a identidade candidata às permissões dos três níveis e à divisão correspondente.

## Referências

- OPENCV. *DNN-based Face Detection And Recognition*. OpenCV 4.13.0. https://docs.opencv.org/4.13.0/d0/dd4/tutorial_dnn_face.html. Acesso em: 26 out. 2026.
- OPENCV. *Histograms — 2: Histogram Equalization*. OpenCV 4.13.0. https://docs.opencv.org/4.13.0/d5/daf/tutorial_py_histogram_equalization.html. Acesso em: 26 out. 2026.
- OPENCV. *Getting Started with Videos*. OpenCV 4.13.0. https://docs.opencv.org/4.13.0/dd/d43/tutorial_py_video_display.html. Acesso em: 26 out. 2026.
- OPENCV. *OpenCV Zoo — YuNet e SFace*. Revisão `48b10fa505aeb51fbd127fc60a5c660040e823b7`. https://github.com/opencv/opencv_zoo. Acesso em: 26 out. 2026.

Contribuição técnica da pessoa responsável pelo processamento de imagens. A dissertação final deve incorporar os módulos, integrantes e resultados reais do grupo, com a formatação e a extensão exigidas pelo enunciado.
