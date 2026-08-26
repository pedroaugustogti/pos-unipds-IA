#!/usr/bin/env python3
"""Fase A — inspeciona select_model e opcionalmente faz smoke no OpenRouter."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.env_load import ensure_env  # noqa: E402

ensure_env()

from lib.model_tier import select_model  # noqa: E402


def _smoke(model: str) -> dict:
    import os

    try:
        from openai import OpenAI
    except ImportError:
        return {"ok": False, "error": "pacote openai nao instalado (pip install openai)"}

    key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    if not key:
        return {"ok": False, "error": "OPENAI_API_KEY ausente"}

    base = (os.environ.get("OPENAI_API_BASE") or os.environ.get("OPENAI_BASE_URL") or "").strip()
    try:
        client = OpenAI(api_key=key, base_url=base or None)
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Responda apenas: ok"}],
            max_tokens=8,
        )
        text = (resp.choices[0].message.content or "").strip()
        return {"ok": True, "model": model, "reply": text[:80]}
    except Exception as exc:  # noqa: BLE001 — CLI smoke reporta qualquer falha de rede/SSL/API
        return {"ok": False, "model": model, "error": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    p = argparse.ArgumentParser(description="Fase A — model tier CLI")
    p.add_argument("--purpose", default="implement_low")
    p.add_argument("--title", default="Ajuste de layout")
    p.add_argument("--role", default="frontend-mobile")
    p.add_argument("--smoke", action="store_true", help="Chamada real OpenRouter no modelo escolhido")
    p.add_argument("--smoke-high", action="store_true", help="Tambem testa GUARDIAO_LLM_HIGH")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    task = {"title": args.title, "agent_role": args.role}
    selected = select_model(task, purpose=args.purpose, role=args.role)
    out: dict = {"select_model": selected}

    if args.smoke and selected.get("uses_llm"):
        out["smoke"] = _smoke(str(selected["model"]))
    if args.smoke_high:
        high = select_model({"title": "pagamento SOS"}, purpose="implement_high")
        out["high"] = high
        out["smoke_high"] = _smoke(str(high["model"]))

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(selected, ensure_ascii=False, indent=2))
        if "smoke" in out:
            print("smoke:", json.dumps(out["smoke"], ensure_ascii=False))
        if "smoke_high" in out:
            print("smoke_high:", json.dumps(out["smoke_high"], ensure_ascii=False))

    if args.smoke and out.get("smoke") and not out["smoke"].get("ok"):
        return 1
    if args.smoke_high and out.get("smoke_high") and not out["smoke_high"].get("ok"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
