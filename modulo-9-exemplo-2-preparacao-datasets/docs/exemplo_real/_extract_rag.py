# -*- coding: utf-8 -*-
"""Extrai rag-api.jsonl e rag-backoffice.jsonl a partir dos repositórios."""
import json
import re
from pathlib import Path

API = Path(r"C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-api\src")
PARENT = Path(r"C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-parent")
CHILD = Path(r"C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-child")
BACKOFFICE = Path(r"C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-backoffice")
OUT = Path(r"c:\Users\pedro\Documents\pos-unipds\pos-unipds-IA\modulo-9-exemplo-2-preparacao-datasets\docs\exemplo_real")

HTTP_RE = re.compile(r"@(Get|Post|Put|Patch|Delete)\(\s*(?:'([^']*)'|\"([^\"]*)\"|`([^`]*)`)?\s*\)")
CTRL_RE = re.compile(r"@Controller\(\s*(?:'([^']*)'|\"([^\"]*)\"|`([^`]*)`)?\s*\)")
OP_RE = re.compile(r"@ApiOperation\(\s*\{[^}]*summary:\s*'([^']*)'")
OP_RE2 = re.compile(r'@ApiOperation\(\s*\{\s*summary:\s*"([^"]*)"')
ROLES_RE = re.compile(r"@Roles\(([^)]*)\)")
BODY_RE = re.compile(r"@Body\(\)\s*(?:dto|body|payload)?\s*:\s*(\w+)")
QUERY_DTO_RE = re.compile(r"@Query\(\)\s*\w+\s*:\s*(\w+)")
QUERY_NAME_RE = re.compile(r"@Query\(\s*'([^']+)'")
PARAM_RE = re.compile(r"@Param\(\s*'([^']+)'")
OK_RE = re.compile(r"@Api(?:Ok|Created)Response\(\s*\{[^}]*type:\s*(\w+)")

CLASS_RE = re.compile(r"export class (\w+)")
PROP_RE = re.compile(
    r"(?:@\w+(?:\([^)]*\))?\s*)*\n?\s*(\w+)\??\s*:\s*([^;]+);",
)
OPTIONAL_RE = re.compile(r"@IsOptional\b|@ApiPropertyOptional\b")
MATCH_RE = re.compile(r"@Matches\(\s*/(.+)/[a-z]*\s*\)")
ENUM_RE = re.compile(r"@IsEnum\(\s*(\w+)\s*\)")
TYPE_HINT = (
    ("IsUUID", "uuid"),
    ("IsEmail", "email"),
    ("IsBoolean", "boolean"),
    ("IsInt", "integer"),
    ("IsNumber", "number"),
    ("IsDate", "date"),
    ("IsArray", "array"),
    ("IsString", "string"),
)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def dto_index():
    idx = {}
    for p in API.rglob("*.ts"):
        if "dto" not in p.as_posix().lower() and not p.name.endswith(".dto.ts"):
            if "/dto/" not in p.as_posix().replace("\\", "/"):
                continue
        text = read(p)
        for m in re.finditer(r"export class (\w+)([\s\S]*?)(?=\nexport class |\Z)", text):
            idx[m.group(1)] = m.group(2)
    return idx


def fields_of(body: str, onde: str):
    out = []
    chunks = re.split(r"\n\s*(?=@)", "\n" + body)
    for ch in chunks:
        pm = re.search(r"\n\s*(\w+)\??\s*:\s*([^;=]+);", ch)
        if not pm:
            continue
        name, typ = pm.group(1), pm.group(2).strip()
        if name in ("constructor",):
            continue
        decor = ch[: pm.start()]
        obrig = not (name.endswith("?") or OPTIONAL_RE.search(decor) or "?" in typ.split("=")[0][-2:])
        pattern = ""
        mm = MATCH_RE.search(decor)
        if mm:
            pattern = mm.group(1)
        em = ENUM_RE.search(decor)
        tipo = typ.replace(" | ", "|")
        for needle, label in TYPE_HINT:
            if needle in decor:
                tipo = label
                break
        if em:
            tipo = f"enum {em.group(1)}"
        ctx = "Campo do DTO."
        if pattern:
            ctx = f"Campo do DTO. Pattern: {pattern}."
        out.append({
            "nome": name,
            "onde": onde,
            "tipo": tipo[:80],
            "obrigatorio": obrig and "?" not in typ,
            "pattern": pattern,
            "contexto": ctx,
        })
    return out


def join_url(prefix, method_path):
    parts = [x.strip("/") for x in (prefix, method_path) if x and x.strip("/")]
    path = "/".join(parts)
    return "/api/v1/" + path if path else "/api/v1"


