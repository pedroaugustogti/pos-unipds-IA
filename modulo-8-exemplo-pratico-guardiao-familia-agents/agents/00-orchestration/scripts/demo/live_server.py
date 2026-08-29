#!/usr/bin/env python3
"""HTTP local sem cache para dashboard ao vivo (Fase 4.2)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_bs = Path(__file__).resolve().parents[2] / "bootstrap.py"
_spec = importlib.util.spec_from_file_location("orch_bootstrap", _bs)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)
_mod.setup()

import argparse
import functools
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from lib.paths import MODULE_ROOT  # noqa: E402
from lib.env_load import ensure_env  # noqa: E402

ensure_env()
from lib.observability import OUT_DIR, build_snapshot, write_dashboard  # noqa: E402


class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def main() -> int:
    p = argparse.ArgumentParser(description="Serve observability/ com polling live")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--no-refresh", action="store_true", help="Nao regenera snapshot na subida")
    args = p.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not args.no_refresh:
        write_dashboard(build_snapshot())

    handler = functools.partial(NoCacheHandler, directory=str(OUT_DIR))
    httpd = ThreadingHTTPServer((args.host, args.port), handler)
    url = f"http://{args.host}:{args.port}/dashboard.html"
    print(f"Live dashboard: {url}")
    print(f"Root: {OUT_DIR}")
    print("Ctrl+C para parar")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nparado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
