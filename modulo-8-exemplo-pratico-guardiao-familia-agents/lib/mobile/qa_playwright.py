"""QA gate interno com Playwright — evidência anexada na issue (sem persistir em disco)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def run_hero_home_playwright(
    *,
    base_url: str,
    expected_text: str,
    forbidden_in_h1: str,
    task_id: str,
) -> dict[str, Any]:
    """
    Abre a home, valida H1/title e captura screenshot em memoria (bytes PNG).
    Requer: pip install playwright && playwright install chromium (ou Chrome local).
    """
    at = datetime.now(timezone.utc).isoformat()
    case: dict[str, Any] = {
        "id": "QA-SITE-HERO-01",
        "name": "Home hero exibe Tranquilidade para sua família",
        "type": "e2e_playwright",
        "steps": (
            f"1. Navegar para {base_url}\n"
            "2. Localizar H1 do hero\n"
            f"3. Assert texto contém '{expected_text}'\n"
            f"4. Assert H1 não contém '{forbidden_in_h1}'\n"
            "5. Capturar screenshot e anexar na issue"
        ),
        "expected": f"H1 e title refletem '{expected_text}'",
        "result": "FAIL",
        "notes": "",
        "at": at,
        "task_id": task_id,
    }

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        case["notes"] = f"playwright nao instalado: {exc}"
        return {"ok": False, "case": case, "error": str(exc), "png_bytes": None}

    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(channel="chrome", headless=True)
            except Exception:
                browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.goto(base_url, wait_until="domcontentloaded", timeout=30000)
            h1 = page.locator("section.hero h1").first
            h1.wait_for(state="visible", timeout=10000)
            text = (h1.inner_text() or "").replace("\n", " ").strip()
            title = page.title()
            png_bytes = page.screenshot(full_page=True, type="png")
            browser.close()

        ok_expected = expected_text.lower() in text.lower()
        ok_forbidden = forbidden_in_h1.lower() not in text.lower()
        ok_title = expected_text.lower() in title.lower()
        ok = ok_expected and ok_forbidden and ok_title
        case["result"] = "PASS" if ok else "FAIL"
        case["notes"] = (
            f"h1={text!r}; title={title!r}; "
            f"expected_ok={ok_expected}; forbidden_ok={ok_forbidden}; title_ok={ok_title}"
        )
        case["observed_h1"] = text
        case["observed_title"] = title
        return {"ok": ok, "case": case, "png_bytes": png_bytes, "filename": f"{task_id}_home_hero.png"}
    except Exception as exc:  # noqa: BLE001
        case["notes"] = f"erro playwright: {exc}"
        return {"ok": False, "case": case, "error": str(exc), "png_bytes": None}


def format_qa_issue_comment(qa: dict[str, Any], *, image_markdown: str = "") -> str:
    case = qa.get("case") or {}
    lines = [
        "## QA Gate — Playwright (evidência)",
        "",
        f"**Caso:** `{case.get('id')}` — {case.get('name')}",
        f"**Resultado:** **{case.get('result')}**",
        "",
        "### Passos",
        "```",
        str(case.get("steps") or ""),
        "```",
        "",
        f"**Esperado:** {case.get('expected')}",
        f"**Observado:** {case.get('notes')}",
        "",
    ]
    if image_markdown:
        lines.extend(["### Screenshot", "", image_markdown, ""])
    return "\n".join(lines)
