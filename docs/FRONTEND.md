# IRIS APS — Front-end React v2.0

Front-end completo para a APS UNIP 2026/2: identificação/autenticação biométrica, **duas áreas separadas** (usuário e administrador), interface escura premium baseada na referência visual apresentada e serviços HTTP preparados para API Python. **Não inclui Python, reconhecimento biométrico real ou banco de dados.**

## Como abrir no VS Code

Requisitos: Node.js 20.19+ (ou 22+), npm e navegador recente.

```bash
npm install
cp .env.example .env
npm run dev
```

No PowerShell do Windows, substitua `cp` por `Copy-Item .env.example .env`.

Abra a URL exibida pelo Vite (normalmente **http://localhost:5173**). Para gerar distribuição: `npm run build`.

> Dependências são baixadas pelo `npm install`; a pasta node_modules não acompanha o ZIP.

## Demonstração sem Python

Com `VITE_DEMO_MODE=true`:

| Perfil | E-mail | Senha | Área inicial |
| --- | --- | --- | --- |
| Administrador | `admin@iris.demo` | `Admin@123` | `/admin` |
| Usuário | `usuario@iris.demo` | `User@123` | `/usuario` |

O modo demo possui cadastros fictícios, filtros, edição/exclusão, webcam, captura, histórico e CSV. **NÃO faz reconhecimento biométrico**: o botão “Simular verificação” compara o nível pedido com o nível da conta demonstrativa logada. Ele não usa a imagem para autenticar; a interface deixa isso visível.

Usuários e histórico demo ficam apenas no `localStorage` do navegador (dados de cadastro fictícios, **sem imagens ou templates faciais**). A sessão demonstrativa fica no `sessionStorage`. Credenciais demo servem somente para apresentação e **não oferecem segurança real**. Limpe dados em Configurações. A câmera não começa automaticamente: exige consentimento do navegador, localhost ou HTTPS. Imagens capturadas ficam somente na memória da aba e podem ser descartadas.

## Páginas

**Usuário**
- `/usuario`: início, níveis permitidos e componente de autenticação.
- `/usuario/reconhecimento`: webcam, captura/upload de imagem, escolha de nível, resultado da API ou simulação claramente identificada.
- `/usuario/perfil`: dados associados à conta.

**Administrador**
- `/admin`: KPIs, níveis, tabela de histórico, atalhos.
- `/admin/usuarios`: lista, busca, filtros, criação, edição, exclusão de usuários.
- `/admin/cadastro`: captura e envio da referência facial selecionando usuário.
- `/admin/historico`: tabela, filtros e exportação CSV.
- `/admin/configuracoes`: status dos módulos e restauração dos dados demo.

As rotas são restritas **visualmente no React**. Em produção, o servidor Python é responsável por autenticar, autorizar cada endpoint e controlar os níveis; não confie no papel/nível informado pelo cliente.

## Preparar integração Python

A configuração fica em `.env`:

```dotenv
VITE_DEMO_MODE=false
VITE_API_URL=http://localhost:8000/api
```

Os contratos abaixo são **propostas**, não APIs implementadas. Alinhe com as pessoas do Python antes de conectar. Front-end **nunca** acessa MySQL diretamente.

| Método e rota sugerida | Entrada | Saída esperada |
| --- | --- | --- |
| `POST /auth/login` | JSON `{ "email": "...", "password": "..." }` | `{ "user": { id,name,email,role,level,job,department,status }, "token": "..." }` |
| `GET /users` | — | `User[]` |
| `POST /users` | JSON `User` | `User` |
| `PATCH /users/:id` | JSON alteração | `User` |
| `DELETE /users/:id` | — | HTTP 204 |
| `POST /recognitions` | `multipart/form-data`, `image` (JPG), `requested_level` (1/2/3) | `{ "identified": true, "authorized": true, "user": { ... }, "confidence": 0.92, "reason": "...", "timestamp": "..." }` |
| `GET /access-logs` | — | `[{ "id":"...", "date":"ISO", "user":"...", "level": 1, "allowed": true, "source":"api" }]` |
| `POST /face-enrollments` | `multipart/form-data`, `user_id`, `image` | `{ "success": true }` |

Ficam centralizados em `src/services/`:
- `api.js`: requisições e URL base.
- `auth.js`: autenticação.
- `users.js`: gestão de usuários.
- `recognition.js`: reconhecimento, cadastro facial e histórico.

**Autorização:** Recomenda-se o Python retornar o usuário/identidade biométrica realmente identificados e decidir as permissões no servidor; a sessão React não deve ser usada como prova da identidade facial. Para produção, avaliar cookies HttpOnly seguros, CSRF/CORS restritos, proteção de endpoints, liveness/anti-spoof, logs/auditoria, consentimento e LGPD. O projeto é uma interface acadêmica, não um produto de segurança pronto para uso.

## Organização de arquivos

```text
src/
├── App.jsx                 # rotas protegidas
├── main.jsx
├── components/
│   ├── AccessLevelSelect.jsx
│   ├── AccessTable.jsx
│   ├── AppShell.jsx
│   ├── CameraPanel.jsx
│   └── UI.jsx
├── contexts/AuthContext.jsx
├── data/demo.js           # dados fictícios
├── pages/
│   ├── Login.jsx
│   ├── Dashboard.jsx
│   ├── Recognize.jsx
│   ├── UsersPage.jsx
│   ├── Enrollment.jsx
│   ├── HistoryPage.jsx
│   ├── Profile.jsx
│   └── SettingsPage.jsx
├── services/
│   ├── api.js
│   ├── auth.js
│   ├── users.js
│   └── recognition.js
├── styles/main.css
└── utils/format.js
```

## Limitações e próximos passos do grupo

1. Conectar os endpoints da equipe Python e validar o formato real das respostas (contratos acima são provisórios).
2. Garantir que cadastro facial, detecção, extração de características e reconhecimento ocorram no Python com validações de qualidade e consentimento.
3. Usar autenticação real da API com níveis de administrador separados das permissões 1/2/3 do cofre.
4. Realizar testes de integração entre React, Python e banco, incluindo erros de câmera/rede/usuário desconhecido.

**Nota de verificação:** o ZIP foi gerado com os arquivos-fonte. O ambiente de elaboração estava sem acesso ao registro npm; por isso `npm install` e `vite build` dependem da execução em uma máquina com internet. A sintaxe JSX pode ser conferida independentemente com o TypeScript instalado no ambiente.
