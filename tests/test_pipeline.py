import unittest

import cv2
import numpy as np

from processamento_imagens import CONTRATO_SFACE, Configuracao, ProcessadorFacial, Status
from processamento_imagens.alinhamento import PreparadorSFace


def imagem_nitida():
    y, x = np.indices((240, 320))
    cinza = np.where(((x // 8 + y // 8) % 2) == 0, 75, 175).astype(np.uint8)
    return np.stack([cinza + 15, cinza, cinza - 15], axis=2)


def deteccao(caixa=(80, 50, 100, 120)):
    x, y, w, h = caixa
    pontos = [(x + w * .3, y + h * .35), (x + w * .7, y + h * .35),
              (x + w * .5, y + h * .55), (x + w * .35, y + h * .75),
              (x + w * .65, y + h * .75)]
    return np.array([*caixa, *(v for p in pontos for v in p), .99], dtype=np.float32)


class PreparadorFixo:
    """Controla detecção e saída para isolar qualidade e contrato nos testes."""

    def __init__(self, linhas=None):
        self.linhas = [deteccao()] if linhas is None else linhas
        self.ultima_bgr = None
        self.ultima_linha = None
        self.alinhada = np.full((112, 112, 3), (17, 101, 229), dtype=np.uint8)

    def detectar(self, bgr):
        self.ultima_bgr = bgr.copy()
        return self.linhas

    def alinhar(self, bgr, linha):
        self.ultima_linha = linha.copy()
        np.testing.assert_array_equal(bgr, self.ultima_bgr)
        return self.alinhada.copy()


class PipelineTests(unittest.TestCase):
    def processador(self, linhas=None, config=None):
        return ProcessadorFacial(config, preparador=PreparadorFixo(linhas))

    def test_entradas_invalidas_incluem_cinza_e_float(self):
        for imagem in [None, [], "foto", np.zeros((0, 10, 3), np.uint8),
                       np.zeros((10, 10, 3), np.float32), np.zeros((10, 10), np.uint8),
                       np.zeros((10, 10, 1), np.uint8), np.zeros((1, 1, 1, 1), np.uint8)]:
            with self.subTest(tipo=type(imagem)):
                r = self.processador().processar(imagem)
                self.assertEqual(r.status, Status.IMAGEM_INVALIDA)
                self.assertIsNone(r.entrada_reconhecimento)

    def test_contrato_sface_e_cores_preservadas(self):
        preparador = PreparadorFixo()
        r = ProcessadorFacial(preparador=preparador).processar(imagem_nitida())
        self.assertEqual(r.status, Status.OK)
        self.assertEqual(r.entrada_reconhecimento.shape, (112, 112, 3))
        self.assertEqual(r.entrada_reconhecimento.dtype, np.uint8)
        self.assertTrue(r.entrada_reconhecimento.flags.c_contiguous)
        np.testing.assert_array_equal(r.entrada_reconhecimento[0, 0], [17, 101, 229])
        np.testing.assert_array_equal(preparador.ultima_bgr, imagem_nitida())
        self.assertEqual(r.resumo()["contrato_reconhecimento"], CONTRATO_SFACE)

    def test_entrada_e_saida_nao_compartilham_pixels_mutaveis(self):
        imagem = imagem_nitida()
        copia = imagem.copy()
        r = self.processador().processar(imagem)
        r.entrada_reconhecimento[:] = 0
        np.testing.assert_array_equal(imagem, copia)
        self.assertGreater(int(r.entrada_reconhecimento.max()), 0)

    def test_sem_rosto_e_multiplos_nao_encaminham_amostra(self):
        for linhas, status in [([], Status.SEM_ROSTO),
                               ([deteccao((10, 10, 80, 90)), deteccao((150, 40, 80, 90))], Status.MULTIPLOS_ROSTOS)]:
            with self.subTest(status=status):
                r = self.processador(linhas).processar(imagem_nitida())
                self.assertEqual(r.status, status)
                self.assertIsNone(r.entrada_reconhecimento)

    def test_rejeita_escuro_claro_e_desfocado(self):
        for valor, problema in [(0, "iluminação baixa"), (255, "iluminação excessiva"), (120, "nitidez baixa")]:
            with self.subTest(valor=valor):
                r = self.processador().processar(np.full((240, 320, 3), valor, np.uint8))
                self.assertEqual(r.status, Status.QUALIDADE_INSUFICIENTE)
                self.assertIn(problema, r.rostos[0].qualidade.problemas)
                self.assertIsNone(r.entrada_reconhecimento)

    def test_redimensionamento_e_coordenadas_dos_cinco_pontos(self):
        linha = deteccao((30, 20, 100, 100))
        imagem = np.tile(imagem_nitida(), (4, 4, 1))
        r = self.processador([linha], Configuracao(largura_maxima=320)).processar(imagem)
        self.assertEqual(r.processada_hw, (240, 320))
        self.assertEqual(r.rostos[0].caixa_original, (120, 80, 400, 400))
        np.testing.assert_allclose(r.rostos[0].pontos_original, linha[4:14].reshape(5, 2) * 4)

    def test_bgra_aceito_sem_modificar_cor(self):
        imagem = imagem_nitida()
        preparador = PreparadorFixo()
        r = ProcessadorFacial(preparador=preparador).processar(cv2.cvtColor(imagem, cv2.COLOR_BGR2BGRA))
        self.assertEqual(r.status, Status.OK)
        np.testing.assert_array_equal(preparador.ultima_bgr, imagem)

    def test_etapas_sao_opcionais_e_nao_modificam_alinhamento(self):
        p = self.processador()
        sem = p.processar(imagem_nitida())
        com = p.processar(imagem_nitida(), incluir_etapas=True)
        self.assertFalse(sem.etapas)
        self.assertEqual(len(com.etapas), 5)
        np.testing.assert_array_equal(sem.entrada_reconhecimento, com.entrada_reconhecimento)

    def test_rosto_pequeno_e_rejeitado_por_qualidade(self):
        r = self.processador([deteccao((20, 20, 40, 40))]).processar(imagem_nitida())
        self.assertEqual(r.status, Status.QUALIDADE_INSUFICIENTE)
        self.assertIsNone(r.entrada_reconhecimento)

    def test_imagem_muito_pequena_nao_e_enviada_ao_detector(self):
        preparador = PreparadorFixo()
        r = ProcessadorFacial(preparador=preparador).processar(np.zeros((1, 1, 3), np.uint8))
        self.assertEqual(r.status, Status.SEM_ROSTO)
        self.assertIsNone(preparador.ultima_bgr)

    def test_pontos_invalidos_e_degenerados_nao_sao_aceitos(self):
        ruim = deteccao()
        ruim[4:14] = 10
        nao_finita = deteccao()
        nao_finita[6] = np.nan
        fora = deteccao()
        fora[4] = 900
        for linha in [ruim, nao_finita, fora, np.zeros(14), deteccao((400, 400, 20, 20))]:
            with self.subTest(linha=linha):
                r = self.processador([linha]).processar(imagem_nitida())
                self.assertEqual(r.status, Status.ALINHAMENTO_INVALIDO)
                self.assertIsNone(r.entrada_reconhecimento)

    def test_deteccao_invalida_adicional_bloqueia_amostra(self):
        r = self.processador([deteccao(), np.zeros(14)]).processar(imagem_nitida())
        self.assertEqual(r.status, Status.ALINHAMENTO_INVALIDO)
        self.assertIsNone(r.entrada_reconhecimento)

    def test_alinhador_com_saida_errada_nao_e_aceito(self):
        for formato, tipo in [((128, 128), np.uint8), ((112, 112, 3), np.float32)]:
            with self.subTest(formato=formato, tipo=tipo):
                preparador = PreparadorFixo()
                preparador.alinhada = np.zeros(formato, tipo)
                r = ProcessadorFacial(preparador=preparador).processar(imagem_nitida())
                self.assertEqual(r.status, Status.ALINHAMENTO_INVALIDO)
                self.assertIsNone(r.entrada_reconhecimento)

    def test_configuracao_invalida(self):
        for kwargs in [{"largura_maxima": 0}, {"largura_maxima": 2.5}, {"brilho_minimo": 250},
                       {"nitidez_minima": -1}, {"clip_limit": float("nan")}, {"limiar_nms": 0},
                       {"confianca_deteccao": 1.1}, {"confianca_deteccao": "0.9"}]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                Configuracao(**kwargs)

    def test_modelos_ausentes_geram_orientacao(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as pasta, self.assertRaisesRegex(ValueError, "preparar-modelos"):
            PreparadorSFace(Configuracao(), pasta)


if __name__ == "__main__":
    unittest.main()
