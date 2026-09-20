from functools import wraps
from flask import jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash
from .storage import new_id, save_users, users
import re

NAME_RE = re.compile(r'^[A-Za-z0-9_.-]{3,24}$')
def public_user(user): return {'id': user['id'], 'username': user['username']} if user else None
def current_user():
    uid = session.get('user_id')
    return next((u for u in users() if u.get('id') == uid), None) if uid else None
def login_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not current_user(): return jsonify(error='Authentication required'), 401
        return fn(*args, **kwargs)
    return wrapped
def register_user(username, password):
    username = username.strip() if isinstance(username, str) else ''
    if not NAME_RE.fullmatch(username): raise ValueError('Username must be 3-24 characters using letters, numbers, ., _, or -')
    if not isinstance(password, str) or not 8 <= len(password) <= 128: raise ValueError('Password must be 8-128 characters')
    records = users()
    if any(u.get('username','').lower() == username.lower() for u in records): raise ValueError('Username is already taken')
    user = {'id': new_id(), 'username': username, 'password_hash': generate_password_hash(password)}
    records.append(user); save_users(records); return user
def authenticate(username, password):
    if not isinstance(username, str) or not isinstance(password, str): return None
    user = next((u for u in users() if u.get('username','').lower() == username.strip().lower()), None)
    return user if user and check_password_hash(user.get('password_hash',''), password) else None
