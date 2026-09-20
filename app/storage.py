import json, os, re, tempfile, threading, uuid
from pathlib import Path
from . import config

LOCK = threading.RLock()
ID_RE = re.compile(r'^[a-f0-9]{32}$')

def ensure_storage():
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.SERVERS_DIR.mkdir(parents=True, exist_ok=True)
    if not config.USERS_FILE.exists(): atomic_write(config.USERS_FILE, [])

def atomic_write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix='.tmp-', text=True)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(value, f, indent=2); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def read_json(path, default):
    try:
        with open(path, encoding='utf-8') as f: value = json.load(f)
        return value if isinstance(value, type(default)) else default
    except (OSError, ValueError, TypeError): return default

def valid_id(value): return isinstance(value, str) and bool(ID_RE.fullmatch(value))
def new_id(): return uuid.uuid4().hex
def users(): ensure_storage(); return read_json(config.USERS_FILE, [])
def save_users(value):
    with LOCK: atomic_write(config.USERS_FILE, value)
def _files(server_id):
    if not valid_id(server_id): raise ValueError('invalid server id')
    directory = config.SERVERS_DIR / server_id
    if directory.parent != config.SERVERS_DIR: raise ValueError('invalid path')
    return directory / 'server.json', directory / 'chat.json'
def get_server(server_id):
    if not valid_id(server_id): return None
    return read_json(_files(server_id)[0], None)
def save_server(server): atomic_write(_files(server['id'])[0], server)
def get_messages(server_id):
    if not valid_id(server_id): return []
    return read_json(_files(server_id)[1], [])
def save_messages(server_id, messages): atomic_write(_files(server_id)[1], messages)
