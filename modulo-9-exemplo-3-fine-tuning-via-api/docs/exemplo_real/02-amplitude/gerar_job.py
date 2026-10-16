"""Dry-run do fine-tuning Vertex com o JSONL da Amplitude já preparado na aula.

Não cria job enquanto a variável CONFIRMAR não for exatamente "true".
O dataset é materiais_aula/dataset-treinado.jsonl (schema contents/role/parts).
"""

import hashlib
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

RAIZ_EX3 = Path(__file__).resolve().parents[3]
DATASET = RAIZ_EX3 / "materiais_aula" / "dataset-treinado.jsonl"
HASH_DO_CARD = "f6eb8f99c30e5ecc1c3ec5f293ba831bccfde59b7cc12070ad03169ab91b52ed"
EXEMPLOS_ESPERADOS = 200
REGIAO = "us-central1"
PROJECT_ID = "fine-tuning-via-api"
BUCKET = "fine-tuning-via-api-amplitude"
OBJETO = "m3-amplitude-auto-saude-200.jsonl"
URI_PADRAO = f"gs://{BUCKET}/{OBJETO}"
FAIXAS = {
    "epoch_count": (1, 20),
    "learning_rate_multiplier": (0.1, 10),
}


def hiperparametros():
    epocas = int(os.environ.get("EPOCH_COUNT", "3"))
    taxa = float(os.environ.get("LEARNING_RATE_MULTIPLIER", "5"))
    erros = []
    minimo, maximo = FAIXAS["epoch_count"]
    if not minimo <= epocas <= maximo:
        erros.append(f"epoch_count fora da faixa {minimo}-{maximo}: {epocas}")
    minimo, maximo = FAIXAS["learning_rate_multiplier"]
    if not minimo <= taxa <= maximo:
        erros.append(f"learning_rate_multiplier fora da faixa {minimo}-{maximo}: {taxa}")
    if erros:
        raise SystemExit("Hiperparâmetro inválido:\n  " + "\n  ".join(erros))
    return epocas, taxa


def carregar_dataset():
    if not DATASET.is_file():
        raise SystemExit(f"dataset ausente: {DATASET}")
    linhas = DATASET.read_text(encoding="utf-8").splitlines()
    linhas = [linha for linha in linhas if linha.strip()]
    if len(linhas) != EXEMPLOS_ESPERADOS:
        raise SystemExit(f"esperados {EXEMPLOS_ESPERADOS} exemplos, encontrados {len(linhas)}")
    auto = saude = 0
    for indice, linha in enumerate(linhas, start=1):
        exemplo = json.loads(linha)
        conteudos = exemplo.get("contents") or []
        papeis = [turno.get("role") for turno in conteudos]
        if papeis != ["user", "model"]:
            raise SystemExit(f"linha {indice} sem o par user/model: {papeis}")
        texto = conteudos[0]["parts"][0]["text"]
        if "benefici" in texto.lower():
            saude += 1
        else:
            auto += 1
    return linhas, auto, saude


def corpo_do_job(uri, epocas, taxa):
    return {
        "baseModel": os.environ.get("BASE_MODEL", "gemini-2.5-flash"),
        "tunedModelDisplayName": os.environ.get("DISPLAY_NAME", "amplitude-auto-saude-m3-200"),
        "supervisedTuningSpec": {
            "trainingDatasetUri": uri,
            "hyperParameters": {
                "epochCount": epocas,
                "learningRateMultiplier": taxa,
            },
        },
    }


def criar_job(corpo):
    projeto = os.environ.get("GCP_PROJECT_ID", PROJECT_ID)
    token = subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True).strip()
    url = (
        f"https://{REGIAO}-aiplatform.googleapis.com/v1/projects/{projeto}"
        f"/locations/{REGIAO}/tuningJobs"
    )
    pedido = urllib.request.Request(
        url,
        data=json.dumps(corpo).encode(),
        method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(pedido) as resposta:
        return json.loads(resposta.read().decode())


def main():
    epocas, taxa = hiperparametros()
    linhas, auto, saude = carregar_dataset()
    digest = hashlib.sha256(DATASET.read_bytes()).hexdigest()
    projeto = os.environ.get("GCP_PROJECT_ID", PROJECT_ID)
    uri = os.environ.get("GCS_DATASET_URI", URI_PADRAO)
    corpo = corpo_do_job(uri, epocas, taxa)

    print(f"projeto: {projeto}")
    print(f"dataset: {DATASET}")
    print(f"exemplos: {len(linhas)} (auto={auto}, saude={saude})")
    print(f"sha256: {digest}")
    if digest == HASH_DO_CARD:
        print("hash igual ao model card publicado do curso")
    else:
        print("hash diferente do model card publicado; confira se o JSONL foi alterado")
    print(f"uri do dataset: {uri}")
    print(f"criar bucket: gsutil mb -l {REGIAO} -p {projeto} gs://{BUCKET}/")
    print("corpo do job:")
    print(json.dumps(corpo, indent=2, ensure_ascii=False))

    if os.environ.get("CONFIRMAR") != "true":
        print("dry-run ok. Nenhum upload e nenhum job. Para criar, defina CONFIRMAR=true.")
        return

    if not uri.startswith("gs://") or not uri.endswith(".jsonl"):
        raise SystemExit("GCS_DATASET_URI precisa ser gs://...jsonl")

    subprocess.run(f'gsutil cp "{DATASET}" "{uri}"', shell=True, check=True)
    job = criar_job(corpo)
    print(f"job criado: {job.get('name')}")
    print("Guarde esse nome em TUNING_JOB_NAME para o acompanhamento da aula.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as erro:
        sys.exit(erro.returncode or 1)
