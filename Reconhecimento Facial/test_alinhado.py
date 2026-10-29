"""Testes de decisao e persistencia; nao medem acuracia biometrica."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from alinhado import RecognitionService, decide, normalize


class RecognitionTests(unittest.TestCase):
    def setUp(self):
        self.a = np.eye(128, dtype=np.float32)[0]
        self.b = np.eye(128, dtype=np.float32)[1]
        self.people = {'001': [self.a.tolist()], '002': [self.b.tolist()]}

    def test_candidate(self):
        self.assertEqual(decide(self.a, self.people, 0.5, 0.05)['person_id'], '001')

    def test_unknown_has_no_identity(self):
        result = decide(-self.a, self.people, 0.5, 0.05)
        self.assertEqual(result['status'], 'desconhecido')
        self.assertIsNone(result['person_id'])

    def test_close_candidates_are_inconclusive(self):
        query = normalize(self.a + self.b)
        result = decide(query, self.people, 0.5, 0.05)
        self.assertEqual(result['status'], 'inconclusivo')
        self.assertIsNone(result['person_id'])

    def test_empty_database(self):
        self.assertEqual(decide(self.a, {}, 0.5, 0.05)['status'], 'sem_cadastros')

    def test_multiple_samples_do_not_compete_with_same_person(self):
        self.people['001'].append(self.a.tolist())
        self.assertEqual(decide(self.a, self.people, 0.5, 0.05)['person_id'], '001')

    def test_invalid_embeddings(self):
        for value in [np.zeros(128), np.ones(127), np.full(128, np.nan)]:
            with self.assertRaises(ValueError):
                normalize(value)

    def test_persistence_duplicate_and_deletion(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'people.json'
            with patch('alinhado.MODEL') as model_path, patch('alinhado.cv2.FaceRecognizerSF.create') as create:
                model_path.exists.return_value = True
                create.return_value.feature.return_value = self.a.reshape(1, -1)
                service = RecognitionService(path)
                image = np.zeros((112, 112, 3), dtype=np.uint8)
                service.register('001', [image])
                restored = RecognitionService(path)
                self.assertEqual(restored.identify(image)['person_id'], '001')
                with self.assertRaises(ValueError):
                    restored.register('001', [image])
                restored.delete('001')
                self.assertEqual(RecognitionService(path).people, {})

    def test_rejects_wrong_image_contract(self):
        service = RecognitionService.__new__(RecognitionService)
        for image in [np.zeros((224, 224, 3), np.uint8), np.zeros((112, 112, 3), np.float32), None]:
            with self.assertRaises(ValueError):
                service.embedding(image)


if __name__ == '__main__':
    unittest.main()
