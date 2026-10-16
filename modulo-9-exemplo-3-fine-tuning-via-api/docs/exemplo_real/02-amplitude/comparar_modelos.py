"""Compara o endpoint fine-tunado com o gemini-2.5-flash base no JSONL da aula.

A amostra sai do próprio dataset de treino (não há split de teste). Temperatura 0.
"""

import json
import os
import subprocess
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
DATASET = RAIZ / "materiais_aula" / "dataset-treinado.jsonl"
SAIDA = Path(__file__).resolve().parents[1] / "03-evidencia" / "comparacao.json"
REGIAO = "us-central1"
PROJETO_NUM = "1056438185728"
ENDPOINT = "4438733389134036992"
BASE = "gemini-2.5-flash"
GCLOUD = Path.home() / "google-cloud-sdk" / "bin" / "gcloud.cmd"
N_POR_DOMINIO = 10


def token():
    env = os.environ.copy()
    pem = Path.home() / "google-cloud-sdk" / "trust-bundle.pem"
    if pem.is_file():
        env["CLOUDSDK_CORE_CUSTOM_CA_CERTS_FILE"] = str(pem)
        env["SSL_CERT_FILE"] = str(pem)
        env["REQUESTS_CA_BUNDLE"] = str(pem)
    bruto = subprocess.check_output([str(GCLOUD), "auth", "print-access-token"], text=True, env=env)
    return bruto.strip()


def gerar(url, texto, acesso):
    corpo = {
        "contents": [{"role": "user", "parts": [{"text": texto}]}],
        "generationConfig": {"temperature": 0},
    }
    pedido = urllib.request.Request(
        url,
        data=json.dumps(corpo).encode(),
        method="POST",
        headers={"Authorization": f"Bearer {acesso}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(pedido, timeout=120) as resposta:
        return json.loads(resposta.read().decode())


def texto_da_resposta(payload):
    candidatos = payload.get("candidates") or []
    if not candidatos:
        return ""
    partes = candidatos[0].get("content", {}).get("parts") or []
    return "".join(parte.get("text", "") for parte in partes).strip()


def json_da_resposta(bruto):
    texto = bruto.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[-1]
        texto = texto.rsplit("```", 1)[0]
    inicio = texto.find("{")
    fim = texto.rfind("}")
    if inicio < 0 or fim < inicio:
        raise ValueError("resposta sem objeto JSON")
    return json.loads(texto[inicio : fim + 1])


def norm(valor):
    if isinstance(valor, str):
        return " ".join(valor.split()).casefold()
    if isinstance(valor, (int, float)):
        return round(float(valor), 2)
    return valor


def amostra(linhas):
    auto, saude = [], []
    for linha in linhas:
        exemplo = json.loads(linha)
        texto = exemplo["contents"][0]["parts"][0]["text"]
        esperado = json.loads(exemplo["contents"][1]["parts"][0]["text"])
        item = {"texto": texto, "esperado": esperado}
        if "benefici" in texto.lower():
            saude.append(item)
        else:
            auto.append(item)
    passo_auto = max(1, len(auto) // N_POR_DOMINIO)
    passo_saude = max(1, len(saude) // N_POR_DOMINIO)
    escolhidos = [("auto", item) for item in auto[::passo_auto][:N_POR_DOMINIO]]
    escolhidos += [("saude", item) for item in saude[::passo_saude][:N_POR_DOMINIO]]
    return escolhidos


def avaliar(nome, url, escolhidos, acesso):
    acertos = 0
    campos_ok = 0
    campos_total = 0
    falhas = []
    for dominio, item in escolhidos:
        try:
            bruto = texto_da_resposta(gerar(url, item["texto"], acesso))
            previsto = json_da_resposta(bruto)
        except Exception as erro:  # noqa: BLE001
            falhas.append({"dominio": dominio, "erro": str(erro)[:240]})
            campos_total += len(item["esperado"])
            continue
        igual = True
        for chave, valor in item["esperado"].items():
            campos_total += 1
            if norm(previsto.get(chave)) == norm(valor):
                campos_ok += 1
            else:
                igual = False
        if igual and set(previsto) == set(item["esperado"]):
            acertos += 1
        else:
            falhas.append({
                "dominio": dominio,
                "esperado": item["esperado"],
                "previsto": previsto,
            })
    return {
        "modelo": nome,
        "exemplos": len(escolhidos),
        "json_completo_ok": acertos,
        "campos_ok": campos_ok,
        "campos_total": campos_total,
        "falhas": falhas[:8],
    }


def main():
    linhas = [linha for linha in DATASET.read_text(encoding="utf-8").splitlines() if linha.strip()]
    escolhidos = amostra(linhas)
    acesso = token()
    base_url = (
        f"https://{REGIAO}-aiplatform.googleapis.com/v1/projects/{PROJETO_NUM}"
        f"/locations/{REGIAO}/publishers/google/models/{BASE}:generateContent"
    )
    tuned_url = (
        f"https://{REGIAO}-aiplatform.googleapis.com/v1/projects/{PROJETO_NUM}"
        f"/locations/{REGIAO}/endpoints/{ENDPOINT}:generateContent"
    )
    relatorio = {
        "amostra": {"auto": N_POR_DOMINIO, "saude": N_POR_DOMINIO, "fonte": "dataset-treinado.jsonl"},
        "base": avaliar(BASE, base_url, escolhidos, acesso),
        "fine_tunado": avaliar(f"endpoint/{ENDPOINT}", tuned_url, escolhidos, acesso),
    }
    SAIDA.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")
    for chave in ("base", "fine_tunado"):
        item = relatorio[chave]
        print(
            f"{item['modelo']}: json {item['json_completo_ok']}/{item['exemplos']}"
            f" campos {item['campos_ok']}/{item['campos_total']} falhas {len(item['falhas'])}"
        )


if __name__ == "__main__":
    main()
