"""API HTTP do IRIS: login e acesso pelo rosto; usuários, biometria e histórico no MySQL.

Servidor:        python api.py              (front-end com VITE_DEMO_MODE=false)
Primeiro admin:  python api.py cadastrar-rosto --usuario 6 --admin foto1.jpg foto2.jpg
Banco:           variáveis APS_DB_HOST, APS_DB_PORT, APS_DB_USER, APS_DB_PASSWORD, APS_DB_NAME.
"""

import argparse
from contextlib import contextmanager
from dataclasses import asdict
from datetime import date, datetime, timezone
import json
import os
import re
import secrets
import sys
from threading import Lock
from time import perf_counter, time
from typing import Literal
from uuid import uuid4

import cv2
from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
from pydantic import BaseModel, Field, model_validator
import pymysql

from exemplos.integrar_reconhecimento import MODULO_PADRAO, RAIZ, carregar_servico
from processamento_imagens import CONTRATO_SFACE, Configuracao, ProcessadorFacial
from processamento_imagens.aquisicao import ErroAquisicao, ler_imagem
from processamento_imagens.modelos import MODELOS

TAMANHO_MAXIMO = 5_000_000
SESSAO_SEGUNDOS = 8 * 3600
# ponytail: sessões em memória; reiniciar a API exige novo login. Persistir em tabela se houver vários processos.
SESSOES: dict[str, tuple[int, float]] = {}
# ponytail: trava global; os modelos OpenCV não são thread-safe e a APS tem uma câmera por vez.
TRAVA = Lock()
_motor = None

app = FastAPI(title="IRIS APS", description="Login e controle de acesso por reconhecimento facial.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("APS_FRONTEND", "http://localhost:5173,http://127.0.0.1:5173").split(","),
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)


@app.exception_handler(pymysql.err.OperationalError)
def banco_indisponivel(_, exc):
    return JSONResponse({"detail": f"Banco de dados indisponível: {exc.args[-1]}"}, status_code=503)


@app.exception_handler(RequestValidationError)
def dados_invalidos(_, exc):
    erros = "; ".join(f"{e['loc'][-1]}: {e['msg']}" for e in exc.errors())
    return JSONResponse({"detail": f"Dados inválidos — {erros}"}, status_code=422)


def motor(limiar=0.5, margem=0.05):
    """Processamento e SFace carregados uma vez; os embeddings vêm do MySQL, não do JSON do serviço."""
    global _motor
    if _motor is None:
        servico = carregar_servico(MODULO_PADRAO, RAIZ / "dados" / "nao_usado_pela_api.json",
                                   threshold=limiar, margin=margem)
        _motor = (ProcessadorFacial(), servico)
    return _motor


def conectar():
    return pymysql.connect(
        host=os.environ.get("APS_DB_HOST", "127.0.0.1"), port=int(os.environ.get("APS_DB_PORT", "3306")),
        user=os.environ.get("APS_DB_USER", "root"), password=os.environ.get("APS_DB_PASSWORD", ""),
        database=os.environ.get("APS_DB_NAME", "sistema_biometrico"),
        charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor,
    )


@contextmanager
def transacao():
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            yield cursor
        conexao.commit()
    except pymysql.err.IntegrityError as exc:
        conexao.rollback()
        mensagens = {
            1062: (409, "Já existe um cadastro com esse CPF, e-mail, código ou nome."),
            1451: (409, "Não é possível excluir: há outros cadastros ligados a este registro."),
            1452: (422, "Referência inválida: setor, produto ou instalação inexistente."),
        }
        if exc.args[0] in mensagens:
            raise HTTPException(*mensagens[exc.args[0]]) from exc
        raise
    except BaseException:
        conexao.rollback()
        raise
    finally:
        conexao.close()


# ---------- Usuários ----------

SQL_USUARIO = """
SELECT u.id, u.nome, u.cpf, u.login, u.email, u.cargo, u.nivel_permissao, u.status, u.divisao_id, u.criado_em,
       d.nome AS divisao, c.id AS conta_id, c.papel,
       (SELECT COUNT(*) FROM amostras_faciais a JOIN cadastros_faciais f ON f.id = a.cadastro_facial_id
        WHERE f.usuario_id = u.id AND f.status = 'ativo') AS amostras
FROM usuarios u LEFT JOIN divisoes d ON d.id = u.divisao_id LEFT JOIN contas c ON c.usuario_id = u.id
"""


def buscar_usuario(c, usuario_id):
    c.execute(SQL_USUARIO + " WHERE u.id = %s", (usuario_id,))
    return c.fetchone()


def ativo(usuario) -> bool:
    return usuario["status"] != "inativo"


def publico(u) -> dict:
    """Linha do banco no formato usado pelo front-end."""
    return {
        "id": u["id"], "name": u["nome"], "cpf": u["cpf"], "email": u["email"] or "",
        "job": u["cargo"] or "", "department": u["divisao"] or "", "level": u["nivel_permissao"],
        "role": "admin" if u["papel"] == "administrador" else "user",
        "status": "Ativo" if ativo(u) else "Inativo",
        "createdAt": str(u["criado_em"])[:10], "faceSamples": int(u["amostras"]),
    }


