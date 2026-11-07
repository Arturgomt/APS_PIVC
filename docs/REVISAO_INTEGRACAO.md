# Revisão de processamento e reconhecimento

Revisão local de 29/10/2026 em `C:\APS - PIVC\APS_PIVC`.

## Conclusão

Os dois módulos são compatíveis e o fluxo integrado funciona tecnicamente.
O processamento já havia migrado do recorte cinza 128x128 para BGR uint8 112x112,
com YuNet e alinhamento geométrico `FaceRecognizerSF.alignCrop`. A imagem é
encaminhada em memória; `resumo()`/JSON não contém pixels e não deve ser usado
como substituto da matriz na identificação.

## O que foi ajustado

- Criado `aps.py` como entrada única para cadastro com fotos e identificação por
  foto ou webcam. Ele reutiliza a integração existente, sem duplicar o pipeline.
- Seleção automática de `Reconhecimento Facial/alinhado.py`. A antiga dependência
  documental de `.local/reconhecimento-recebido/` foi removida dos comandos atuais.
- `RecognitionService` passou a receber `model_path` explicitamente; removida a
  alteração da variável global `MODEL` pelo carregador integrado.
- Modelos compartilhados em `modelos/` e banco integrado em
  `dados/cadastros_alinhados.json`. O banco é criado somente no primeiro cadastro.
- Acrescentadas opções de limiar e margem à execução integrada, com validação.
- Validação mais clara de JSON de cadastro inválido e de norma não finita.
- Testes do reconhecimento incluídos na descoberta principal `tests/`.
- Ambiente `.venv` local instalado com NumPy 2.4.2 e OpenCV 4.13.0.92,
  usando Python 3.12. Modelos baixados pela rotina com revisão fixa e SHA-256.
- Proteção no `.gitignore` para cadastros e pesos da demonstração antiga.

O script antigo `Reconhecimento Facial/app.py` continua disponível como histórico.
Para o projeto integrado, execute somente os comandos de `aps.py` no README raiz.
O frontend não foi alterado; nesta cópia foi encontrada sua documentação, não os
arquivos React/Vite de implementação.

## Verificações executadas

- Suíte unificada: 49 testes aprovados, incluindo quatro testes opcionais com
  modelos reais habilitados pela imagem pública de exemplo do OpenCV.
- Imagem original -> YuNet -> qualidade -> alinhamento -> SFace -> cadastro ->
  recarga da base -> identificação -> exclusão, em base temporária.
- Verificação de alinhamento idêntico ao OpenCV, rejeição de imagem sem rosto e
  rejeição de dois rostos.
- CLI integrada: cadastro e consulta da mesma imagem pública com ID
  `amostra_tecnica`, usando `.local/testes/cadastro_cli.json`. Similaridade 1.0
  nesse ensaio de repetição não mede precisão em imagens diferentes.
- Webcam real: leitura de três frames sem janela, encerramento normal. O último
  frame detectou um rosto e foi rejeitado por nitidez (49,307 para mínimo 60).
  O reconhecimento não foi chamado, como esperado. Não foram gravadas imagens
  da câmera nem cadastrada a pessoa capturada.
- `git diff --check` sem erros de whitespace.

Imagem pública usada apenas para ensaio técnico:
https://raw.githubusercontent.com/opencv/opencv/4.13.0/samples/data/lena.jpg

Para repetir a suíte completa nesta cópia:

```powershell
$env:APS_IMAGEM_TESTE = (Resolve-Path '.local/testes/lena.jpg').Path
$env:APS_MODULO_RECONHECIMENTO = (Resolve-Path 'Reconhecimento Facial/alinhado.py').Path
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

A imagem em `.local/` não é versionada. Sem as variáveis e a imagem, quatro testes
reais são pulados; os demais não precisam de uma pessoa ou câmera.

## O que falta para a equipe

1. Cadastrar participantes com fotos diferentes e de qualidade aprovada. Nesta
   revisão não foram criados cadastros reais na base padrão.
2. Avaliar consultas novas, pessoas desconhecidas e condições reais da webcam.
   Medir falsas aceitações, falsas rejeições e latência. Não usar a mesma foto
   de cadastro para estimar acurácia; os limiares atuais são experimentais.
3. Ajustar iluminação, distância e foco da captura. Não reduzir o limite de
   nitidez apenas para fazer o teste passar sem avaliar o impacto.
4. Para o frontend: implementar API HTTP que receba imagem e execute o pipeline
   integrado. Mapear `candidato` a uma identidade candidata, sem interpretar
   similaridade como porcentagem de certeza. Captura no navegador e captura
   local em Python são alternativas; decidir qual será usada na apresentação.
5. Implementar persistência SQL de usuários, referências e permissões se esse
   for o plano da equipe. O projeto atualmente usa JSON; não há conexão SQL.
6. Aplicar autorização no backend: usuário ativo, nível requerido e escopo da
   divisão. Reconhecimento por si só não concede acesso ao conteúdo protegido.
7. Implementar histórico de decisões e autenticação das operações administrativas.
   Prova de vida não está implementada; o protótipo não é controle de acesso real.

## Limitações operacionais

Cadastro na CLI integrada é por arquivos; a webcam faz identificação. O serviço
mantém a base em memória e precisa ser recarregado se outro processo cadastrar
alguém. Escritores simultâneos no JSON não são suportados. A busca compara todas
as amostras e deve ser medida antes de ampliar o número de usuários. Os modelos
de alinhamento e reconhecimento são carregados uma vez por instância, mas existem
duas instâncias SFace no fluxo; otimizar compartilhamento só se as medições exigirem.
