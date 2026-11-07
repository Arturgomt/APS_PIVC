# IRIS — site

```powershell
npm install
npm run dev
```

Abra http://localhost:5173.

O arquivo `.env` escolhe o modo:

```dotenv
VITE_DEMO_MODE=false
VITE_API_URL=http://localhost:8000/api
```

Com `VITE_DEMO_MODE=true` o site roda sem a API, com dados de exemplo
(login `admin@iris.demo` / `Admin@123` ou `usuario@iris.demo` / `User@123`).
