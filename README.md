# TRAMA — Seguimiento psicopedagógico

Trabajo Final Integrador de la Tecnicatura Universitaria en Programación, Universidad Tecnológica Nacional. Grupo 157 — Alexia Rubin y María Victoria Volpe.

TRAMA centraliza el seguimiento de pacientes por profesional: admisión, trayectoria escolar, equipo interviniente, objetivos, sesiones, observaciones, evidencias, cronología e informes. Incorpora transcripción de audio y asistencia de IA para organizar registros y redactar borradores, siempre sujetos a revisión profesional. Se utilizan datos ficticios para las pruebas y la demostración académica.

## Arquitectura y documentación

- Frontend: React, TypeScript y Vite. Módulos organizados por dominio, servicios HTTP y estado de edición compartido.
- Backend: FastAPI, SQLModel y PostgreSQL. Autenticación por sesiones opacas con cookie HttpOnly, autorización por pertenencia y registro transaccional de sesiones y observaciones.
- Integraciones: Groq para transcripción, organización de registros y borradores de informes.
- [Propuesta y alcance](PropuestadeProyecto.md)
- [Frontend](frontend/README.md) · [Backend](backend/README.md) · [Contratos de API](backend/CONTRATOS.md)
- [Organización asistida](docs/ORGANIZACION_IA.md) · [Registro unificado](docs/REGISTRO_UNIFICADO_IA.md)
- [Validación y pruebas](docs/VALIDACION.md)

## Instalación y ejecución

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


## Publicación

El `Dockerfile` construye el frontend y publica los archivos estáticos y la API bajo un mismo origen. No requiere cambiar rutas, CORS ni la política de cookies para comunicar dos sitios distintos.

1. Crear una base PostgreSQL vacía e instalar `backend/init.sql` una sola vez (en una base existente, aplicar únicamente las migraciones pendientes).
2. Configurar el servicio Docker desde la raíz del repositorio. Definir `DATABASE_URL` con el esquema `postgresql+psycopg://`, `ALLOWED_ORIGINS` como lista JSON con el origen HTTPS público, `SESSION_COOKIE_SECURE=true`, y `GROQ_API_KEY` si se utiliza IA. No publicar secretos.
3. La plataforma debe terminar HTTPS y redirigir al puerto del contenedor (`PORT`, por defecto 8000). Verificar `/api/salud`, acceso, micrófono e informes desde la URL pública.

Para construir localmente (si Docker está instalado): `docker build -t trama .`. Para una comprobación por HTTP local, se puede ejecutar con `SESSION_COOKIE_SECURE=false` y el origen `http://localhost:8000`; en un despliegue HTTPS debe quedar en `true`.

La configuración de publicación no sustituye la inicialización de la base ni acredita un despliegue ya activo. La URL pública, el informe final y el video se incorporarán a este README al completar la entrega.
