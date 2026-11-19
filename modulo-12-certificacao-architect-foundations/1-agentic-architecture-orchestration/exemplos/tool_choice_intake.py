"""
CCAR-F · tool_choice forçada → extract_ticket_fields → open_ticket → end_turn.
Mock por default; --live usa Anthropic API.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

TOOLS = [
    {
        "name": "extract_ticket_fields",
        "description": "Extract ticket fields from the customer message for intake parsing.",
        "input_schema": {
            "type": "object",
            "properties": {
                "intent": {
                    "type": "string",
                    "enum": ["refund", "shipping", "cancel", "other"],
                },
                "order_id": {"type": ["string", "null"]},
                "amount": {"type": ["number", "null"]},
                "urgency": {
                    "type": "string",
                    "enum": ["low", "normal", "high"],
                },
            },
            "required": ["intent", "order_id", "amount", "urgency"],
        },
    }
]


def open_ticket(fields: dict[str, Any]) -> str:
    tid = "T-9001"
    print(f"[host] open_ticket({fields}) → {tid}")
    return tid


def mock_forced_extract(_messages: list) -> dict[str, Any]:
    return {
        "stop_reason": "tool_use",
        "content": [
            {
                "type": "tool_use",
                "id": "toolu_01Extract",
                "name": "extract_ticket_fields",
                "input": {
                    "intent": "refund",
                    "order_id": "88210",
                    "amount": 189.9,
                    "urgency": "high",
                },
            }
        ],
    }


def mock_end_turn(ticket_id: str, fields: dict[str, Any]) -> dict[str, Any]:
    return {
        "stop_reason": "end_turn",
        "content": [
            {
                "type": "text",
                "text": (
                    f"Ticket {ticket_id} aberto: {fields['intent']} "
                    f"pedido {fields['order_id']}, R${fields['amount']}, "
                    f"urgência {fields['urgency']}."
                ),
            }
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()

    email_body = (
        "Oi, cobraram duas vezes o pedido 88210.\n"
        "Quero estorno de R$ 189,90. Urgente.\n— Marina"
    )
    messages: list[dict[str, Any]] = [
        {"role": "user", "content": f"Customer email:\n{email_body}"}
    ]

    if args.live:
        import anthropic

        client = anthropic.Anthropic()
        resp = client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929"),
            max_tokens=512,
            tools=TOOLS,
            tool_choice={"type": "tool", "name": "extract_ticket_fields"},
            messages=messages,
        )
        stop = resp.stop_reason
        content = resp.content
        # normalize to dicts
        blocks = []
        for b in content:
            if b.type == "tool_use":
                blocks.append(
                    {
                        "type": "tool_use",
                        "id": b.id,
                        "name": b.name,
                        "input": b.input,
                    }
                )
            elif b.type == "text":
                blocks.append({"type": "text", "text": b.text})
        content = blocks
    else:
        raw = mock_forced_extract(messages)
        stop, content = raw["stop_reason"], raw["content"]

    print("stop_reason:", stop)
    print(json.dumps(content, ensure_ascii=False, indent=2))

    assert stop == "tool_use"
    block = next(b for b in content if b["type"] == "tool_use")
    fields = block["input"]
    ticket_id = open_ticket(fields)

    messages.append({"role": "assistant", "content": content})
    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": block["id"],
                    "content": json.dumps(
                        {"ticket_id": ticket_id, "fields": fields, "status": "created"}
                    ),
                }
            ],
        }
    )

    if args.live:
        resp2 = client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929"),
            max_tokens=256,
            tools=TOOLS,
            tool_choice={"type": "auto"},
            messages=messages,
        )
        print("stop_reason:", resp2.stop_reason)
        for b in resp2.content:
            if b.type == "text":
                print(b.text)
    else:
        raw2 = mock_end_turn(ticket_id, fields)
        print("stop_reason:", raw2["stop_reason"])
        print(raw2["content"][0]["text"])


if __name__ == "__main__":
    main()
