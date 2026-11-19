"""
CCAR-F · 1.1 + 1.3 — multi tool_use no mesmo turn → host paralelo → resposta final.

Fluxo:
  User: notícias + clima
  API #1  stop_reason=tool_use  → web_search + get_weather (mesmo content)
  Host    asyncio.gather        → executa as duas em paralelo
  API #2  stop_reason=end_turn  → texto final para o user
          (opcional) tool final  → deliver_briefing (após síntese)

Uso:
  py -3 parallel_tool_loop.py              # mock (sem API key)
  set ANTHROPIC_API_KEY=... & py -3 parallel_tool_loop.py --live
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import time
from dataclasses import dataclass
from typing import Any

# ---------------------------------------------------------------------------
# Tools (client-side) — o modelo SÓ declara; o host EXECUTA
# ---------------------------------------------------------------------------

TOOLS: list[dict[str, Any]] = [
    {
        "name": "web_search",
        "description": (
            "Busca fatos/notícias atuais na web. "
            "Use quando o user pedir novidades, headlines ou eventos de hoje."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "get_weather",
        "description": (
            "Temperatura e condição atual por cidade. "
            "Use somente para clima/tempo."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    },
    {
        "name": "deliver_briefing",
        "description": (
            "Tool FINAL: entrega o briefing já sintetizado ao canal do user. "
            "Chame só DEPOIS de ter resultados de busca e clima. "
            "Não use para buscar dados."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "channel": {"type": "string", "enum": ["chat", "email", "slack"]},
                "body": {"type": "string"},
            },
            "required": ["channel", "body"],
        },
    },
]


def run_web_search(query: str) -> str:
    time.sleep(0.4)  # simula I/O
    return f"[web_search] top hits for '{query}': Anthropic update X; partners Y."


def run_get_weather(city: str) -> str:
    time.sleep(0.4)
    return f"[get_weather] {city}: 28°C, nublado."


def run_deliver_briefing(channel: str, body: str) -> str:
    time.sleep(0.1)
    return f"[deliver_briefing] sent via {channel} ({len(body)} chars)."


TOOL_IMPL = {
    "web_search": lambda inp: run_web_search(inp["query"]),
    "get_weather": lambda inp: run_get_weather(inp["city"]),
    "deliver_briefing": lambda inp: run_deliver_briefing(inp["channel"], inp["body"]),
}


@dataclass
class ToolUse:
    id: str
    name: str
    input: dict[str, Any]


def extract_tool_uses(content: list[Any]) -> list[ToolUse]:
    out: list[ToolUse] = []
    for block in content:
        btype = block["type"] if isinstance(block, dict) else block.type
        if btype != "tool_use":
            continue
        if isinstance(block, dict):
            out.append(ToolUse(block["id"], block["name"], block["input"]))
        else:
            out.append(ToolUse(block.id, block.name, block.input))
    return out


async def run_one(tool: ToolUse) -> dict[str, Any]:
    """Uma tool em thread — I/O não bloqueia o event loop."""
    impl = TOOL_IMPL.get(tool.name)
    started = time.perf_counter()
    if impl is None:
        result = {
            "type": "tool_result",
            "tool_use_id": tool.id,
            "is_error": True,
            "content": f"unknown tool: {tool.name}",
        }
    else:
        raw = await asyncio.to_thread(impl, tool.input)
        result = {
            "type": "tool_result",
            "tool_use_id": tool.id,
            "content": raw,
        }
    elapsed = time.perf_counter() - started
    print(f"  ✓ {tool.name} ({tool.id}) em {elapsed:.2f}s")
    return result


async def run_tools_parallel(tool_uses: list[ToolUse]) -> list[dict[str, Any]]:
    """Agrupa N tool_result — disparo paralelo (host, não a API)."""
    print(f"\n[host] disparando {len(tool_uses)} tool(s) em paralelo...")
    t0 = time.perf_counter()
    results = await asyncio.gather(*[run_one(t) for t in tool_uses])
    print(f"[host] paralelo total: {time.perf_counter() - t0:.2f}s "
          f"(série teria ~{0.4 * len(tool_uses):.1f}s)\n")
    return list(results)


def content_as_dicts(content: list[Any]) -> list[dict[str, Any]]:
    """Normaliza blocos SDK → dict para reenviar em messages."""
    out: list[dict[str, Any]] = []
    for block in content:
        if isinstance(block, dict):
            out.append(block)
            continue
        if block.type == "text":
            out.append({"type": "text", "text": block.text})
        elif block.type == "tool_use":
            out.append(
                {
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                }
            )
    return out


# ---------------------------------------------------------------------------
# Mock model — demonstra a sequência sem ANTHROPIC_API_KEY
# ---------------------------------------------------------------------------

class MockResponse:
    def __init__(self, stop_reason: str, content: list[dict[str, Any]]):
        self.stop_reason = stop_reason
        self.content = content


def mock_create(messages: list[dict[str, Any]]) -> MockResponse:
    """Simula: 1º turn = 2 tools; 2º = deliver_briefing; 3º = end_turn."""
    n_assistant = sum(1 for m in messages if m["role"] == "assistant")

    if n_assistant == 0:
        return MockResponse(
            "tool_use",
            [
                {
                    "type": "tool_use",
                    "id": "toolu_search",
                    "name": "web_search",
                    "input": {"query": "Claude AI news today"},
                },
                {
                    "type": "tool_use",
                    "id": "toolu_weather",
                    "name": "get_weather",
                    "input": {"city": "São Paulo"},
                },
            ],
        )

    if n_assistant == 1:
        # Modelo já viu os 2 tool_result → tool FINAL de entrega
        body = (
            "Briefing diário\n"
            "- Claude: Anthropic update X; partners Y.\n"
            "- São Paulo: 28°C, nublado."
        )
        return MockResponse(
            "tool_use",
            [
                {
                    "type": "tool_use",
                    "id": "toolu_deliver",
                    "name": "deliver_briefing",
                    "input": {"channel": "chat", "body": body},
                }
            ],
        )

    return MockResponse(
        "end_turn",
        [
            {
                "type": "text",
                "text": (
                    "Pronto — briefing enviado no chat.\n\n"
                    "Hoje sobre Claude: Anthropic update X; partners Y.\n"
                    "Clima em São Paulo: 28°C, nublado."
                ),
            }
        ],
    )


# ---------------------------------------------------------------------------
# Live Anthropic (opcional)
# ---------------------------------------------------------------------------

def live_create(client: Any, model: str, messages: list[dict[str, Any]]) -> Any:
    return client.messages.create(
        model=model,
        max_tokens=1024,
        tools=TOOLS,
        messages=messages,
    )


# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------

async def agent_loop(
    user_text: str,
    *,
    live: bool = False,
    model: str = "claude-sonnet-4-5-20250929",
) -> str:
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_text}]
    client = None
    if live:
        import anthropic

        client = anthropic.Anthropic()

    print(f"[user] {user_text}\n")
    final_text = ""

    for turn in range(1, 8):
        if live:
            resp = live_create(client, model, messages)
            stop = resp.stop_reason
            content = resp.content
        else:
            resp = mock_create(messages)
            stop = resp.stop_reason
            content = resp.content

        print(f"[api #{turn}] stop_reason={stop}")
        print(f"         content={json.dumps(content_as_dicts(content), ensure_ascii=False, indent=2)}")

        if stop == "tool_use":
            tool_uses = extract_tool_uses(content)
            # Mesmo turn com N tools → paralelo; 1 tool (ex. final) → gather de 1
            results = await run_tools_parallel(tool_uses)

            messages.append({"role": "assistant", "content": content_as_dicts(content)})
            messages.append({"role": "user", "content": results})  # agrupamento
            continue

        if stop == "end_turn":
            for block in content_as_dicts(content):
                if block.get("type") == "text":
                    final_text += block["text"]
            messages.append({"role": "assistant", "content": content_as_dicts(content)})
            break

        # max_tokens / stop_sequence / refusal → sai
        print(f"[host] saindo do loop: stop_reason={stop}")
        break

    return final_text


def main() -> None:
    parser = argparse.ArgumentParser(description="Parallel tool_use agent loop (CCAR-F)")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Chama Anthropic API (precisa ANTHROPIC_API_KEY)",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929"),
    )
    args = parser.parse_args()

    if args.live and not os.getenv("ANTHROPIC_API_KEY"):
        raise SystemExit("Defina ANTHROPIC_API_KEY para --live")

    user = (
        "Quais as notícias de hoje sobre Claude e como está o clima em São Paulo? "
        "Depois entregue o briefing no chat."
    )
    text = asyncio.run(agent_loop(user, live=args.live, model=args.model))
    print("=" * 60)
    print("[final → user]")
    print(text)


if __name__ == "__main__":
    main()
