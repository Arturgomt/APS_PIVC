# Atendimento às diretrizes da APS

Fonte: enunciado fornecido na conversa “Etapas APS UNIP”, cabeçalho **Orientações para a disciplina de Atividades Práticas Supervisionadas — 2026/2**, e divisão de tarefas da pessoa 3. O nome do arquivo menciona 2024.2, mas o conteúdo identifica 2026/2.

## Sua entrega: processamento de imagens

| Solicitação | Implementação atual |
|---|---|
| Python e OpenCV | Pacote `processamento_imagens/` |
| Capturar webcam em tempo real | `aquisicao.Webcam`, comando `webcam` |
| Pré-processar e ajustar resolução | Resize proporcional e preparo geométrico SFace |
| Analisar iluminação e qualidade | Brilho médio, variância do Laplaciano e tamanho da face |
| Demonstrar operações de filtragem e contraste | Exportações didáticas de cinza, suavização e CLAHE |
| Detectar e segmentar rostos | YuNet com cinco pontos e `alignCrop` SFace |
| Preparar para o reconhecedor do colega | BGR `uint8`, `(112,112,3)`, contrato versionado |
| Tratar entradas inválidas, ausência/múltiplos rostos e falha de alinhamento | Estados explícitos; não encaminha captura rejeitada |
| Integrar sua saída | `integracao.reconhecer` e exemplo com o serviço recebido |
| Relatório de código | `scripts/relatorio_codigo.py` |

O estado da demonstração física e os ensaios reais estão em `VALIDACAO.md`. A captura antiga informada pelo integrante foi feita antes da adaptação SFace e não valida o novo alinhamento na webcam.

## As cinco fases do enunciado

| Fase | Responsável e conexão |
|---|---|
| Sensor / aquisição | Sua parte lê a webcam ou foto |
| Pré-processamento | Sua parte ajusta resolução, verifica qualidade e prepara geometricamente a imagem |
| Segmentação | Sua parte detecta a região e produz o rosto alinhado |
| Extração de características | `RecognitionService` recebido gera o embedding SFace |
| Classificação / interpretação | O reconhecedor compara as referências; o sistema completo ainda consulta permissões |

Cinza, suavização e CLAHE são preservados como demonstrações do processamento. Não são enviados ao SFace no lugar da imagem BGR: o contrato do módulo recebido exige cor e alinhamento compatível. As métricas de brilho e nitidez avaliam a amostra, sem identificar a pessoa.

## Responsabilidades do sistema completo

O módulo recebido cobre cadastro de referências e identificação 1:N, persistindo IDs e embeddings em JSON. O exemplo desta entrega verifica sua comunicação com o processamento. A identidade candidata ainda deve ser ligada ao cadastro de usuários e às regras do grupo:

- Nível 1: permissão geral.
- Nível 2: diretores de divisões específicas, com verificação da divisão.
- Nível 3: acesso exclusivo ao ministro do Meio Ambiente.

Banco SQL, regras de autorização, histórico de tentativas e a aplicação completa não foram implementados nesta entrega individual. O JSON do reconhecedor não substitui automaticamente esses componentes.

## Trabalho escrito e entregas

O enunciado exige A4, Arial 12, espaçamento 1,5 e margens esquerda e direita de 2,5 cm; na versão física, espiral com capa transparente. O texto Markdown é contribuição para compor a dissertação e não comprova formatação ou extensão do documento final.

| Seção | Páginas |
|---|---|
| Objetivo | 1 a 2 |
| Introdução | 2 a 8 |
| Fundamentos das técnicas de reconhecimento facial | 10 a 20 |
| Plano de desenvolvimento | 5 a 15 |
| Projeto / estrutura do programa | 18 a 35 |

Elementos pré e pós-textuais não entram na contagem. Incluir capa com curso, tema, nomes e RAs, índice, objetivo e motivação, introdução, fundamentos, plano, estrutura e módulos, relatório de código, bibliografia e ficha padrão de APS com atividades reais em ordem cronológica.

O documento informa grupos de 3 a 5 integrantes, avaliação de 30% apresentação e 70% trabalho escrito, sujeita ao orientador; acompanhamento parcial e relatório de código no Teams; demonstração do programa e entrega final obrigatória no site da UNIP. GitHub não substitui essas entregas.

Datas informadas: formação de grupos de 10/08/2026 a **12/11/2026**; postagem de arquivos de 13/10/2026 a **12/11/2026**. Confirmar com o orientador eventuais atualizações posteriores ao enunciado fornecido.
