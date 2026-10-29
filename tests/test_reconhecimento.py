"""Inclui os testes do reconhecimento na descoberta principal da equipe."""
import importlib.util
from pathlib import Path
import sys
import unittest

PASTA = Path(__file__).resolve().parents[1] / 'Reconhecimento Facial'


def load_tests(loader, tests, pattern):
    # O teste original usa import alinhado; limitar essa resolução ao carregamento.
    sys.path.insert(0, str(PASTA))
    try:
        spec = importlib.util.spec_from_file_location('test_alinhado_grupo', PASTA / 'test_alinhado.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return loader.loadTestsFromModule(module)
    finally:
        sys.path.remove(str(PASTA))
