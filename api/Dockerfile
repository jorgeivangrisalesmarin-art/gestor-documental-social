FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv

COPY pyproject.toml ./
RUN pip install --no-cache-dir . && pip install --no-cache-dir "uvicorn[standard]"

COPY app/ app/
RUN useradd -m appuser
USER appuser

EXPOSE 8080
# Cloud Run inyecta $PORT; uvicorn fijo a 8080 con --port
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
