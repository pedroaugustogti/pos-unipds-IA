"""Valida memory-eval (com vs sem memoria) e gera relatorio."""

import json
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

RUNTIME = Path(__file__).resolve().parent / "runtime"
EXEMPLO = Path(__file__).resolve().parent
EX12 = EXEMPLO.parent / "modulo-4-exemplo-12-embeddings-reflexao-evolutiva"
sys.path.insert(0, str(RUNTIME))

from memory_eval import executar_memory_eval  # noqa: E402

SAIDA = EXEMPLO / "evals" / "resultados"
AGENTE = EXEMPLO / "monitor-agent"
SUITE = EXEMPLO / "evals" / "suites" / "memory_impact_eval.yaml"
MAX_CASOS = int(os.environ.get("MEMORY_EVAL_MAX_CASOS", "2"))


def _garantir_env() -> None:
    env_dest = RUNTIME / ".env"
    if env_dest.exists():
        return
    env_src = EX12 / "runtime" / ".env"
    if env_src.exists():
        shutil.copy(env_src, env_dest)
        print(f"[setup] .env copiado de {env_src.parent.name}")
    elif (RUNTIME / ".env.example").exists():
        shutil.copy(RUNTIME / ".env.example", env_dest)
        print("[setup] .env criado a partir de .env.example")


def main() -> None:
    from dotenv import load_dotenv

    _garantir_env()
    load_dotenv(RUNTIME / ".env")
    os.environ.setdefault("RUNTIME_PLANEJADOR", "auto")

    SAIDA.mkdir(parents=True, exist_ok=True)
    inicio = time.time()

    resultado = executar_memory_eval(
        caminho_agente=str(AGENTE),
        caminho_suite=str(SUITE),
        max_casos=MAX_CASOS,
    )

    metricas = resultado.get("metricas_agregadas", {})
    status = resultado.get("status", {})
    lesson_ok = metricas.get("lesson_quality", 0) >= 0.4
    decision_ok = metricas.get("decision_improvement", 0) >= 0
    pass_count = sum(1 for s in status.values() if s == "PASS")

    relatorio = {
        "timestamp": datetime.now().isoformat(),
        "max_casos": MAX_CASOS,
        "metricas_agregadas": metricas,
        "status": status,
        "pass_count": pass_count,
        "fail_count": sum(1 for s in status.values() if s == "FAIL"),
        "lesson_quality_ok": lesson_ok,
        "decision_improvement_ok": decision_ok,
        "arquivo_relatorio": resultado.get("arquivo_relatorio"),
        "duracao_segundos": round(time.time() - inicio, 2),
        "sucesso": bool(resultado.get("arquivo_relatorio")) and lesson_ok,
    }

    json_path = SAIDA / "relatorio_execucao_memory.json"
    json_path.write_text(json.dumps(relatorio, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# Relatorio de validacao — Evals de Memoria",
        "",
        f"- **Data:** {relatorio['timestamp']}",
        f"- **Casos:** {MAX_CASOS}",
        f"- **Duracao:** {relatorio['duracao_segundos']}s",
        f"- **Sucesso:** {'SIM' if relatorio['sucesso'] else 'NAO'}",
        "",
        "## Metricas",
        "",
    ]
    for k, v in metricas.items():
        st = status.get(k, "N/A")
        md.append(f"- **{k}:** {v} ({st})")
    md.append("")
    md.append(f"Relatorio completo: `{resultado.get('arquivo_relatorio', '')}`")
    (SAIDA / "RELATORIO_EXECUCAO_MEMORY.md").write_text("\n".join(md), encoding="utf-8")

    print(f"\n=== Validacao: {SAIDA} ===")
    print(f"Sucesso: {relatorio['sucesso']}")
    print(f"PASS: {pass_count} | lesson_quality: {metricas.get('lesson_quality')}")


if __name__ == "__main__":
    main()
