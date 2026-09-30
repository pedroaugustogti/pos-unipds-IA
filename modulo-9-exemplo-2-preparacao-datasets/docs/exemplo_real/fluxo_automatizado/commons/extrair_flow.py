"""Devolve o objeto JSON do fluxo a partir do flow_id.

O prefixo escolhe o arquivo: parent, child ou backoffice.
"""

from __future__ import annotations

import json
import sys

try:
    from .variaveis_parent import EXEMPLO_REAL
except ImportError:
    from variaveis_parent import EXEMPLO_REAL


def extrair_flow(flow_id: str) -> dict:
    app = flow_id.split(".", 1)[0]
    path = EXEMPLO_REAL / f"rag-fluxo-{app}.jsonl"
    if not path.exists():
        raise SystemExit(f"arquivo de fluxo nao encontrado: {path.name}")
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("flow_id") == flow_id:
            return row
    raise SystemExit(f"{flow_id} nao esta em {path.name}")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("uso: python extrair_flow.py <flow_id>")
    print(json.dumps(extrair_flow(sys.argv[1]), ensure_ascii=False))


if __name__ == "__main__":
    main()
