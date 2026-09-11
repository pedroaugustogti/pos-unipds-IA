# Guardião Família — QA scenario worker (full stack: emulator + Appium + Python)
# Uso: docker build -t guardiao-qa-scenario-worker:latest -f docker/qa-scenario-worker/Dockerfile .

FROM budtmo/docker-android:emulator_11.0

USER root

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:/usr/local/bin:$PATH \
    PYTHONPATH=/workspace \
    GF_STATUS_DIR=/status \
    GF_APPIUM_EVIDENCE_DIR=/evidence

RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 \
      python3-pip \
      python3-venv \
      python3-full \
      curl \
      ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/python3 /usr/local/bin/python \
    && python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip

# Appium (se a base não trouxer)
RUN if ! command -v appium >/dev/null 2>&1; then \
      curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
      && apt-get install -y --no-install-recommends nodejs \
      && npm install -g appium@2 \
      && appium driver install uiautomator2 || true; \
    fi

WORKDIR /workspace

COPY docker/qa-scenario-worker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

VOLUME ["/status", "/evidence", "/ctx"]

ENTRYPOINT ["/entrypoint.sh"]
