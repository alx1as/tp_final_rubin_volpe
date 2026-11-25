# Compilación reproducible del frontend con el lockfile existente.
FROM node:24-bookworm-slim AS frontend
WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.13-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 SESSION_COOKIE_SECURE=true
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
COPY --from=frontend /build/frontend/dist /app/frontend/dist
RUN useradd --create-home trama
USER trama
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn app.production:create_production_app --factory --host 0.0.0.0 --port ${PORT:-8000}"]
