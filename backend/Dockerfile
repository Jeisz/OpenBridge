# Contexto de construcción: raíz del repositorio.
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY backend/pyproject.toml /tmp/backend/pyproject.toml
RUN pip install --no-cache-dir /tmp/backend
COPY backend /app/backend
COPY shared /app/shared
RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