class DadosUsuario(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    cpf: str = Field(max_length=20)
    email: str = Field("", max_length=254)
    job: str = Field("", max_length=100)
    department: str = Field("", max_length=100)
    level: int = Field(ge=1, le=3)
    role: Literal["admin", "user"] = "user"
    status: Literal["Ativo", "Inativo"] = "Ativo"


def formatar_cpf(cpf: str) -> str:
    digitos = re.sub(r"\D", "", cpf)
    if len(digitos) != 11:
        raise HTTPException(422, "CPF deve ter 11 dígitos.")
    return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"


def divisao_id(c, nome: str):
    nome = nome.strip()
    if not nome:
        return None
    c.execute("SELECT id FROM divisoes WHERE nome = %s", (nome,))
    linha = c.fetchone()
    if linha:
        return linha["id"]
    c.execute("INSERT INTO divisoes (nome) VALUES (%s)", (nome,))
    return c.lastrowid


def definir_conta(c, usuario_id, papel, conta_ativa):
    """Sem senha: a conta só registra o papel; a autenticação é pelo rosto."""
    c.execute("SELECT id FROM contas WHERE usuario_id = %s", (usuario_id,))
    if c.fetchone():
        c.execute("UPDATE contas SET papel = %s, ativo = %s WHERE usuario_id = %s", (papel, conta_ativa, usuario_id))
    else:
        c.execute("INSERT INTO contas (usuario_id, login, senha_hash, papel, ativo) "
                  "SELECT id, login, '!', %s, %s FROM usuarios WHERE id = %s", (papel, conta_ativa, usuario_id))


def colunas(c, dados: DadosUsuario) -> tuple:
    return (dados.name.strip(), formatar_cpf(dados.cpf), dados.level,
            "ativo" if dados.status == "Ativo" else "inativo", int(dados.status == "Ativo"),
            dados.email.strip().lower() or None, dados.job.strip() or None, divisao_id(c, dados.department))


def evento(c, responsavel, acao, registro_id, detalhes=None, entidade="usuarios"):
    c.execute("INSERT INTO eventos_administrativos (conta_responsavel_id, acao, entidade, registro_id, detalhes) "
              "VALUES (%s, %s, %s, %s, %s)",
              (responsavel["conta_id"], acao, entidade, str(registro_id),
               json.dumps(detalhes, ensure_ascii=False) if detalhes else None))


# ---------- Biometria ----------

def configuracao_id(c) -> int:
    sha = MODELOS["sface"]["sha256"]
    c.execute("SELECT id FROM configuracoes_biometricas WHERE contrato_preprocessamento = %s AND modelo_sha256 = %s "
              "ORDER BY id LIMIT 1", (CONTRATO_SFACE, sha))
    linha = c.fetchone()
    if linha:
        return linha["id"]
    c.execute("INSERT INTO configuracoes_biometricas (modelo_nome, modelo_versao, modelo_sha256, dimensao_embedding, "
              "contrato_preprocessamento, parametros_preprocessamento) VALUES ('SFace', '2021dec', %s, 128, %s, %s)",
              (sha, CONTRATO_SFACE, json.dumps(asdict(Configuracao()))))
    return c.lastrowid


def carregar_pessoas(c, config) -> dict[str, list]:
    # Inclui inativos: assim um inativo é reconhecido e negado, em vez de confundido com outra pessoa.
    c.execute("SELECT f.usuario_id, a.embedding FROM amostras_faciais a "
              "JOIN cadastros_faciais f ON f.id = a.cadastro_facial_id "
              "WHERE f.status = 'ativo' AND f.configuracao_id = %s", (config,))
    pessoas = {}
    for linha in c.fetchall():
        pessoas.setdefault(str(linha["usuario_id"]), []).append(json.loads(linha["embedding"]))
    return pessoas


def ler_upload(arquivo: UploadFile):
    dados = arquivo.file.read(TAMANHO_MAXIMO + 1)
    if len(dados) > TAMANHO_MAXIMO:
        raise HTTPException(413, "Imagem maior que 5 MB.")
    imagem = cv2.imdecode(np.frombuffer(dados, np.uint8), cv2.IMREAD_COLOR) if dados else None
    if imagem is None:
        raise HTTPException(422, "Arquivo de imagem inválido.")
    return imagem


def analisar(c, imagem, com_embedding=False):
    """Processa a imagem e identifica (1:N) entre todos os rostos cadastrados."""
    processador, servico = motor()
    config = configuracao_id(c)
    pessoas = carregar_pessoas(c, config)
    with TRAVA:
        resultado = processador.processar(imagem)
        entrada = resultado.entrada_reconhecimento
        reconhecimento = embedding = None
        if entrada is not None:
            servico.people = pessoas
            reconhecimento = servico.identify(entrada)
            if com_embedding:
                embedding = servico.embedding(entrada)
    usuario = None
    if reconhecimento and reconhecimento["status"] == "candidato":
        usuario = buscar_usuario(c, int(reconhecimento["person_id"]))
    return resultado, reconhecimento, usuario, embedding, config


def falha_identificacao(resultado, reconhecimento, usuario):
    if reconhecimento is None:
        return resultado.mensagem
    if reconhecimento["status"] == "sem_cadastros":
        return "Nenhum rosto cadastrado no sistema."
    if reconhecimento["status"] == "desconhecido":
        return "Rosto não reconhecido."
    if reconhecimento["status"] == "inconclusivo":
        return "Reconhecimento inconclusivo: rosto semelhante a mais de uma pessoa. Tente novamente."
    if usuario is None:
        return "Cadastro do rosto sem usuário correspondente."
    if not ativo(usuario):
        return "Usuário inativo."
    return None


def registrar_tentativa(c, *, resultado, reconhecimento, usuario, permitido, motivo, origem,
                        config, inicio, solicitante=None, recurso=None):
    _, servico = motor()
    c.execute(
        "INSERT INTO tentativas_acesso (usuario_id, resultado, motivo, requisicao_id, conta_solicitante_id, "
        "usuario_candidato_id, recurso_id, configuracao_id, status_processamento, status_reconhecimento, "
        "similaridade, limiar_aplicado, margem_aplicada, acesso_permitido, origem, tempo_total_ms) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (usuario["id"] if usuario else None, "AUTORIZADO" if permitido else "NEGADO", motivo[:255], str(uuid4()),
         solicitante["conta_id"] if solicitante else None, usuario["id"] if usuario else None,
         recurso["id"] if recurso else None, config, resultado.status.value,
         reconhecimento["status"] if reconhecimento else None,
         reconhecimento["similarity"] if reconhecimento else None, servico.threshold, servico.margin,
         int(permitido), origem, round((perf_counter() - inicio) * 1000, 3)),
    )


