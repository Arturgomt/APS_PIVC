"""Identificacao 1:N de rostos previamente alinhados ao padrao SFace."""
import argparse
import json
from pathlib import Path
from urllib.request import urlopen

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent
MODEL = ROOT / 'models' / 'face_recognition_sface_2021dec.onnx'
VERSION = 'sface-2021dec-aligned-112-bgr-v1'


def download_model():
    MODEL.parent.mkdir(exist_ok=True)
    if MODEL.exists():
        return
    url = 'https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx'
    temporary = MODEL.with_suffix('.part')
    try:
        with urlopen(url, timeout=120) as source, temporary.open('wb') as target:
            while block := source.read(1024 * 1024):
                target.write(block)
        temporary.replace(MODEL)
    finally:
        temporary.unlink(missing_ok=True)


def normalize(value):
    vector = np.asarray(value, dtype=np.float32).reshape(-1)
    norm = np.linalg.norm(vector)
    if vector.size != 128 or not np.isfinite(vector).all() or norm < 1e-8:
        raise ValueError('Embedding SFace invalido: esperados 128 valores finitos e norma positiva.')
    return vector / norm


def decide(embedding, people, threshold, margin):
    """Busca exata. Score por pessoa = maior cosseno entre suas amostras."""
    if not -1 <= threshold <= 1 or not 0 <= margin <= 2:
        raise ValueError('Limiar deve estar em [-1,1] e margem em [0,2].')
    query = normalize(embedding)
    if not people:
        return {'status': 'sem_cadastros', 'person_id': None, 'similarity': None}
    scores = sorted(((max(float(query @ normalize(v)) for v in samples), person_id)
                     for person_id, samples in people.items()), reverse=True)
    best_score, best_id = scores[0]
    status = 'candidato'
    if best_score < threshold:
        status = 'desconhecido'
    elif len(scores) > 1 and best_score - scores[1][0] < margin:
        status = 'inconclusivo'
    return {'status': status, 'person_id': best_id if status == 'candidato' else None,
            'similarity': round(best_score, 6)}


class RecognitionService:
    def __init__(self, database=ROOT / 'cadastros_alinhados.json', threshold=0.5, margin=0.05):
        if not MODEL.exists():
            raise ValueError('Baixe o modelo: python alinhado.py baixar-modelo')
        if not -1 <= threshold <= 1 or not 0 <= margin <= 2:
            raise ValueError('Limiar ou margem fora do intervalo permitido.')
        self.model = cv2.FaceRecognizerSF.create(str(MODEL), '')
        self.database = Path(database)
        self.threshold, self.margin = threshold, margin
        self.people = {}
        if self.database.exists():
            data = json.loads(self.database.read_text(encoding='utf-8'))
            if data.get('version') != VERSION:
                raise ValueError('Base incompativel com modelo/preparacao atual.')
            self.people = data['people']
            for person_id, samples in self.people.items():
                if not isinstance(person_id, str) or not person_id.strip() or not samples:
                    raise ValueError('Cadastro invalido.')
                for sample in samples:
                    normalize(sample)

    def embedding(self, aligned_bgr):
        # Sem deteccao, recorte, alinhamento ou redimensionamento aqui.
        if not isinstance(aligned_bgr, np.ndarray) or aligned_bgr.shape != (112, 112, 3) or aligned_bgr.dtype != np.uint8:
            raise ValueError('Entrada deve ser numpy uint8 BGR com shape (112,112,3), alinhada ao SFace.')
        return normalize(self.model.feature(np.ascontiguousarray(aligned_bgr)))

    def register(self, person_id, aligned_images):
        if not isinstance(person_id, str) or not person_id.strip():
            raise ValueError('Identificador obrigatorio.')
        samples = [self.embedding(img).tolist() for img in aligned_images]
        if not samples:
            raise ValueError('Forneca pelo menos uma imagem.')
        if person_id in self.people:
            raise ValueError('Identificador ja cadastrado; exclua explicitamente antes de cadastrar novamente.')
        updated = dict(self.people)
        updated[person_id] = samples
        self._save(updated)

    def identify(self, aligned_bgr):
        return decide(self.embedding(aligned_bgr), self.people, self.threshold, self.margin)

    def delete(self, person_id):
        updated = dict(self.people)
        updated.pop(person_id, None)
        self._save(updated)

    def _save(self, people):
        self.database.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.database.with_suffix('.tmp')
        temporary.write_text(json.dumps({'version': VERSION, 'people': people}, ensure_ascii=False), encoding='utf-8')
        temporary.replace(self.database)
        self.people = people


def read_image(path):
    # imdecode permite caminhos Unicode no Windows. IMREAD_COLOR entrega BGR uint8.
    image = cv2.imdecode(np.frombuffer(Path(path).read_bytes(), dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f'Imagem invalida: {path}')
    return image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limiar', type=float, default=0.5)
    parser.add_argument('--margem', type=float, default=0.05)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('baixar-modelo')
    register = commands.add_parser('cadastrar')
    register.add_argument('--id', required=True)
    register.add_argument('imagens', nargs='+')
    identify = commands.add_parser('identificar')
    identify.add_argument('imagem')
    delete = commands.add_parser('excluir')
    delete.add_argument('--id', required=True)
    args = parser.parse_args()
    if args.command == 'baixar-modelo':
        download_model()
        print('Modelo disponivel.')
        return
    service = RecognitionService(threshold=args.limiar, margin=args.margem)
    if args.command == 'cadastrar':
        service.register(args.id, [read_image(path) for path in args.imagens])
        print(json.dumps({'status': 'cadastrado', 'person_id': args.id}))
    elif args.command == 'identificar':
        print(json.dumps(service.identify(read_image(args.imagem)), ensure_ascii=False))
    else:
        service.delete(args.id)
        print(json.dumps({'status': 'excluido', 'person_id': args.id}))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, cv2.error) as error:
        raise SystemExit(f'Erro: {error}')
