import os
from pathlib import Path

EXEMPLO_REAL = Path(__file__).resolve().parents[2]
FLOW_PATH = EXEMPLO_REAL / "rag-fluxo-parent.jsonl"
SESSAO_PATH = Path(__file__).resolve().parents[1] / "sessao_appium.json"

APPIUM_URL = os.environ.get("GF_APPIUM_URL", "http://127.0.0.1:4723").rstrip("/")
SERIAL = os.environ.get("GF_PARENT_EMULATOR_SERIAL", "emulator-5554")
PACKAGE = "com.guardiaofamilia.parent"
ACTIVITY = "com.guardiaofamilia.parent.MainActivity"
METRO = os.environ.get("GF_PARENT_METRO_PORT", "8082")
DEV_URL = (
    f"exp+guardiao-familia-parent://expo-development-client/"
    f"?url=http://10.0.2.2:{METRO}"
)
