import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import numpy as np

from processamento_imagens.aquisicao import ErroAquisicao, Webcam, ler_imagem
from processamento_imagens.cli import main
from processamento_imagens.pipeline import ProcessadorFacial
from processamento_imagens.saida import exportar, salvar_png
from tests.test_pipeline import PreparadorFixo, imagem_nitida


class AquisicaoTests(unittest.TestCase):
    def test_arquivo_inexistente(self):
        with self.assertRaisesRegex(ErroAquisicao, "não encontrado"):
            ler_imagem("nao_existe.png")

    def test_arquivo_corrompido_e_vazio(self):
        with tempfile.TemporaryDirectory() as pasta:
            for conteudo in [b"", b"nao sou imagem"]:
                arquivo = Path(pasta) / "invalida.png"
                arquivo.write_bytes(conteudo)
                with self.assertRaises(ErroAquisicao):
                    ler_imagem(arquivo)

    def test_caminho_com_acentos(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "aquisição_ação.png"
            salvar_png(arquivo, imagem_nitida())
            np.testing.assert_array_equal(ler_imagem(arquivo), imagem_nitida())

    @patch("processamento_imagens.aquisicao.cv2.VideoCapture")
    def test_camera_indisponivel_libera_recurso(self, fabrica):
        fabrica.return_value.isOpened.return_value = False
        with self.assertRaises(ErroAquisicao), Webcam():
            self.fail("Não deveria abrir.")
        fabrica.return_value.release.assert_called_once()

    @patch("processamento_imagens.aquisicao.cv2.VideoCapture")
    def test_falha_de_leitura_libera_recurso(self, fabrica):
        fabrica.return_value.read.return_value = (False, None)
        with self.assertRaises(ErroAquisicao), Webcam() as camera:
            camera.ler()
        fabrica.return_value.release.assert_called_once()

    @patch("processamento_imagens.aquisicao.cv2.VideoCapture")
    def test_camera_le_e_fecha(self, fabrica):
        frame = imagem_nitida()
        fabrica.return_value.read.return_value = (True, frame)
        with Webcam() as camera:
            self.assertIs(camera.ler(), frame)
        fabrica.return_value.release.assert_called_once()
        with self.assertRaises(ErroAquisicao):
            camera.ler()


class SaidaCliTests(unittest.TestCase):
    def setUp(self):
        self.processador = ProcessadorFacial(preparador=PreparadorFixo())
        self.resultado = self.processador.processar(imagem_nitida(), incluir_etapas=True)

    def test_exportacao_padrao_somente_metadados(self):
        with tempfile.TemporaryDirectory() as pasta:
            destino = exportar(self.resultado, pasta)
            self.assertEqual([p.name for p in destino.iterdir()], ["resultado.json"])
            dados = json.loads((destino / "resultado.json").read_text(encoding="utf-8"))
            self.assertTrue(dados["pronto_para_reconhecimento"])
            self.assertFalse(dados["imagens_salvas"])

    def test_png_alinhado_preserva_pixels_e_cor(self):
        with tempfile.TemporaryDirectory() as pasta:
            destino = exportar(self.resultado, pasta, salvar_imagens=True)
            self.assertEqual(len(list(destino.glob("*.png"))), 6)
            np.testing.assert_array_equal(
                ler_imagem(destino / "rosto_01_alinhado_bgr.png"), self.resultado.entrada_reconhecimento,
            )

    def test_exportacoes_nao_sobrescrevem(self):
        with tempfile.TemporaryDirectory() as pasta:
            self.assertNotEqual(exportar(self.resultado, pasta), exportar(self.resultado, pasta))

    @patch("processamento_imagens.cli.ProcessadorFacial")
    def test_cli_imagem_sem_rosto_e_relatorio(self, fabrica):
        fabrica.return_value = ProcessadorFacial(preparador=PreparadorFixo([]))
        with tempfile.TemporaryDirectory() as pasta, contextlib.redirect_stdout(io.StringIO()) as texto:
            arquivo = Path(pasta) / "sem_rosto.png"
            salvar_png(arquivo, np.zeros((240, 320, 3), np.uint8))
            codigo = main(["imagem", "--entrada", str(arquivo), "--saida", str(Path(pasta) / "saida")])
            self.assertEqual(codigo, 2)
            self.assertEqual(json.loads(texto.getvalue())["status"], "sem_rosto")
            relatorio = next((Path(pasta) / "saida").glob("*/resultado.json"))
            self.assertIn("configuracao", json.loads(relatorio.read_text(encoding="utf-8")))

    def test_cli_arquivo_inexistente_retorna_erro(self):
        with contextlib.redirect_stderr(io.StringIO()) as texto:
            self.assertEqual(main(["imagem", "--entrada", "nao_existe.png"]), 1)
            self.assertIn("não encontrado", texto.getvalue())

    def test_cli_exige_destino_e_limite_sem_gui(self):
        for args in [["imagem", "--entrada", "x", "--salvar-imagens"], ["webcam", "--sem-janela"],
                     ["webcam", "--max-frames", "0"], ["webcam", "--camera", "-1"]]:
            with self.subTest(args=args), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exc:
                main(args)
            self.assertEqual(exc.exception.code, 2)

    @patch("processamento_imagens.cli.ProcessadorFacial")
    @patch("processamento_imagens.cli.Webcam")
    def test_cli_webcam_limitada_e_sem_janela(self, fabrica_camera, fabrica_processador):
        fabrica_processador.return_value = self.processador
        camera = MagicMock()
        camera.ler.return_value = imagem_nitida()
        fabrica_camera.return_value.__enter__.return_value = camera
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["webcam", "--sem-janela", "--max-frames", "3"]), 0)
        self.assertEqual(camera.ler.call_count, 3)
        fabrica_camera.return_value.__exit__.assert_called_once()

    @patch("processamento_imagens.cli.preparar_modelos", return_value={"yunet": Path("a"), "sface": Path("b")})
    def test_cli_download_e_explicito(self, preparar):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["preparar-modelos"]), 0)
        preparar.assert_called_once_with(None)
