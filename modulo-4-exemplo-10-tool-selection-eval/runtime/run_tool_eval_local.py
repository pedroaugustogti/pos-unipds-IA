"""Runner local do tool-eval com saida ASCII-safe (Windows)."""
import json
import os
import sys
import time
from pathlib import Path

# forcar UTF-8 no stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from tool_eval import gerar_relatorio_tool_eval, rodar_tool_eval

ARQUITETURAS = ["padrao", "react", "plan_execute", "reflect"]
AGENTE = "../monitor-agent"
SUITE_MOCK = "../evals/suites/tool_selection.yaml"
SUITE_LLM = "../evals/suites/tool_selection_llm.yaml"
RESULTADOS = Path("../evals/resultados")
CASOS_RAPIDO = ["ts-001", "ts-006", "ts-008"]


def _resolver_suite() -> str:
    usar_llm = "--llm" in sys.argv or os.environ.get("RUNTIME_PLANEJADOR", "").lower() == "llm"
    return SUITE_LLM if usar_llm else SUITE_MOCK


def _resolver_timeout_total() -> float | None:
    if "--timeout" in sys.argv:
        idx = sys.argv.index("--timeout")
        return float(sys.argv[idx + 1])
    return None


def _resolver_casos() -> list[str] | None:
    if "--rapido" in sys.argv:
        return CASOS_RAPIDO
    if "--casos" in sys.argv:
        idx = sys.argv.index("--casos")
        return [c.strip() for c in sys.argv[idx + 1].split(",") if c.strip()]
    return None


def main():
    comparar = "--comparar" in sys.argv
    rapido = "--rapido" in sys.argv
    arquiteturas = ARQUITETURAS if comparar and not rapido else ["padrao"]
    if "--arquitetura" in sys.argv:
        idx = sys.argv.index("--arquitetura")
        arquiteturas = [sys.argv[idx + 1]]

    suite = _resolver_suite()
    timeout_total = _resolver_timeout_total()
    casos_ids = _resolver_casos()

    if "--llm" in sys.argv:
        os.environ["RUNTIME_PLANEJADOR"] = "llm"

    if timeout_total and "RUNTIME_LLM_TIMEOUT_SEC" not in os.environ:
        n_casos = len(casos_ids or CASOS_RAPIDO if rapido else [1] * 8)
        if rapido or casos_ids:
            n_casos = len(casos_ids or CASOS_RAPIDO)
        else:
            n_casos = 8 * len(arquiteturas)
        por_chamada = max(3.0, min(9.0, (timeout_total - 2) / max(n_casos, 1)))
        os.environ["RUNTIME_LLM_TIMEOUT_SEC"] = str(round(por_chamada, 1))

    RESULTADOS.mkdir(parents=True, exist_ok=True)
    todos = []
    inicio = time.monotonic()

    print(f"Suite: {suite}")
    if casos_ids:
        print(f"Casos: {', '.join(casos_ids)}")
    if timeout_total:
        print(f"Budget: {timeout_total}s (LLM timeout/call: {os.environ.get('RUNTIME_LLM_TIMEOUT_SEC', '?')}s)")

    for arq in arquiteturas:
        restante = None
        if timeout_total:
            restante = max(1.0, timeout_total - (time.monotonic() - inicio))
            if restante <= 1.0:
                print(f"\n! Timeout atingido antes de {arq}")
                break
        print(f"\n>>> Rodando arquitetura: {arq}")
        resultado = rodar_tool_eval(
            AGENTE,
            suite,
            arquitetura=None if arq == "padrao" else arq,
            casos_ids=casos_ids,
            timeout_total_seg=restante,
            log_path=RESULTADOS / f"tool_eval_{arq}_rapido.log" if rapido else None,
        )
        caminho = RESULTADOS / f"tool_eval_{arq}.json"
        caminho.write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
        todos.append(resultado)

    duracao = round(time.monotonic() - inicio, 2)

    if comparar or len(todos) > 1:
        gerar_relatorio_tool_eval(todos, str(RESULTADOS / "tool_selection_report.md"))

    resumo = {
        "suite": suite,
        "modo": os.environ.get("RUNTIME_PLANEJADOR", "auto"),
        "casos": casos_ids,
        "duracao_seg": duracao,
        "timeout_total_seg": timeout_total,
        "llm_timeout_por_chamada_seg": os.environ.get("RUNTIME_LLM_TIMEOUT_SEC"),
        "arquiteturas": [
            {
                "arquitetura": r["arquitetura"],
                "tool_selection_accuracy": r["tool_selection_accuracy"],
                "argument_accuracy": r["argument_accuracy"],
                "unnecessary_calls_rate": r["unnecessary_calls_rate"],
                "wrong_tool_rate": r["wrong_tool_rate"],
                "violacoes": r.get("violacoes", []),
                "duracao_seg": r.get("duracao_seg"),
            }
            for r in todos
        ],
    }
    (RESULTADOS / "resumo_execucao.json").write_text(
        json.dumps(resumo, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\n=== RESUMO ({duracao}s) ===")
    print(json.dumps(resumo, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