def cadastrar_amostra(c, usuario_id, imagem, responsavel=None) -> int:
    if buscar_usuario(c, usuario_id) is None:
        raise HTTPException(404, "Usuário não encontrado.")
    resultado, reconhecimento, outro, embedding, config = analisar(c, imagem, com_embedding=True)
    if embedding is None:
        raise HTTPException(422, resultado.mensagem)
    if outro is not None and outro["id"] != usuario_id:
        raise HTTPException(409, f"Este rosto já está cadastrado para {outro['nome']}.")
    c.execute("UPDATE cadastros_faciais SET status = 'substituido', desativado_em = NOW() "
              "WHERE usuario_id = %s AND status = 'ativo' AND configuracao_id <> %s", (usuario_id, config))
    c.execute("SELECT id FROM cadastros_faciais WHERE usuario_id = %s AND status = 'ativo'", (usuario_id,))
    linha = c.fetchone()
    if linha:
        cadastro = linha["id"]
    else:
        c.execute("INSERT INTO cadastros_faciais (usuario_id, configuracao_id, cadastrado_por) VALUES (%s, %s, %s)",
                  (usuario_id, config, responsavel["conta_id"] if responsavel else None))
        cadastro = c.lastrowid
    c.execute("SELECT COALESCE(MAX(ordem), 0) + 1 AS ordem FROM amostras_faciais WHERE cadastro_facial_id = %s", (cadastro,))
    ordem = c.fetchone()["ordem"]
    rosto = resultado.rostos[0]
    c.execute("INSERT INTO amostras_faciais (cadastro_facial_id, ordem, embedding, brilho_medio, "
              "variancia_laplaciano, confianca_deteccao) VALUES (%s, %s, %s, %s, %s, %s)",
              (cadastro, ordem, json.dumps([round(float(v), 7) for v in embedding]),
               rosto.qualidade.brilho_medio, rosto.qualidade.variancia_laplaciano, rosto.confianca_deteccao))
    return ordem


# ---------- Autenticação ----------

def sessao(authorization: str | None = Header(None)):
    token = (authorization or "").removeprefix("Bearer ").strip()
    entrada = SESSOES.get(token)
    if entrada is None or entrada[1] < time():
        SESSOES.pop(token, None)
        raise HTTPException(401, "Sessão expirada. Entre novamente com o rosto.")
    with transacao() as c:
        usuario = buscar_usuario(c, entrada[0])
    if usuario is None or not ativo(usuario):
        SESSOES.pop(token, None)
        raise HTTPException(401, "Conta inativa.")
    return usuario


def administrador(usuario=Depends(sessao)):
    if usuario["papel"] != "administrador":
        raise HTTPException(403, "Apenas administradores.")
    return usuario


@app.post("/api/auth/login")
def login(image: UploadFile = File(...)):
    inicio, imagem = perf_counter(), ler_upload(image)
    with transacao() as c:
        resultado, reconhecimento, usuario, _, config = analisar(c, imagem)
        falha = falha_identificacao(resultado, reconhecimento, usuario)
        registrar_tentativa(c, resultado=resultado, reconhecimento=reconhecimento, usuario=usuario,
                            permitido=falha is None, motivo=falha or "Login pelo rosto.", origem="login",
                            config=config, inicio=inicio)
    if falha:
        raise HTTPException(401, falha)
    token = secrets.token_urlsafe(32)
    SESSOES[token] = (usuario["id"], time() + SESSAO_SEGUNDOS)
    return {"user": publico(usuario), "token": token}


@app.post("/api/auth/logout", status_code=204)
def logout(authorization: str | None = Header(None)):
    SESSOES.pop((authorization or "").removeprefix("Bearer ").strip(), None)


