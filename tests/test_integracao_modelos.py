import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import numpy as np

from exemplos.integrar_reconhecimento import carregar_servico
from processamento_imagens import ProcessadorFacial, reconhecer
from processamento_imagens.modelos import preparar_modelos, sha256
from tests.test_pipeline import PreparadorFixo, imagem_nitida


class IntegracaoTests(unittest.TestCase):
    def test_chama_servico_com_formato_correto(self):
        resultado = ProcessadorFacial(preparador=PreparadorFixo()).processar(imagem_nitida())
        servico = Mock()
        servico.identify.return_value = {"status": "candidato", "person_id": "001", "similarity": .8}
        saida = reconhecer(resultado, servico)
        imagem = servico.identify.call_args.args[0]
        np.testing.assert_array_equal(imagem, resultado.entrada_reconhecimento)
        self.assertEqual(saida["reconhecimento"]["person_id"], "001")
        self.assertNotIn("acesso_permitido", saida)

    def test_captura_rejeitada_nao_chama_reconhecedor(self):
        for preparador in [PreparadorFixo([]), PreparadorFixo([np.zeros(15)])]:
            servico = Mock()
            resultado = ProcessadorFacial(preparador=preparador).processar(imagem_nitida())
            self.assertIsNone(reconhecer(resultado, servico)["reconhecimento"])
            servico.identify.assert_not_called()

    def test_modulo_externo_ausente_e_contrato_incompativel(self):
        with self.assertRaisesRegex(ValueError, "não encontrado"):
            carregar_servico("nao_existe.py", "nao_criar.json")
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "alinhado.py"
            arquivo.write_text("VERSION = 'outro-contrato'\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "contrato"):
                carregar_servico(arquivo, Path(pasta) / "pessoas.json")
            self.assertFalse((Path(pasta) / "pessoas.json").exists())


class ModelosTests(unittest.TestCase):
    def test_modelo_existente_valido_nao_acessa_rede(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "modelo.onnx"
            arquivo.write_bytes(b"modelo-local")
            manifesto = {"teste": {"arquivo": arquivo.name, "diretorio": "teste", "sha256": sha256(arquivo)}}
            with patch("processamento_imagens.modelos.MODELOS", manifesto), patch("processamento_imagens.modelos.urlopen") as rede:
                preparar_modelos(pasta)
                rede.assert_not_called()

    def test_modelo_existente_incorreto_nao_e_sobrescrito(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "modelo.onnx"
            arquivo.write_bytes(b"preservar")
            manifesto = {"teste": {"arquivo": arquivo.name, "diretorio": "teste", "sha256": "0" * 64}}
            with patch("processamento_imagens.modelos.MODELOS", manifesto), self.assertRaises(ValueError):
                preparar_modelos(pasta)
            self.assertEqual(arquivo.read_bytes(), b"preservar")

    def test_download_corrompido_nao_publica_modelo_e_limpa_parcial(self):
        with tempfile.TemporaryDirectory() as pasta:
            manifesto = {"teste": {"arquivo": "modelo.onnx", "diretorio": "teste", "sha256": "0" * 64}}
            with patch("processamento_imagens.modelos.MODELOS", manifesto), \
                    patch("processamento_imagens.modelos.urlopen", return_value=io.BytesIO(b"errado")), self.assertRaises(ValueError):
                preparar_modelos(pasta)
            self.assertFalse(list(Path(pasta).iterdir()))
