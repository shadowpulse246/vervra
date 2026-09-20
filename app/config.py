import os
from pathlib import Path

# All paths are anchored to the repository, not the process working directory.
BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_DIR = BASE_DIR / "public"
DATA_DIR = Path(os.environ.get("VERVRA_DATA_DIR", str(BASE_DIR / "data"))).resolve()
USERS_FILE = DATA_DIR / "users.json"
SERVERS_DIR = DATA_DIR / "servers"
SECRET_KEY = os.environ.get("VERVRA_SECRET_KEY", "vervra-development-secret")
MAX_MESSAGE_LENGTH = 2000