# ---------- Acesso aos níveis ----------

@app.post("/api/recognitions")
def reconhecer_acesso(image: UploadFile = File(...), requested_level: int = Form(..., ge=1, le=3),
                      solicitante=Depends(sessao)):
    inicio, imagem = perf_counter(), ler_upload(image)
    with transacao() as c:
        c.execute("SELECT r.id, r.titulo, r.conteudo, r.divisao_id, n.exige_divisao FROM recursos_protegidos r "
                  "JOIN niveis_acesso n ON n.id = r.nivel_exigido_id WHERE n.codigo = %s AND r.ativo = 1 "
                  "ORDER BY r.id LIMIT 1", (requested_level,))
        recurso = c.fetchone()
        if recurso is None:
            raise HTTPException(409, f"Nenhum recurso ativo cadastrado para o nível {requested_level}.")
        resultado, reconhecimento, usuario, _, config = analisar(c, imagem)
        motivo = falha_identificacao(resultado, reconhecimento, usuario)
        permitido = False
        if motivo is None:
            if usuario["nivel_permissao"] < requested_level:
                motivo = (f"Nível insuficiente: {usuario['nome']} possui nível {usuario['nivel_permissao']}, "
                          f"solicitado nível {requested_level}.")
            elif recurso["exige_divisao"] and recurso["divisao_id"] not in (None, usuario["divisao_id"]):
                motivo = "Recurso restrito a outra divisão."
            else:
                permitido = True
                motivo = f"Acesso autorizado a {usuario['nome']}: {recurso['titulo']}."
        registrar_tentativa(c, resultado=resultado, reconhecimento=reconhecimento, usuario=usuario,
                            permitido=permitido, motivo=motivo, origem="api", config=config, inicio=inicio,
                            solicitante=solicitante, recurso=recurso)
    return {
        "identified": usuario is not None, "authorized": permitido,
        "user": publico(usuario) if usuario else None,
        "confidence": reconhecimento["similarity"] if reconhecimento else None,
        "reason": motivo, "timestamp": datetime.now(timezone.utc).isoformat(),
        "resource": {"title": recurso["titulo"], "content": recurso["conteudo"]} if permitido else None,
    }


# ---------- Administração ----------

@app.get("/api/users")
def listar_usuarios(_=Depends(administrador)):
    with transacao() as c:
        c.execute(SQL_USUARIO + " ORDER BY u.nome")
        return [publico(u) for u in c.fetchall()]


@app.post("/api/users", status_code=201)
def criar_usuario(dados: DadosUsuario, responsavel=Depends(administrador)):
    with transacao() as c:
        valores = colunas(c, dados)
        # Login é exigido pela tabela, mas não é usado: a entrada é pelo rosto.
        c.execute("INSERT INTO usuarios (nome, cpf, nivel_permissao, status, ativo, email, cargo, divisao_id, "
                  "login, senha_hash, criado_por) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, '!', %s)",
                  (*valores, re.sub(r"\D", "", valores[1]), responsavel["conta_id"]))
        novo = c.lastrowid
        definir_conta(c, novo, "administrador" if dados.role == "admin" else "usuario", valores[4])
        evento(c, responsavel, "criar", novo)
        return publico(buscar_usuario(c, novo))


@app.patch("/api/users/{usuario_id}")
def atualizar_usuario(usuario_id: int, dados: DadosUsuario, responsavel=Depends(administrador)):
    if usuario_id == responsavel["id"] and (dados.role != "admin" or dados.status != "Ativo"):
        raise HTTPException(400, "Você não pode remover seu próprio acesso de administrador.")
    with transacao() as c:
        if buscar_usuario(c, usuario_id) is None:
            raise HTTPException(404, "Usuário não encontrado.")
        valores = colunas(c, dados)
        c.execute("UPDATE usuarios SET nome = %s, cpf = %s, nivel_permissao = %s, status = %s, ativo = %s, "
                  "email = %s, cargo = %s, divisao_id = %s WHERE id = %s", (*valores, usuario_id))
        definir_conta(c, usuario_id, "administrador" if dados.role == "admin" else "usuario", valores[4])
        garantir_admin_com_rosto(c)
        evento(c, responsavel, "editar", usuario_id)
        return publico(buscar_usuario(c, usuario_id))


@app.delete("/api/users/{usuario_id}", status_code=204)
def excluir_usuario(usuario_id: int, responsavel=Depends(administrador)):
    """Apaga a biometria e desativa o usuário; o histórico de acessos é preservado."""
    if usuario_id == responsavel["id"]:
        raise HTTPException(400, "Não é permitido excluir a própria conta.")
    with transacao() as c:
        if buscar_usuario(c, usuario_id) is None:
            raise HTTPException(404, "Usuário não encontrado.")
        c.execute("DELETE a FROM amostras_faciais a JOIN cadastros_faciais f ON f.id = a.cadastro_facial_id "
                  "WHERE f.usuario_id = %s", (usuario_id,))
        c.execute("DELETE FROM cadastros_faciais WHERE usuario_id = %s", (usuario_id,))
        c.execute("DELETE FROM biometria WHERE usuario_id = %s", (usuario_id,))
        c.execute("UPDATE usuarios SET status = 'inativo', ativo = 0 WHERE id = %s", (usuario_id,))
        c.execute("UPDATE contas SET ativo = 0 WHERE usuario_id = %s", (usuario_id,))
        garantir_admin_com_rosto(c)
        evento(c, responsavel, "excluir", usuario_id, {"biometria": "apagada"})