def audience(roles, file_name, url, hits):
    parent_hit, child_hit, bo_hit = hits
    callers = []
    if parent_hit:
        callers.append("parent")
    if child_hit:
        callers.append("child")
    if bo_hit:
        callers.append("backoffice")
    if callers:
        return callers
    role_set = set(re.findall(r"UserRole\.(\w+)", roles or ""))
    name = file_name.lower()
    if "/webhooks" in url:
        return []
    if role_set == {"ADMIN"} or "/admin/" in url or url.startswith("/api/v1/admin"):
        return ["backoffice"]
    if "DEVICE" in role_set or "device" in name or role_set == {"CHILD"}:
        return ["child"]
    if "child" in name and "parent" not in name:
        return ["child"]
    return ["parent"]


def caller_note(url, chamado, roles, hits):
    parent_hit, child_hit, bo_hit = hits
    if "/webhooks" in url and not any(hits):
        return "Webhook: nenhum app mobile nem o back-office chama esta rota."
    if not any(hits):
        return "Nenhuma chamada literal em parent, child ou back-office; chamado_por veio da role ou do caminho."
    return ""


PATH_RE = re.compile(r"/((?:[a-z0-9${}.:-]+)(?:/[a-z0-9${}.:-]+)+)")


def collect_client_paths():
    bag = {"parent": [], "child": [], "backoffice": []}
    roots = (("parent", PARENT), ("child", CHILD), ("backoffice", BACKOFFICE))
    for label, root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if p.suffix not in {".ts", ".tsx"}:
                continue
            if "node_modules" in p.parts or "dist" in p.parts or ".expo" in p.parts or ".next" in p.parts:
                continue
            text = read(p)
            for m in PATH_RE.finditer(text):
                path = re.sub(r"\$\{[^}]+\}", "{id}", m.group(1)).split("?")[0].strip("/")
                segs = path.split("/")
                if any(seg[:1].isupper() for seg in segs):
                    continue
                if path.endswith((".ts", ".tsx", ".png", ".svg")):
                    continue
                bag[label].append(path)
    return bag


def called_by(url, bag):
    tail = url.replace("/api/v1/", "").strip("/")
    segs = [s for s in tail.split("/") if s and not s.startswith(":")]
    key = "/".join(segs[-2:]) if len(segs) >= 2 else (segs[0] if segs else tail)

    def hit(samples):
        for s in samples:
            if key and key in s:
                return True
        return False

    return hit(bag["parent"]), hit(bag["child"]), hit(bag["backoffice"])


def extract_api(dtos, bag):
    rows = []
    for p in sorted(API.rglob("*.controller.ts")):
        text = read(p)
        rel = p.relative_to(API.parent).as_posix()
        parts = CTRL_RE.split(text)
        # split keeps the capture groups: [pre, g1, g2, g3, body, g1, g2, g3, body...]
        if len(parts) < 5:
            continue
        i = 1
        while i + 3 < len(parts):
            prefix = parts[i] or parts[i + 1] or parts[i + 2] or ""
            body = parts[i + 3]
            i += 4
            roles = " ".join(ROLES_RE.findall(body[:800]))
            # method blocks
            matches = list(HTTP_RE.finditer(body))
            for idx, hm in enumerate(matches):
                method = hm.group(1).upper()
                method_path = hm.group(2) or hm.group(3) or hm.group(4) or ""
                url = join_url(prefix, method_path)
                start = hm.end()
                end = matches[idx + 1].start() if idx + 1 < len(matches) else min(len(body), start + 1800)
                block = body[hm.start():end]
                # drop the next decorator's method if we included too much: cut at next export or next class method signature after first function
                ph, ch, bo = called_by(url, bag)
                quem = audience(roles, p.name, url, (ph, ch, bo))
                entrada = []
                for name in PARAM_RE.findall(block):
                    entrada.append({
                        "nome": name,
                        "onde": "path",
                        "tipo": "string",
                        "obrigatorio": True,
                        "pattern": "uuid" if "UUID" in block or "uuid" in name.lower() or name.endswith("Id") else "",
                        "contexto": "Parâmetro de rota.",
                    })
                for name in QUERY_NAME_RE.findall(block):
                    entrada.append({
                        "nome": name,
                        "onde": "query",
                        "tipo": "string",
                        "obrigatorio": False,
                        "pattern": "",
                        "contexto": "Query string nomeada no controller.",
                    })
                bm = BODY_RE.search(block)
                if bm and bm.group(1) in dtos:
                    entrada.extend(fields_of(dtos[bm.group(1)], "body"))
                elif bm:
                    entrada.append({
                        "nome": bm.group(1),
                        "onde": "body",
                        "tipo": bm.group(1),
                        "obrigatorio": True,
                        "pattern": "",
                        "contexto": "DTO referenciado, classe não lida em src/**/dto.",
                    })
                qm = QUERY_DTO_RE.search(block)
                if qm and qm.group(1) in dtos:
                    entrada.extend(fields_of(dtos[qm.group(1)], "query"))
                saida = []
                ok = OK_RE.search(block)
                if ok:
                    saida.append({
                        "nome": ok.group(1),
                        "tipo": ok.group(1),
                        "contexto": "Tipo declarado em @ApiOkResponse ou @ApiCreatedResponse.",
                    })
                else:
                    saida.append({
                        "nome": "retorno do service",
                        "tipo": "não declarado no controller",
                        "contexto": "O handler devolve o retorno do service sem tipo Swagger neste método.",
                    })
                summary = ""
                sm = OP_RE.search(block) or OP_RE2.search(block)
                if sm:
                    summary = sm.group(1)
                note = caller_note(url, quem, roles, (ph, ch, bo))
                resumo = summary or f"{method} {url}"
                if note:
                    resumo = resumo + " " + note
                apps = []
                if ph:
                    apps.append("parent")
                if ch:
                    apps.append("child")
                if bo:
                    apps.append("backoffice")
                fonte = ", ".join(apps) if apps else "sem chamada literal nos apps"
                quem_txt = ", ".join(quem) if quem else "nenhum"
                prompt = (
                    f"{method} {url} ({p.name}). chamado_por={quem_txt}. "
                    f"Visto em: {fonte}. {resumo}"
                )
                rows.append({
                    "method": method,
                    "url": url,
                    "controller": rel,
                    "chamado_por": quem,
                    "entrada": entrada,
                    "saida": saida,
                    "resumo_contexto": resumo.strip(),
                    "prompt_context": prompt.strip(),
                })
    # dedupe method+url keeping first
    seen = set()
    uniq = []
    for r in rows:
        k = (r["method"], r["url"])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(r)
    return uniq


