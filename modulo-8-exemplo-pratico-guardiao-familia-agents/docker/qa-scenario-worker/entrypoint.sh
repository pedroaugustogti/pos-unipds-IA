#!/usr/bin/env bash
# Entrypoint do worker de cenário QA (container full-stack).
set -euo pipefail

mkdir -p "${GF_STATUS_DIR:-/status}" "${GF_APPIUM_EVIDENCE_DIR:-/evidence}"

export PYTHONPATH="${PYTHONPATH:-/workspace}"
export GF_SKIP_BUILD="${GF_SKIP_BUILD:-1}"

if [[ ! -f "${GF_ACTUATION_CONTEXT_PATH:-}" ]]; then
  echo "GF_ACTUATION_CONTEXT_PATH missing or not a file: ${GF_ACTUATION_CONTEXT_PATH:-}" >&2
  exit 2
fi

if [[ -z "${GF_SCENARIO_ID:-}" || -z "${GF_TASK_ID:-}" ]]; then
  echo "GF_TASK_ID and GF_SCENARIO_ID are required" >&2
  exit 2
fi

# Emulador: a imagem budtmo costuma expor scripts próprios; se existirem, dispare em background.
if command -v /home/androidusr/docker-android/mixins/scripts/run.sh >/dev/null 2>&1; then
  /home/androidusr/docker-android/mixins/scripts/run.sh >/tmp/emulator-boot.log 2>&1 &
elif command -v emulator >/dev/null 2>&1; then
  echo "emulator binary present — host image should boot AVD via its supervisor" >&2
fi

cd /workspace

# deps do host montado (venv da imagem; trusted-host p/ SSL corporativo)
if [[ -f /workspace/agents/00-runtime/requirements.txt ]]; then
  pip install --quiet --disable-pip-version-check \
    --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    -r /workspace/agents/00-runtime/requirements.txt || true
fi

exec python -m lib.mobile.qa_scenario_worker