def garantir_admin_com_rosto(c):
    """Chamada dentro da transação: desfaz a mudança se nenhum administrador conseguiria entrar."""
    c.execute("SELECT COUNT(*) AS total FROM amostras_faciais a JOIN cadastros_faciais f ON f.id = a.cadastro_facial_id "
              "JOIN contas c ON c.usuario_id = f.usuario_id JOIN usuarios u ON u.id = f.usuario_id "
              "WHERE f.status = 'ativo' AND c.papel = 'administrador' AND c.ativo = 1 AND u.status <> 'inativo'")
    if c.fetchone()["total"] == 0:
        raise HTTPException(409, "Operação bloqueada: nenhum administrador ficaria com rosto cadastrado e "
                                 "ninguém conseguiria entrar. Cadastre o rosto de outro administrador antes.")


@app.get("/api/users/{usuario_id}/face-samples")
def listar_amostras(usuario_id: int, _=Depends(administrador)):
    with transacao() as c:
        c.execute("SELECT a.id, a.ordem, a.capturado_em, a.brilho_medio, a.variancia_laplaciano, a.confianca_deteccao "
                  "FROM amostras_faciais a JOIN cadastros_faciais f ON f.id = a.cadastro_facial_id "
                  "WHERE f.usuario_id = %s AND f.status = 'ativo' ORDER BY a.ordem", (usuario_id,))
        return [{"id": a["id"], "order": a["ordem"], "capturedAt": a["capturado_em"].isoformat(),
                 "brightness": a["brilho_medio"], "sharpness": a["variancia_laplaciano"],
                 "confidence": a["confianca_deteccao"]} for a in c.fetchall()]


@app.delete("/api/users/{usuario_id}/face-samples", status_code=204)
@app.delete("/api/users/{usuario_id}/face-samples/{amostra_id}", status_code=204)
def apagar_amostras(usuario_id: int, amostra_id: int | None = None, responsavel=Depends(administrador)):
    """Sem amostra_id apaga todas; o cadastro facial vazio é removido junto."""
    with transacao() as c:
        filtro, valores = ("", (usuario_id,)) if amostra_id is None else (" AND a.id = %s", (usuario_id, amostra_id))
        c.execute("DELETE a FROM amostras_faciais a JOIN cadastros_faciais f ON f.id = a.cadastro_facial_id "
                  "WHERE f.usuario_id = %s" + filtro, valores)
        if c.rowcount == 0:
            raise HTTPException(404, "Amostra não encontrada.")
        apagadas = c.rowcount
        c.execute("DELETE f FROM cadastros_faciais f LEFT JOIN amostras_faciais a ON a.cadastro_facial_id = f.id "
                  "WHERE f.usuario_id = %s AND a.id IS NULL", (usuario_id,))
        garantir_admin_com_rosto(c)
        evento(c, responsavel, "apagar_rosto", usuario_id, {"amostras_apagadas": apagadas, "amostra_id": amostra_id})


@app.post("/api/face-enrollments")
def cadastrar_rosto(user_id: int = Form(...), image: UploadFile = File(...), responsavel=Depends(administrador)):
    imagem = ler_upload(image)
    with transacao() as c:
        ordem = cadastrar_amostra(c, user_id, imagem, responsavel)
        evento(c, responsavel, "cadastrar_rosto", user_id, {"amostra": ordem})
    return {"success": True, "message": f"Amostra {ordem} cadastrada. Recomenda-se de 3 a 5 amostras por pessoa."}


@app.get("/api/access-logs")
def historico(_=Depends(administrador)):
    with transacao() as c:
        c.execute("SELECT t.id, t.ocorrido_em, t.acesso_permitido, t.origem, t.motivo, t.similaridade, "
                  "u.nome, n.codigo FROM tentativas_acesso t "
                  "LEFT JOIN usuarios u ON u.id = COALESCE(t.usuario_candidato_id, t.usuario_id) "
                  "LEFT JOIN recursos_protegidos r ON r.id = t.recurso_id "
                  "LEFT JOIN niveis_acesso n ON n.id = r.nivel_exigido_id "
                  "ORDER BY t.ocorrido_em DESC, t.id DESC LIMIT 500")
        return [{"id": t["id"], "date": t["ocorrido_em"].isoformat(), "user": t["nome"] or "Usuário desconhecido",
                 "level": t["codigo"], "allowed": bool(t["acesso_permitido"]), "source": (t["origem"] or "api").lower(),
                 "reason": t["motivo"], "similarity": t["similaridade"]} for t in c.fetchall()]


# ---------- Cadastros da empresa e hierarquia ----------
# Perfil = usuarios.nivel_permissao. Cada item tem setor, nível de sigilo e status (rascunho/aprovado).
# Setores e instalações são estruturais: todos veem, só administradores alteram.

