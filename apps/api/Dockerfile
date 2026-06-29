FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml ./
COPY healthos_api ./healthos_api
COPY alembic.ini ./alembic.ini
COPY migrations ./migrations
RUN pip install --no-cache-dir -e .

CMD ["uvicorn", "healthos_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
