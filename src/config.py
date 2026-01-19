from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

DB_PATH = DATA_DIR / "contabilidad.db"
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

DEFAULT_ACCOUNT_NAME = "credito"   # si no dicen cuenta
CURRENCY = "CLP"
# agregando resumen automatico
OWNER_CHAT_ID = int(os.environ.get("OWNER_CHAT_ID", "0"))
