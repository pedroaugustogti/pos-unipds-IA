#!/usr/bin/env python3
"""GraphQL fallback para contar items do Project #2."""
import json
import os
import urllib.request

ORG = "guardiaofamilia"
PROJECT_NUMBER = 2

def main():
    token = (os.environ.get("CURSOR_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN") or "").strip()
    if not token:
        print("TOKEN missing")
        return 1
    q = """
    query($org: String!, $num: Int!) {
      organization(login: $org) {
        projectV2(number: $num) {
          title
          items(first: 100) {
            totalCount
            nodes { title }
            pageInfo { hasNextPage endCursor }
          }
        }
      }
    }
    """
    payload = json.dumps({"query": q, "variables": {"org": ORG, "num": PROJECT_NUMBER}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode())
    if data.get("errors"):
        print("ERR:", "; ".join(e["message"] for e in data["errors"]))
        return 1
    proj = data["data"]["organization"]["projectV2"]
    items = proj["items"]
    print(f"Project: {proj['title']}")
    print(f"totalCount: {items['totalCount']}")
    v2 = sum(1 for n in items["nodes"] if (n.get("title") or "").startswith("[T-"))
    print(f"sample [T-*] in first page: {v2}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
