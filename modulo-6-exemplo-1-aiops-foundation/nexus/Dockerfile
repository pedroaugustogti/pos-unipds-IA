# Módulo 13.1 — Nexus-Bot: artefato de IA imutável (python:3.12-slim)
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV CREWAI_TRACING_ENABLED=false
ENV NEXUS_IN_DOCKER=1
ENV OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# Projeto Final (Lab 12) — orquestração hierárquica Game Day
CMD ["python", "labs/modulo12_projeto_final.py"]
