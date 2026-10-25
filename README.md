# Instalación y ejecución

## Requisitos

- Node.js 24 o superior y npm.
- Python 3.13.
- PostgreSQL 16 o superior, con las herramientas `psql` y `createdb` disponibles.

## Dependencias

Ejecutar desde la raíz del repositorio.

**Windows (PowerShell)**

```powershell
npm ci --prefix frontend
py -3.13 -m venv backend/.venv
.\backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
```

**Linux / macOS**

```bash
npm ci --prefix frontend
python3.13 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
```

## PostgreSQL

Crear la base e instalar el esquema **una sola vez** sobre una base vacía, con un usuario de PostgreSQL que tenga los permisos correspondientes:

```bash
createdb -h localhost -U USUARIO seguimiento
psql -h localhost -U USUARIO -d seguimiento -v ON_ERROR_STOP=1 -f backend/init.sql
```

Configurar `DATABASE_URL` en `backend/.env` con las credenciales locales:

```dotenv
DATABASE_URL=postgresql+psycopg://USUARIO:CONTRASEÑA@localhost:5432/seguimiento
ALLOWED_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
SESSION_COOKIE_SECURE=false
```

En instalaciones existentes, conservar la base y el archivo `.env`; no volver a ejecutar `backend/init.sql`.

## Ejecución

```bash
npm run dev
```

- Aplicación: http://localhost:5173
- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- Salud de PostgreSQL: http://127.0.0.1:8000/api/salud

El comando inicia frontend (Vite) y backend (FastAPI). Para detenerlos, `Ctrl+C`.
