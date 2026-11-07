# IRIS — APS PIVC

Sistema de acesso por reconhecimento facial para uma empresa química.
Front-end em React, API em Python (FastAPI + OpenCV) e banco MySQL.

## Rodar

Com tudo instalado, abra `iniciar.bat`. Ele liga o MySQL, a API e o site
(http://localhost:5173).

Primeira instalação:

```powershell
# banco
mysql -u root -p --default-character-set=utf8mb4 < "sistema biometria APS.sql"
mysql -u root -p --default-character-set=utf8mb4 < migracao_empresa_quimica.sql

# Python
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m processamento_imagens preparar-modelos

# primeiro administrador (id da tabela usuarios + fotos do rosto)
.\.venv\Scripts\python.exe api.py cadastrar-rosto --usuario 6 --admin foto1.jpg foto2.jpg foto3.jpg

# site
cd frontend
npm install
Set-Content .env "VITE_DEMO_MODE=false`nVITE_API_URL=http://localhost:8000/api"
```

Se o MySQL tiver senha, defina `$env:APS_DB_PASSWORD` antes de rodar a API.

## Perfis

| Perfil | Nível | Vê | Aprova e exclui |
|---|---|---|---|
| Analista | 1 | Itens internos | — |
| Diretor | 2 | Internos e restritos do próprio setor | No próprio setor |
| Ministro | 3 | Tudo, inclusive fórmulas | Tudo |

Administrador é uma função à parte: cuida de usuários, setores, instalações e rostos.
As regras estão em `pode_ver`, `pode_editar` e `pode_aprovar`, no `api.py`.

## Pastas

| Pasta | Conteúdo |
|---|---|
| `api.py` | API, login pelo rosto e regras de acesso |
| `processamento_imagens/` | Captura, qualidade e alinhamento do rosto (YuNet) |
| `Reconhecimento Facial/` | Comparação dos rostos (SFace) |
| `frontend/` | Site |
| `tests/` | Testes |
| `docs/` | Requisitos da APS |

## Testes

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

Com `$env:APS_DB_TESTE = "1"` também roda o teste da API contra o MySQL, num banco
temporário. O relatório de código para o Teams sai com `python scripts/relatorio_codigo.py`.
