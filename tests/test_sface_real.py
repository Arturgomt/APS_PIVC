"""Ensaios opcionais reais; requerem pesos locais e uma imagem explicitamente indicada."""

from pathlib import Path
import os
import tempfile
import unittest

import cv2
import numpy as np

from exemplos.integrar_reconhecimento import carregar_servico
from processamento_imagens import ProcessadorFacial, Status, reconhecer
from processamento_imagens.alinhamento import PreparadorSFace
from processamento_imagens.aquisicao import ler_imagem
from processamento_imagens.configuracao import Configuracao
from processamento_imagens.modelos import caminhos_modelos

IMAGEM = os.environ.get("APS_IMAGEM_TESTE")
MODULO = os.environ.get("APS_MODULO_RECONHECIMENTO")
DISPONIVEL = bool(IMAGEM and Path(IMAGEM).is_file() and all(p.is_file() for p in caminhos_modelos().values()))


@unittest.skipUnless(DISPONIVEL, "Informe APS_IMAGEM_TESTE e prepare os modelos para os testes reais opcionais.")
class SFaceRealTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.imagem = ler_imagem(IMAGEM)
        cls.processador = ProcessadorFacial()

    def test_rosto_real_e_alinhamento_identico_ao_opencv(self):
        resultado = self.processador.processar(self.imagem)
        self.assertEqual(resultado.status, Status.OK)
        preparador = PreparadorSFace(Configuracao())
        altura, largura = self.imagem.shape[:2]
        imagem = self.imagem
        if largura > 960:
            imagem = cv2.resize(imagem, (960, max(1, round(altura * 960 / largura))), interpolation=cv2.INTER_AREA)
        deteccoes = preparador.detectar(imagem)
        self.assertEqual(len(deteccoes), 1)
        esperado = preparador.alinhar(imagem, deteccoes[0])
        np.testing.assert_array_equal(resultado.entrada_reconhecimento, esperado)
        self.assertFalse(np.array_equal(esperado[:, :, 0], esperado[:, :, 2]))

    def test_imagem_sem_rosto_nao_tem_amostra(self):
        resultado = self.processador.processar(np.zeros((480, 640, 3), np.uint8))
        self.assertEqual(resultado.status, Status.SEM_ROSTO)
        self.assertIsNone(resultado.entrada_reconhecimento)

    def test_dois_rostos_nao_tem_amostra(self):
        resultado = self.processador.processar(np.hstack([self.imagem, self.imagem]))
        self.assertEqual(resultado.status, Status.MULTIPLOS_ROSTOS)
        self.assertEqual(len(resultado.rostos), 2)
        self.assertIsNone(resultado.entrada_reconhecimento)

    @unittest.skipUnless(MODULO and Path(MODULO).is_file(), "Informe APS_MODULO_RECONHECIMENTO para testar o serviço do colega.")
    def test_cadastro_consulta_e_recarga_no_servico_recebido(self):
        resultado = self.processador.processar(self.imagem)
        self.assertIsNotNone(resultado.entrada_reconhecimento)
        with tempfile.TemporaryDirectory() as pasta:
            banco = Path(pasta) / "pessoas.json"
            servico = carregar_servico(MODULO, banco)
            self.assertEqual(reconhecer(resultado, servico)["reconhecimento"]["status"], "sem_cadastros")
            servico.register("amostra_tecnica", [resultado.entrada_reconhecimento])
            restaurado = carregar_servico(MODULO, banco)
            resposta = reconhecer(resultado, restaurado)["reconhecimento"]
            self.assertEqual(resposta["status"], "candidato")
            self.assertEqual(resposta["person_id"], "amostra_tecnica")
            self.assertGreater(resposta["similarity"], .99)
            restaurado.delete("amostra_tecnica")
            self.assertEqual(carregar_servico(MODULO, banco).people, {})
