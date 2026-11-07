"""Fluxo da API contra MySQL/MariaDB real; o rosto é simulado.

Requer um servidor de banco: defina APS_DB_TESTE=1 e, se necessário, APS_DB_HOST/PORT/USER/PASSWORD.
O dump do grupo é importado num banco descartável (aps_teste_api), nunca no sistema_biometrico.
"""

import importlib.util
import os
from pathlib import Path
from time import time
import unittest

import cv2
import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
BANCO = "aps_teste_api"


def png(valor):
    """Imagem cujo primeiro pixel define a 'pessoa' no processador falso; 0 = sem rosto."""
    return cv2.imencode(".png", np.full((8, 8, 3), valor, np.uint8))[1].tobytes()


@unittest.skipUnless(os.environ.get("APS_DB_TESTE"), "Defina APS_DB_TESTE=1 com um MySQL/MariaDB disponível.")
class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import pymysql
        from pymysql.constants import CLIENT
        from fastapi.testclient import TestClient

        import api
        from processamento_imagens.tipos import Qualidade, Resultado, Rosto, Status

        especificacao = importlib.util.spec_from_file_location("alinhado_teste", RAIZ / "Reconhecimento Facial" / "alinhado.py")
        alinhado = importlib.util.module_from_spec(especificacao)
        especificacao.loader.exec_module(alinhado)

        class ProcessadorFalso:
            def processar(self, imagem):
                valor = int(imagem[0, 0, 0])
                if valor == 0:
                    return Resultado(Status.SEM_ROSTO, "Nenhum rosto detectado.")
                rosto = Rosto((0, 0, 9, 9), (0, 0, 9, 9), [[0.0, 0.0]] * 5, .99, Qualidade(120.0, 200.0))
                rosto.imagem_alinhada_bgr = np.full((112, 112, 3), valor, np.uint8)
                return Resultado(Status.OK, "ok", [rosto])

        class ServicoFalso:
            threshold, margin, people = .5, .05, {}

            def embedding(self, imagem):
                return np.eye(128, dtype=np.float32)[int(imagem[0, 0, 0]) % 128]

            def identify(self, imagem):
                return alinhado.decide(self.embedding(imagem), self.people, self.threshold, self.margin)

        os.environ["APS_DB_NAME"] = BANCO
        conexao = pymysql.connect(host=os.environ.get("APS_DB_HOST", "127.0.0.1"),
                                  port=int(os.environ.get("APS_DB_PORT", "3306")),
                                  user=os.environ.get("APS_DB_USER", "root"),
                                  password=os.environ.get("APS_DB_PASSWORD", ""),
                                  charset="utf8mb4", client_flag=CLIENT.MULTI_STATEMENTS, autocommit=True)
        with conexao.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS {BANCO}")
            for arquivo in ("sistema biometria APS.sql", "migracao_empresa_quimica.sql"):
                cursor.execute((RAIZ / arquivo).read_text(encoding="utf-8").replace("sistema_biometrico", BANCO))
                while cursor.nextset():
                    pass
        conexao.close()
        cls.conexao_admin = conexao
        api._motor = (ProcessadorFalso(), ServicoFalso())
        api.SESSOES.clear()
        cls.api = api
        cls.cliente = TestClient(api.app)

    @classmethod
    def tearDownClass(cls):
        cls.conexao_admin.connect()
        with cls.conexao_admin.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS {BANCO}")
        cls.conexao_admin.close()

    def entrar(self, valor):
        return self.cliente.post("/api/auth/login", files={"image": ("r.png", png(valor), "image/png")})

    def test_fluxo_completo(self):
        c = self.cliente
        self.assertEqual(self.entrar(10).json()["detail"], "Nenhum rosto cadastrado no sistema.")

        # Primeiro administrador pela linha de comando (usuário 6 do dump).
        with self.api.transacao() as cursor:
            self.assertEqual(self.api.cadastrar_amostra(cursor, 6, np.full((8, 8, 3), 10, np.uint8)), 1)
            self.api.definir_conta(cursor, 6, "administrador", 1)
        resposta = self.entrar(10)
        self.assertEqual(resposta.status_code, 200, resposta.text)
        self.assertEqual(resposta.json()["user"]["role"], "admin")
        admin = {"Authorization": "Bearer " + resposta.json()["token"]}

        self.assertEqual(self.entrar(99).status_code, 401)
        self.assertEqual(self.entrar(0).json()["detail"], "Nenhum rosto detectado.")

        novo = {"name": "Ana Diretora", "cpf": "111.222.333-44", "email": "ana@iris.gov", "job": "Diretora",
                "department": "Pesquisa", "level": 2, "role": "user", "status": "Ativo"}
        resposta = c.post("/api/users", json=novo, headers=admin)
        self.assertEqual(resposta.status_code, 201, resposta.text)
        ana = resposta.json()
        self.assertEqual((ana["cpf"], ana["department"], ana["faceSamples"]), ("111.222.333-44", "Pesquisa", 0))
        self.assertEqual(c.post("/api/users", json=novo, headers=admin).status_code, 409)

        enviar = lambda uid, valor: c.post("/api/face-enrollments", data={"user_id": str(uid)},
                                           files={"image": ("r.png", png(valor), "image/png")}, headers=admin)
        self.assertEqual(enviar(ana["id"], 10).status_code, 409)  # rosto do admin
        self.assertEqual(enviar(ana["id"], 20).json()["success"], True)
        self.assertEqual(enviar(ana["id"], 20).status_code, 200)

        usuario = {"Authorization": "Bearer " + self.entrar(20).json()["token"]}
        self.assertEqual(c.get("/api/users", headers=usuario).status_code, 403)
        self.assertEqual(c.get("/api/users", headers={"Authorization": "Bearer invalido"}).status_code, 401)

        pedir = lambda valor, nivel: c.post("/api/recognitions", data={"requested_level": str(nivel)},
                                            files={"image": ("r.png", png(valor), "image/png")}, headers=usuario).json()
        resposta = pedir(20, 2)
        self.assertTrue(resposta["authorized"])
        self.assertEqual(resposta["user"]["name"], "Ana Diretora")
        self.assertEqual(resposta["resource"]["title"], "Relatorio da Diretoria")
        resposta = pedir(20, 3)
        self.assertFalse(resposta["authorized"])
        self.assertIn("Nível insuficiente", resposta["reason"])
        resposta = pedir(10, 1)  # só o rosto decide: o admin pede pela sessão da Ana
        self.assertTrue(resposta["authorized"])
        self.assertEqual(resposta["user"]["id"], 6)
        self.assertFalse(pedir(0, 1)["identified"])

        logs = c.get("/api/access-logs", headers=admin).json()
        self.assertEqual([(l["user"], l["level"], l["allowed"]) for l in logs[:4]],
                         [("Usuário desconhecido", 1, False), ("João da Silva", 1, True),
                          ("Ana Diretora", 3, False), ("Ana Diretora", 2, True)])
        self.assertEqual(logs[4]["source"], "login")

        alterado = dict(novo, level=3, department="Gabinete")
        self.assertEqual(c.patch(f"/api/users/{ana['id']}", json=alterado, headers=admin).json()["level"], 3)
        self.assertTrue(pedir(20, 3)["authorized"])
        self.assertEqual(c.patch("/api/users/6", json=dict(novo, cpf="12345678900", role="user"), headers=admin).status_code, 400)

        rota = f"/api/users/{ana['id']}/face-samples"
        amostras = c.get(rota, headers=admin).json()
        self.assertEqual([a["order"] for a in amostras], [1, 2])
        self.assertEqual(c.get(rota, headers=usuario).status_code, 403)
        self.assertEqual(c.delete(f"{rota}/{amostras[0]['id']}", headers=admin).status_code, 204)
        self.assertEqual([a["order"] for a in c.get(rota, headers=admin).json()], [2])
        self.assertEqual(c.delete(f"{rota}/999999", headers=admin).status_code, 404)
        # Único administrador com rosto: apagar tudo trancaria o sistema, então nada muda.
        self.assertEqual(c.delete("/api/users/6/face-samples", headers=admin).status_code, 409)
        self.assertEqual(self.entrar(10).status_code, 200)

        self.assertEqual(c.delete(f"/api/users/{ana['id']}", headers=admin).status_code, 204)
        self.assertEqual(c.post("/api/recognitions", data={"requested_level": "1"},
                                files={"image": ("r.png", png(20), "image/png")}, headers=usuario).status_code, 401)
        self.assertEqual(self.entrar(20).json()["detail"], "Rosto não reconhecido.")
        ana = next(u for u in c.get("/api/users", headers=admin).json() if u["id"] == ana["id"])
        self.assertEqual((ana["status"], ana["faceSamples"]), ("Inativo", 0))
        self.assertEqual(c.delete("/api/users/6", headers=admin).status_code, 400)


    def test_hierarquia_dos_cadastros(self):
        c, api = self.cliente, self.api
        with api.transacao() as cursor:
            cursor.execute("SELECT id FROM divisoes WHERE nome = 'Produção'")
            producao = cursor.fetchone()["id"]
            cursor.execute("UPDATE usuarios SET divisao_id = %s WHERE id IN (7, 27)", (producao,))
        for uid in (7, 27, 28):  # usuários do dump: 7 nível 1, 27 nível 2, 28 nível 3
            api.SESSOES[f"t{uid}"] = (uid, time() + 600)
        analista, diretor, ministro = ({"Authorization": f"Bearer t{uid}"} for uid in (7, 27, 28))
        listar = lambda rota, quem: c.get(f"/api/{rota}", headers=quem).json()

        # Visibilidade: nível, setor e rascunhos.
        self.assertNotIn("PQ-011", {p["codigo"] for p in listar("produtos", analista)})  # rascunho de outro setor
        self.assertIn("PQ-011", {p["codigo"] for p in listar("produtos", ministro)})
        self.assertEqual(listar("processos", analista), [])
        self.assertEqual(len(listar("processos", diretor)), 2)
        self.assertEqual({d["tipo"] for d in listar("documentos", diretor)}, {"FISPQ", "Bula", "POP"})
        self.assertEqual(listar("formulas", diretor), [])
        formula = listar("formulas", ministro)[0]
        self.assertNotIn("componentes", formula)  # composição só no detalhe

        resposta = c.get(f"/api/formulas/{formula['id']}", headers=diretor)
        self.assertEqual(resposta.status_code, 403)
        self.assertIn("Diretor", resposta.json()["detail"])
        detalhe = c.get(f"/api/formulas/{formula['id']}", headers=ministro).json()
        self.assertAlmostEqual(sum(x["percentual"] for x in detalhe["componentes"]), 100)
        with api.transacao() as cursor:
            cursor.execute("SELECT acao FROM eventos_administrativos WHERE entidade = 'formulas'")
            self.assertEqual([e["acao"] for e in cursor.fetchall()], ["visualizar"])

        # Aprovação: analista cria rascunho, diretor do setor aprova.
        novo = {"codigo": "PQ-900", "nome": "Ácido Cítrico 50%", "cas": "77-92-9", "unidade": "L", "estoque": 100}
        criado = c.post("/api/produtos", json=novo, headers=analista).json()
        self.assertEqual((criado["status"], criado["setor"], criado["podeAprovar"]), ("rascunho", "Produção", False))
        rota = f"/api/produtos/{criado['id']}"
        self.assertEqual(c.post(f"{rota}/aprovar", headers=analista).status_code, 403)
        self.assertEqual(c.put(rota, json=dict(novo, estoque=150), headers=analista).status_code, 200)
        aprovado = c.post(f"{rota}/aprovar", headers=diretor).json()
        self.assertEqual((aprovado["status"], aprovado["aprovador"], aprovado["estoque"]), ("aprovado", "Diretor Teste", 150))
        self.assertEqual(c.post(f"{rota}/aprovar", headers=diretor).status_code, 409)
        self.assertEqual(c.put(rota, json=novo, headers=analista).status_code, 403)
        self.assertEqual(c.post("/api/produtos", json=dict(novo, nome="Outro"), headers=diretor).status_code, 409)

        # Cada perfil só cria até o próprio nível.
        processo = {"nome": "Envase do ácido cítrico", "produto_id": criado["id"], "etapas": "1. Envasar."}
        self.assertEqual(c.post("/api/processos", json=processo, headers=analista).status_code, 403)
        self.assertEqual(c.post("/api/processos", json=processo, headers=diretor).status_code, 201)
        formula_nova = {"produto_id": criado["id"], "versao": "1.0", "componentes": [{"nome": "Água", "percentual": 50}]}
        self.assertEqual(c.post("/api/formulas", json=formula_nova, headers=diretor).status_code, 403)
        excesso = dict(formula_nova, componentes=[{"nome": "Água", "percentual": 60}, {"nome": "Ácido", "percentual": 50}])
        self.assertEqual(c.post("/api/formulas", json=excesso, headers=ministro).status_code, 422)
        documento = {"titulo": "Plano de emergência", "tipo": "Outro", "conteudo": "Rotas de fuga.", "nivel_sigilo": 3}
        self.assertEqual(c.post("/api/documentos", json=documento, headers=diretor).status_code, 403)
        doc = c.post("/api/documentos", json=dict(documento, nivel_sigilo=2, setor_id=producao), headers=ministro).json()
        self.assertTrue(next(d for d in listar("documentos", diretor) if d["id"] == doc["id"])["podeAprovar"])

        # Estrutura: só administrador; ser administrador não amplia o nível.
        self.assertEqual(c.post("/api/setores", json={"nome": "Compras"}, headers=ministro).status_code, 403)
        with api.transacao() as cursor:
            api.definir_conta(cursor, 7, "administrador", 1)
        self.assertEqual(c.post("/api/setores", json={"nome": "Compras"}, headers=analista).status_code, 201)
        self.assertEqual(c.delete(f"/api/setores/{producao}", headers=analista).status_code, 409)  # em uso
        self.assertEqual(listar("processos", analista), [])

        permissoes = c.get("/api/permissoes", headers=diretor).json()
        regras = {(r["rota"], r["nivel"]): r for r in permissoes["regras"]}
        self.assertEqual((permissoes["perfil"], permissoes["setor"]), ("Diretor", "Produção"))
        self.assertTrue(regras[("processos", 2)]["aprovar"])
        self.assertFalse(regras[("processos", 2)]["verOutrosSetores"])
        self.assertFalse(regras[("formulas", 3)]["verProprioSetor"])
        self.assertTrue(regras[("documentos", 1)]["verOutrosSetores"])

        self.assertEqual(c.delete(rota, headers=analista).status_code, 403)
        self.assertEqual(c.delete(rota, headers=diretor).status_code, 409)  # processo ligado ao produto


if __name__ == "__main__":
    unittest.main()