def extract_backoffice():
    api_text = read(BACKOFFICE / "lib" / "adminApi.ts")
    chunks = re.split(r"export (?:async )?function (\w+)", api_text)
    funcs = {}
    for i in range(1, len(chunks) - 1, 2):
        name, body = chunks[i], chunks[i + 1][:2500]
        method_m = re.search(r"method:\s*['\"](\w+)['\"]", body)
        method = method_m.group(1).upper() if method_m else "GET"
        eps = []
        for m in PATH_RE.finditer(body):
            path = re.sub(r"\$\{[^}]+\}", "{id}", m.group(1)).split("?")[0].strip("/")
            if path.startswith("admin") or path.startswith("auth"):
                eps.append(f"{method} /api/v1/{path}")
        seen = []
        for e in eps:
            if e not in seen:
                seen.append(e)
        funcs[name] = seen

    shell = read(BACKOFFICE / "components" / "AdminShell.tsx")
    nav = dict(re.findall(r"href:\s*'([^']+)',\s*label:\s*'([^']+)'", shell))

    rows = []
    for page in sorted((BACKOFFICE / "app").rglob("page.tsx")):
        rel_app = page.relative_to(BACKOFFICE / "app").as_posix()
        route = "/" + rel_app.replace("/page.tsx", "").replace("page.tsx", "")
        route = re.sub(r"\([^)]+\)/?", "", route)
        route = re.sub(r"/+", "/", route)
        if route != "/" and route.endswith("/"):
            route = route[:-1]
        if not route:
            route = "/"
        text = read(page)
        imported = re.findall(r"import\s*\{([^}]+)\}\s*from\s*'@/lib/adminApi'", text)
        names = []
        for block in imported:
            names.extend(n.strip().split(" ")[0].strip() for n in block.split(",") if n.strip() and not n.strip().startswith("type "))
        acoes = []
        for n in names:
            eps = funcs.get(n) or []
            if not eps:
                acoes.append({
                    "funcao": n,
                    "endpoint": None,
                    "acao": f"{n} importada de adminApi; path não lido no corpo da função.",
                })
            for ep in eps:
                acoes.append({
                    "funcao": n,
                    "endpoint": ep,
                    "acao": f"{n} chama {ep}.",
                })
        label = nav.get(route, route.strip("/") or "inicio")
        accessed = ["AdminShell"] if route in nav else []
        eps_txt = ", ".join(a["endpoint"] for a in acoes if a["endpoint"]) or "nenhum path /admin no arquivo"
        rows.append({
            "route": route,
            "label": label,
            "page_file": page.relative_to(BACKOFFICE).as_posix(),
            "accessed_from": accessed,
            "navigates_to": [],
            "acoes": acoes,
            "prompt_context": (
                f"Página back-office {route} ({label}) em {page.relative_to(BACKOFFICE).as_posix()}. "
                f"Funções adminApi: {', '.join(names) or 'nenhuma'}. Endpoints: {eps_txt}."
            ),
        })
    return rows


def main():
    dtos = dto_index()
    bag = collect_client_paths()
    api_rows = extract_api(dtos, bag)
    backoffice = extract_backoffice()
    api_rows.sort(key=lambda r: (r["url"], r["method"]))
    backoffice.sort(key=lambda r: r["route"])
    outputs = (
        ("rag-api.jsonl", api_rows),
        ("rag-backoffice.jsonl", backoffice),
    )
    for name, rows in outputs:
        path = OUT / name
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8", newline="\n")
        print(name, len(rows))


if __name__ == "__main__":
    main()
