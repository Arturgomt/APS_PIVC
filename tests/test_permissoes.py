"""Regras de hierarquia (api.pode_*): quem vê, edita, aprova e exclui. Não precisa de banco."""

import unittest

from api import CADASTROS, pode_aprovar, pode_editar, pode_excluir, pode_ver

PRODUCAO, QUALIDADE = 1, 2
ANALISTA = {"id": 10, "nivel_permissao": 1, "divisao_id": PRODUCAO, "papel": "usuario"}
DIRETOR = {"id": 20, "nivel_permissao": 2, "divisao_id": PRODUCAO, "papel": "usuario"}
MINISTRO = {"id": 30, "nivel_permissao": 3, "divisao_id": None, "papel": "usuario"}
ADMIN_ANALISTA = dict(ANALISTA, id=40, papel="administrador")
CONTEUDO, ESTRUTURA = CADASTROS["produtos"], CADASTROS["instalacoes"]


def item(nivel=1, setor=PRODUCAO, status="aprovado", autor=99):
    return {"nivel_sigilo": nivel, "setor_id": setor, "status": status, "criado_por": autor}


class HierarquiaTests(unittest.TestCase):
    def test_visibilidade_por_nivel_e_setor(self):
        casos = [  # (usuário, item, vê?)
            (ANALISTA, item(1, QUALIDADE), True),  # nível 1 é de todos os setores
            (ANALISTA, item(2), False),
            (DIRETOR, item(2), True),
            (DIRETOR, item(2, QUALIDADE), False),  # nível 2 só no próprio setor
            (DIRETOR, item(3), False),
            (MINISTRO, item(3, QUALIDADE), True),
            (ADMIN_ANALISTA, item(3), False),  # ser administrador não abre fórmulas
        ]
        for usuario, alvo, esperado in casos:
            with self.subTest(usuario=usuario["id"], alvo=alvo):
                self.assertEqual(pode_ver(usuario, alvo, CONTEUDO), esperado)

    def test_rascunho_so_para_autor_e_aprovadores(self):
        rascunho = item(status="rascunho", autor=ANALISTA["id"])
        self.assertTrue(pode_ver(ANALISTA, rascunho, CONTEUDO))
        self.assertFalse(pode_ver(dict(ANALISTA, id=11), rascunho, CONTEUDO))
        self.assertTrue(pode_ver(DIRETOR, rascunho, CONTEUDO))
        self.assertFalse(pode_ver(dict(DIRETOR, divisao_id=QUALIDADE), rascunho, CONTEUDO))

    def test_analista_so_altera_rascunho_proprio(self):
        self.assertTrue(pode_editar(ANALISTA, item(status="rascunho", autor=ANALISTA["id"]), CONTEUDO))
        self.assertFalse(pode_editar(ANALISTA, item(status="rascunho"), CONTEUDO))
        self.assertFalse(pode_editar(ANALISTA, item(), CONTEUDO))
        self.assertFalse(pode_aprovar(ANALISTA, item(status="rascunho", autor=ANALISTA["id"]), CONTEUDO))
        self.assertFalse(pode_excluir(ANALISTA, item(status="rascunho", autor=ANALISTA["id"]), CONTEUDO))

    def test_diretor_aprova_e_exclui_no_proprio_setor(self):
        self.assertTrue(pode_aprovar(DIRETOR, item(2, status="rascunho"), CONTEUDO))
        self.assertFalse(pode_aprovar(DIRETOR, item(2, QUALIDADE, status="rascunho"), CONTEUDO))
        self.assertFalse(pode_aprovar(DIRETOR, item(3, status="rascunho"), CONTEUDO))
        self.assertFalse(pode_aprovar(DIRETOR, item(), CONTEUDO))  # já aprovado
        self.assertTrue(pode_excluir(DIRETOR, item(2), CONTEUDO))
        self.assertFalse(pode_editar(DIRETOR, item(1, QUALIDADE), CONTEUDO))

    def test_ministro_faz_tudo_em_qualquer_setor(self):
        for regra in (pode_ver, pode_editar, pode_excluir):
            self.assertTrue(regra(MINISTRO, item(3, QUALIDADE), CONTEUDO))
        self.assertTrue(pode_aprovar(MINISTRO, item(3, QUALIDADE, status="rascunho"), CONTEUDO))

    def test_estrutura_so_administrador_altera(self):
        self.assertTrue(pode_ver(ANALISTA, {}, ESTRUTURA))
        self.assertFalse(pode_editar(MINISTRO, {}, ESTRUTURA))
        self.assertTrue(pode_excluir(ADMIN_ANALISTA, {}, ESTRUTURA))
        self.assertFalse(pode_aprovar(ADMIN_ANALISTA, {}, ESTRUTURA))


if __name__ == "__main__":
    unittest.main()
