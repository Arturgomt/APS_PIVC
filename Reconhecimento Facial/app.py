"""Demonstracao local de identificacao 1:N. Nao usar para liberar acesso."""
import argparse
import json
from pathlib import Path
from urllib.request import urlopen

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent
DB = ROOT / 'cadastros.json'
MODELS = {
    'detector': ('face_detection_yunet', 'face_detection_yunet_2023mar.onnx'),
    'recognizer': ('face_recognition_sface', 'face_recognition_sface_2021dec.onnx'),
}
MODEL_VERSION = 'sface-2021dec-yunet-2023mar'


def download_models():
    folder = ROOT / 'models'
    folder.mkdir(exist_ok=True)
    for directory, filename in MODELS.values():
        path = folder / filename
        if path.exists():
            continue
        url = f'https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/{directory}/{filename}'
        print(f'Baixando {filename}...')
        temporary = path.with_suffix('.part')
        try:
            with urlopen(url, timeout=120) as source, temporary.open('wb') as target:
                while block := source.read(1024 * 1024):
                    target.write(block)
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)


def load_database():
    if not DB.exists():
        return {}
    data = json.loads(DB.read_text(encoding='utf-8'))
    if data.get('model') != MODEL_VERSION:
        raise ValueError('Cadastro usa outra versao de modelo. Refaça o cadastro.')
    return data['people']


def save_database(people):
    temporary = DB.with_suffix('.tmp')
    temporary.write_text(json.dumps({'model': MODEL_VERSION, 'people': people}, ensure_ascii=False), encoding='utf-8')
    temporary.replace(DB)


def normalize(vector):
    vector = np.asarray(vector, dtype=np.float32).reshape(-1)
    norm = np.linalg.norm(vector)
    if not np.isfinite(vector).all() or norm < 1e-8:
        raise ValueError('Embedding invalido.')
    return vector / norm


class FacePipeline:
    def __init__(self):
        paths = {key: str(ROOT / 'models' / value[1]) for key, value in MODELS.items()}
        if not all(Path(path).exists() for path in paths.values()):
            raise ValueError('Execute primeiro: python app.py baixar-modelos')
        self.detector = cv2.FaceDetectorYN.create(paths['detector'], '', (640, 480), 0.9)
        self.recognizer = cv2.FaceRecognizerSF.create(paths['recognizer'], '')

    def prepare_faces(self, frame):
        """Etapa substituivel pelo colega: detectar e alinhar, sem identificar."""
        self.detector.setInputSize((frame.shape[1], frame.shape[0]))
        _, faces = self.detector.detect(frame)
        if faces is None:
            return []
        return [(face, self.recognizer.alignCrop(frame, face)) for face in faces]

    def embed(self, aligned_bgr):
        """Entrada: rosto BGR uint8 alinhado pelo contrato do SFace (112x112)."""
        return normalize(self.recognizer.feature(aligned_bgr))


def identify(vector, people, threshold, margin):
    if not people:
        return 'Sem cadastros', None
    # Uma pontuacao por pessoa, usando a melhor das suas amostras.
    ranking = sorted(((max(float(vector @ normalize(sample)) for sample in samples), name)
                      for name, samples in people.items()), reverse=True)
    score, name = ranking[0]
    if score < threshold:
        return 'Desconhecido', score
    if len(ranking) > 1 and score - ranking[1][0] < margin:
        return 'Inconclusivo', score
    return name, score


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['baixar-modelos', 'cadastrar', 'identificar', 'excluir'])
    parser.add_argument('--nome')
    parser.add_argument('--camera', type=int, default=0)
    parser.add_argument('--limiar', type=float, default=0.5, help='Experimental: calibrar com dados reais.')
    parser.add_argument('--margem', type=float, default=0.05, help='Diferenca minima entre primeiro e segundo candidatos.')
    args = parser.parse_args()
    if args.action == 'baixar-modelos':
        download_models()
        return
    if args.action in ('cadastrar', 'excluir') and not (args.nome and args.nome.strip()):
        parser.error('--nome e obrigatorio')
    if not -1 <= args.limiar <= 1 or args.margem < 0:
        parser.error('Limiar deve estar entre -1 e 1; margem deve ser nao negativa.')
    people = load_database()
    if args.action == 'excluir':
        people.pop(args.nome, None)
        save_database(people)
        print('Exclusao concluida.')
        return
    if args.action == 'identificar' and not people:
        raise ValueError('Cadastre pelo menos uma pessoa antes de identificar.')
    pipeline = FacePipeline()
    capture = cv2.VideoCapture(args.camera)
    samples = []
    try:
        if not capture.isOpened():
            raise RuntimeError('Nao foi possivel abrir a camera. Verifique permissoes ou --camera 1.')
        print('Q/Esc: sair. No cadastro, ESPACO captura uma amostra; cinco amostras salvam o cadastro.')
        if args.action == 'cadastrar' and args.nome in people:
            print('As cinco novas amostras substituirao o cadastro existente deste nome.')
        while True:
            ok, frame = capture.read()
            if not ok:
                raise RuntimeError('Falha ao receber imagem da camera.')
            prepared = pipeline.prepare_faces(frame)
            display = frame.copy()
            for face, aligned in prepared:
                label = f'Cadastro {len(samples)}/5'
                if args.action == 'identificar':
                    label, score = identify(pipeline.embed(aligned), people, args.limiar, args.margem)
                    if score is not None:
                        label += f' | similaridade {score:.3f}'
                x, y, w, h = face[:4].astype(int)
                cv2.rectangle(display, (x, y), (x+w, y+h), (0, 200, 255), 2)
                cv2.putText(display, label, (max(x, 0), max(y-8, 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)
            cv2.imshow('Reconhecimento facial - prototipo', display)
            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord('q')):
                break
            if key == 32 and args.action == 'cadastrar':
                if len(prepared) != 1:
                    print('Para cadastrar, mantenha exatamente um rosto na imagem.')
                    continue
                samples.append(pipeline.embed(prepared[0][1]).tolist())
                print(f'Amostra {len(samples)}/5 capturada. Varie levemente a posicao.')
                if len(samples) == 5:
                    people[args.nome] = samples
                    save_database(people)
                    print(f'Cadastro salvo: {args.nome}')
                    break
    finally:
        capture.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    try:
        main()
    except (ValueError, RuntimeError, OSError, cv2.error) as error:
        raise SystemExit(f'Erro: {error}')