PERFIS = {1: "Analista", 2: "Diretor", 3: "Ministro"}
NIVEIS = {1: "interno", 2: "restrito ao setor", 3: "confidencial"}


def pode_ver(u, item, spec) -> bool:
    if spec.get("estrutural"):
        return True
    meu, nivel = u["nivel_permissao"], item["nivel_sigilo"]
    if nivel > meu or (nivel > 1 and meu < 3 and item["setor_id"] != u["divisao_id"]):
        return False
    return item["status"] == "aprovado" or item["criado_por"] == u["id"] or pode_aprovar(u, item, spec)


def pode_editar(u, item, spec) -> bool:
    if spec.get("estrutural"):
        return u["papel"] == "administrador"
    meu = u["nivel_permissao"]
    if item["nivel_sigilo"] > meu or (meu < 3 and item["setor_id"] != u["divisao_id"]):
        return False
    # Analista só altera os próprios rascunhos; diretor e ministro alteram tudo o que alcançam.
    return meu >= 2 or (item["status"] == "rascunho" and item["criado_por"] == u["id"])


def pode_aprovar(u, item, spec) -> bool:
    return (not spec.get("estrutural") and item["status"] == "rascunho"
            and u["nivel_permissao"] >= 2 and pode_editar(u, item, spec))


def pode_excluir(u, item, spec) -> bool:
    return pode_editar(u, item, spec) and (spec.get("estrutural") or u["nivel_permissao"] >= 2)


def motivo_negado(u, item, spec) -> str:
    if spec.get("estrutural"):
        return "Somente administradores alteram setores e instalações."
    meu = u["nivel_permissao"]
    if item["nivel_sigilo"] > meu:
        return (f"Seu perfil ({PERFIS[meu]}) não acessa itens de nível {item['nivel_sigilo']} "
                f"({NIVEIS[item['nivel_sigilo']]}).")
    if meu < 3 and item["setor_id"] != u["divisao_id"]:
        return "Este item pertence a outro setor; analistas e diretores só alteram o próprio setor."
    if meu == 1:
        return "Analistas só alteram os próprios rascunhos; aprovar e excluir cabe a diretores e ao ministro."
    return "Sem permissão para esta operação."


