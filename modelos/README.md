# Modelos locais

Execute `python -m processamento_imagens preparar-modelos` pelo Python do ambiente virtual, a partir da raiz do projeto. O comando baixa os dois pesos abaixo, verifica seus hashes e não baixa novamente um arquivo válido. Os pesos ONNX ficam fora do Git; este README é versionado.

Origem: OpenCV Zoo, revisão fixada `48b10fa505aeb51fbd127fc60a5c660040e823b7`.

| Modelo | Uso | SHA-256 |
|---|---|---|
| `face_detection_yunet_2023mar.onnx` | Detecção e cinco pontos faciais | `8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4` |
| `face_recognition_sface_2021dec.onnx` | `alignCrop`, igual ao reconhecedor do colega | `0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79` |

Os hashes correspondem aos ponteiros Git LFS oficiais dessa revisão. O SFace é carregado aqui para usar seu alinhamento; a extração de características continua no serviço de reconhecimento do colega. O parâmetro `--modelos` permite utilizar outra pasta contendo estes dois arquivos.

Fontes e licenças:

- [YuNet na revisão utilizada](https://github.com/opencv/opencv_zoo/tree/48b10fa505aeb51fbd127fc60a5c660040e823b7/models/face_detection_yunet)
- [SFace na revisão utilizada](https://github.com/opencv/opencv_zoo/tree/48b10fa505aeb51fbd127fc60a5c660040e823b7/models/face_recognition_sface)
