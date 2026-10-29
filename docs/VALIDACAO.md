# Validação da versão 0.2 — SFace

Verificação realizada em **26/10/2026**, Windows, Python 3.13.12, OpenCV Python 4.13.0.92 e NumPy 2.4.2.

## Resultado atual

**39 testes aprovados**, com os quatro ensaios reais opcionais habilitados. A suíte cobre contratos, qualidade, bloqueios, aquisição simulada, exportação, modelos e integração. O módulo recebido do colega permanece inalterado.

| Verificação | Resultado |
|---|---|
| Download explícito de YuNet e SFace | Concluído; SHA-256 confere com a revisão oficial |
| Detector e alinhador reais | Executados na imagem de exemplo do OpenCV |
| Contrato de saída | BGR `uint8`, `(112,112,3)`, contíguo |
| Alinhamento do pipeline versus `alignCrop` direto | Pixels idênticos no ensaio |
| Preservação de cor | Canais distintos mantidos no recorte de teste |
| Imagem sem rosto | `sem_rosto`; nenhuma entrada ao reconhecedor |
| Duas cópias da face lado a lado | `multiplos_rostos`; nenhuma entrada ao reconhecedor |
| Cadastro e consulta no serviço recebido | Cadastro salvo, recarregado, identificado como candidato e excluído |
| Controle de acesso | Fora do escopo da entrega individual; candidato não recebe autorização |

A imagem usada foi [lena.jpg do OpenCV 4.13.0](https://github.com/opencv/opencv/blob/4.13.0/samples/data/lena.jpg), preservada em `.local/amostras/` e fora do Git. Não são usadas fotos pessoais do grupo na suíte. O cadastro do ensaio real ocorre em diretório temporário.

Na passagem real pelo pipeline, houve um rosto com confiança de detecção 0,908979, brilho médio 126,353 e variância do Laplaciano 541,737. São observações da imagem de exemplo, sem significado de identidade ou acurácia biométrica.

O ensaio de integração cadastra e consulta a mesma imagem para verificar formato, chamada, persistência e recarga. **Não mede acurácia de reconhecimento.** Avaliar pessoas conhecidas e desconhecidas em capturas separadas continua necessário.

## Reproduzir

Suíte padrão, sem downloads e sem dependência do arquivo do colega:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Os quatro testes reais são ignorados quando modelos e entradas não são indicados. Para habilitá-los nesta cópia local:

```powershell
$env:APS_IMAGEM_TESTE = (Resolve-Path .local/amostras/opencv_lena.jpg).Path
$env:APS_MODULO_RECONHECIMENTO = (Resolve-Path .local/reconhecimento-recebido/alinhado.py).Path
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Em outra máquina, use uma imagem de teste com exatamente um rosto colorido e de qualidade suficiente, prepare os modelos e informe o caminho do módulo recebido. Os ensaios reais são verificações técnicas, não um conjunto representativo de avaliação.

O workflow do GitHub executa a suíte padrão em Ubuntu e Windows, Python 3.11 e 3.13. Sem os dados locais, os testes reais opcionais aparecem como ignorados. CI no GitHub só terá resultado após publicar a branch.

## Captura anterior compartilhada pelo integrante

Antes da adaptação SFace, o integrante compartilhou uma captura aprovada pelo pipeline Haar da versão 0.1: resolução 1280×720, processamento 960×540, um rosto, brilho 106,915, nitidez 94,955 e tempo de 11,365 ms. A saída era cinza 128×128. Esse registro foi preservado como histórico e **não valida o contrato ou a webcam da versão 0.2**.

## Roteiro da demonstração física

1. Abrir `python -m processamento_imagens webcam --camera 0` com o Python da `.venv` e verificar caixas e cinco pontos faciais.
2. Enquadrar uma pessoa com iluminação uniforme; observar a mensagem de amostra alinhada.
3. Sair do enquadramento e depois enquadrar duas pessoas; verificar que as amostras são bloqueadas.
4. Alterar distância, iluminação ou nitidez. Verificar rejeição por qualidade ou ausência de detecção.
5. Executar com `--saida saidas --salvar-imagens`, pressionar S e conferir etapas e PNG BGR 112×112 sem anotações.
6. Cadastrar fotos reais pelo exemplo documentado em `INTEGRACAO.md`; identificar com capturas diferentes e testar desconhecidos.
7. Executar o exemplo com `--webcam`; verificar ID candidato e respostas inconclusivas/desconhecidas sem autorização automática.
8. Conferir Q/Esc e fechamento da janela, que devem liberar a câmera.
9. Gerar `saidas/relatorio_codigo.txt` para o Teams e registrar as atividades reais na ficha de APS.

A webcam física não foi aberta durante estes ajustes. A demonstração da versão atual no computador da apresentação continua pendente.