class Setor(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    descricao: str = Field("", max_length=1000)


class Instalacao(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    tipo: Literal["Fábrica", "Laboratório", "Depósito", "Escritório"]
    cidade: str = Field("", max_length=100)
    licenca_ambiental: str = Field("", max_length=60)
    licenca_validade: date | None = None
    setor_id: int | None = None


class Conteudo(BaseModel):
    setor_id: int | None = None  # só o Ministro escolhe; os demais gravam no próprio setor


class Produto(Conteudo):
    codigo: str = Field(min_length=1, max_length=30)
    nome: str = Field(min_length=2, max_length=150)
    cas: str = Field("", max_length=20, pattern=r"^(\d{2,7}-\d{2}-\d)?$")
    classe_risco: str = Field("", max_length=80)
    estado_fisico: Literal["Sólido", "Líquido", "Gasoso"] = "Líquido"
    unidade: Literal["kg", "L", "t", "m³"] = "kg"
    estoque: float = Field(0, ge=0)
    instalacao_id: int | None = None
    descricao: str = Field("", max_length=4000)


class Componente(BaseModel):
    nome: str = Field(min_length=1, max_length=150)
    cas: str = Field("", max_length=20)
    percentual: float = Field(gt=0, le=100)


class Formula(Conteudo):
    produto_id: int
    versao: str = Field(min_length=1, max_length=20)
    componentes: list[Componente] = Field(min_length=1, max_length=50)
    observacoes: str = Field("", max_length=4000)

    @model_validator(mode="after")
    def soma_ate_100(self):
        if sum(c.percentual for c in self.componentes) > 100.001:
            raise ValueError("a soma dos componentes passa de 100%")
        return self


class Processo(Conteudo):
    nome: str = Field(min_length=3, max_length=150)
    produto_id: int
    instalacao_id: int | None = None
    etapas: str = Field(min_length=3, max_length=8000)
    parametros: str = Field("", max_length=2000)
    epis: str = Field("", max_length=1000)


class Documento(Conteudo):
    titulo: str = Field(min_length=3, max_length=200)
    tipo: Literal["FISPQ", "Bula", "POP", "Laudo", "Licença", "Patente", "Outro"]
    produto_id: int | None = None
    versao: str = Field("1.0", min_length=1, max_length=20)
    validade: date | None = None
    conteudo: str = Field(min_length=1, max_length=20000)
    nivel_sigilo: int = Field(1, ge=1, le=3)


def sql_conteudo(tabela, colunas="", juncoes=""):
    return (f"SELECT t.*, d.nome AS setor, au.nome AS autor, ap.nome AS aprovador{colunas} FROM {tabela} t "
            "JOIN divisoes d ON d.id = t.setor_id LEFT JOIN usuarios au ON au.id = t.criado_por "
            f"LEFT JOIN usuarios ap ON ap.id = t.aprovado_por {juncoes}")


COM_PRODUTO = ", p.nome AS produto", "LEFT JOIN produtos p ON p.id = t.produto_id"
COM_INSTALACAO = ", i.nome AS instalacao", "LEFT JOIN instalacoes i ON i.id = t.instalacao_id"

# nivel: sigilo fixo do cadastro (None = escolhido em cada documento); secretos: só no detalhe.
CADASTROS = {
    "setores": {"titulo": "Setores", "tabela": "divisoes", "modelo": Setor, "estrutural": True,
                "select": "SELECT t.* FROM divisoes t"},
    "instalacoes": {"titulo": "Instalações", "tabela": "instalacoes", "modelo": Instalacao, "estrutural": True,
                    "select": "SELECT t.*, d.nome AS setor FROM instalacoes t LEFT JOIN divisoes d ON d.id = t.setor_id"},
    "produtos": {"titulo": "Produtos", "tabela": "produtos", "modelo": Produto, "nivel": 1,
                 "select": sql_conteudo("produtos", *COM_INSTALACAO)},
    "processos": {"titulo": "Processos", "tabela": "processos", "modelo": Processo, "nivel": 2,
                  "select": sql_conteudo("processos", COM_PRODUTO[0] + COM_INSTALACAO[0],
                                         COM_PRODUTO[1] + " " + COM_INSTALACAO[1])},
    "formulas": {"titulo": "Fórmulas", "tabela": "formulas", "modelo": Formula, "nivel": 3,
                 "secretos": ("componentes", "observacoes"), "select": sql_conteudo("formulas", *COM_PRODUTO)},
    "documentos": {"titulo": "Documentos", "tabela": "documentos", "modelo": Documento, "nivel": None,
                   "secretos": ("conteudo",), "select": sql_conteudo("documentos", *COM_PRODUTO)},
}


def obter(c, spec, item_id, usuario):
    c.execute(spec["select"] + " WHERE t.id = %s", (item_id,))
    item = c.fetchone()
    if item is None:
        raise HTTPException(404, "Registro não encontrado.")
    if not pode_ver(usuario, item, spec):
        raise HTTPException(403, motivo_negado(usuario, item, spec))
    return item


def resposta(usuario, item, spec, detalhe=False) -> dict:
    saida = {k: v for k, v in item.items() if detalhe or k not in spec.get("secretos", ())}
    if isinstance(saida.get("componentes"), str):
        saida["componentes"] = json.loads(saida["componentes"])
    saida.update(podeEditar=pode_editar(usuario, item, spec), podeAprovar=pode_aprovar(usuario, item, spec),
                 podeExcluir=pode_excluir(usuario, item, spec))
    return saida


def montar(spec, dados, usuario, atual=None):
    """Valores a gravar e o item resultante, para conferir a permissão antes de salvar."""
    valores = {k: (None if v == "" else v) for k, v in dados.model_dump().items()}
    if "componentes" in valores:
        valores["componentes"] = json.dumps(valores["componentes"], ensure_ascii=False)
    if spec.get("estrutural"):
        return valores, {}
    setor = valores.pop("setor_id")
    if usuario["nivel_permissao"] < 3 or setor is None:
        setor = atual["setor_id"] if atual else usuario["divisao_id"]
    if setor is None:
        raise HTTPException(422, "Seu usuário não tem setor definido; peça ao administrador para cadastrá-lo.")
    valores["setor_id"] = setor
    valores["nivel_sigilo"] = valores.get("nivel_sigilo") or spec["nivel"]
    item = dict(valores, status=atual["status"] if atual else "rascunho",
                criado_por=atual["criado_por"] if atual else usuario["id"])
    return valores, item


def registrar_cadastro(rota, spec):
    tabela, modelo, tags = spec["tabela"], spec["modelo"], [spec["titulo"]]

    @app.get(f"/api/{rota}", tags=tags)
    def listar(usuario=Depends(sessao)):
        with transacao() as c:
            c.execute(spec["select"] + " ORDER BY t.id")
            return [resposta(usuario, i, spec) for i in c.fetchall() if pode_ver(usuario, i, spec)]

    @app.get(f"/api/{rota}/{{item_id}}", tags=tags)
    def detalhar(item_id: int, usuario=Depends(sessao)):
        with transacao() as c:
            item = obter(c, spec, item_id, usuario)
            if item.get("nivel_sigilo") == 3:  # toda leitura de informação confidencial fica registrada
                evento(c, usuario, "visualizar", item_id, entidade=rota)
            return resposta(usuario, item, spec, detalhe=True)

    @app.post(f"/api/{rota}", status_code=201, tags=tags)
    def criar(dados: modelo, usuario=Depends(sessao)):
        valores, item = montar(spec, dados, usuario)
        if not pode_editar(usuario, item, spec):
            raise HTTPException(403, motivo_negado(usuario, item, spec))
        if item:
            valores.update(status="rascunho", criado_por=usuario["id"])
        with transacao() as c:
            c.execute(f"INSERT INTO {tabela} ({', '.join(valores)}) VALUES ({', '.join(['%s'] * len(valores))})",
                      tuple(valores.values()))
            novo = c.lastrowid
            evento(c, usuario, "criar", novo, entidade=rota)
            return resposta(usuario, obter(c, spec, novo, usuario), spec, detalhe=True)

    @app.put(f"/api/{rota}/{{item_id}}", tags=tags)
    def atualizar(item_id: int, dados: modelo, usuario=Depends(sessao)):
        with transacao() as c:
            atual = obter(c, spec, item_id, usuario)
            valores, item = montar(spec, dados, usuario, atual)
            for alvo in (atual, item or atual):  # pode alterar o item atual e o resultado da alteração
                if not pode_editar(usuario, alvo, spec):
                    raise HTTPException(403, motivo_negado(usuario, alvo, spec))
            c.execute(f"UPDATE {tabela} SET {', '.join(f'{k} = %s' for k in valores)} WHERE id = %s",
                      (*valores.values(), item_id))
            evento(c, usuario, "editar", item_id, entidade=rota)
            return resposta(usuario, obter(c, spec, item_id, usuario), spec, detalhe=True)

    @app.delete(f"/api/{rota}/{{item_id}}", status_code=204, tags=tags)
    def excluir(item_id: int, usuario=Depends(sessao)):
        with transacao() as c:
            item = obter(c, spec, item_id, usuario)
            if not pode_excluir(usuario, item, spec):
                raise HTTPException(403, motivo_negado(usuario, item, spec))
            c.execute(f"DELETE FROM {tabela} WHERE id = %s", (item_id,))
            evento(c, usuario, "excluir", item_id, entidade=rota)

    if spec.get("estrutural"):
        return

    @app.post(f"/api/{rota}/{{item_id}}/aprovar", tags=tags)
    def aprovar(item_id: int, usuario=Depends(sessao)):
        with transacao() as c:
            item = obter(c, spec, item_id, usuario)
            if item["status"] == "aprovado":
                raise HTTPException(409, "Este item já está aprovado.")
            if not pode_aprovar(usuario, item, spec):
                raise HTTPException(403, motivo_negado(usuario, item, spec))
            c.execute(f"UPDATE {tabela} SET status = 'aprovado', aprovado_por = %s, aprovado_em = NOW() WHERE id = %s",
                      (usuario["id"], item_id))
            evento(c, usuario, "aprovar", item_id, entidade=rota)
            return resposta(usuario, obter(c, spec, item_id, usuario), spec, detalhe=True)


for _rota, _spec in CADASTROS.items():
    registrar_cadastro(_rota, _spec)


@app.get("/api/permissoes")
def minhas_permissoes(usuario=Depends(sessao)):
    """Matriz do que o usuário logado pode fazer, calculada pelas mesmas regras usadas nas rotas."""
    regras = []
    tem_setor = usuario["divisao_id"] is not None or usuario["nivel_permissao"] == 3
    for rota, spec in CADASTROS.items():
        niveis = [None] if spec.get("estrutural") else ([spec["nivel"]] if spec["nivel"] else [1, 2, 3])
        for nivel in niveis:
            proprio = {"setor_id": usuario["divisao_id"], "nivel_sigilo": nivel, "status": "aprovado", "criado_por": None}
            outro_setor = dict(proprio, setor_id=0)
            regras.append({
                "rota": rota, "cadastro": spec["titulo"], "nivel": nivel,
                "verProprioSetor": pode_ver(usuario, proprio, spec),
                "verOutrosSetores": pode_ver(usuario, outro_setor, spec),
                "criar": tem_setor and pode_editar(usuario, dict(proprio, status="rascunho", criado_por=usuario["id"]), spec),
                "editarAprovado": pode_editar(usuario, proprio, spec),
                "aprovar": pode_aprovar(usuario, dict(proprio, status="rascunho", criado_por=0), spec),
                "excluir": pode_excluir(usuario, proprio, spec),
            })
    return {"perfil": PERFIS[usuario["nivel_permissao"]], "nivel": usuario["nivel_permissao"],
            "setor": usuario["divisao"], "administrador": usuario["papel"] == "administrador", "regras": regras}


# ---------- Linha de comando ----------

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--limiar", type=float, default=0.5)
    parser.add_argument("--margem", type=float, default=0.05)
    parser.add_argument("--porta", type=int, default=8000)
    comandos = parser.add_subparsers(dest="comando")
    cadastro = comandos.add_parser("cadastrar-rosto", help="Cadastra o rosto por fotos; --admin cria o primeiro administrador.")
    cadastro.add_argument("--usuario", type=int, required=True, help="id da tabela usuarios")
    cadastro.add_argument("--admin", action="store_true")
    cadastro.add_argument("fotos", nargs="+")
    args = parser.parse_args(argv)
    try:
        motor(args.limiar, args.margem)
        if args.comando == "cadastrar-rosto":
            for foto in args.fotos:
                with transacao() as c:
                    ordem = cadastrar_amostra(c, args.usuario, ler_imagem(foto))
                print(f"{foto}: amostra {ordem} cadastrada.")
            if args.admin:
                with transacao() as c:
                    definir_conta(c, args.usuario, "administrador", 1)
                print(f"Usuário {args.usuario} agora é administrador.")
            return 0
        with transacao() as c:
            configuracao_id(c)  # valida a conexão antes de abrir a porta
    except HTTPException as exc:
        print(f"Erro: {exc.detail}", file=sys.stderr)
        return 2
    except (ErroAquisicao, ValueError, OSError, pymysql.err.Error, cv2.error) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=args.porta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
