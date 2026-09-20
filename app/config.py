import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get('VERVRA_DATA_DIR', BASE_DIR / 'data'))
USERS_FILE = DATA_DIR / 'users.json'
SERVERS_DIR = DATA_DIR / 'servers'
SECRET_KEY = os.environ.get('VERVRA_SECRET_KEY', 'vervra-development-secret')
MAX_MESSAGE_LENGTH = 2000
