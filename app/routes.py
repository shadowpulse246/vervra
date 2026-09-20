from flask import Blueprint, jsonify, request, session
from .auth import authenticate, current_user, login_required, public_user, register_user
from .config import MAX_MESSAGE_LENGTH
from .storage import get_messages, get_server, new_id, save_messages, save_server

api = Blueprint('api', __name__, url_prefix='/api')
def data(): return request.get_json(silent=True) if isinstance(request.get_json(silent=True), dict) else {}
def view(s): return {'id':s['id'],'name':s['name'],'owner_id':s['owner_id'],'members':len(s['members']),'channels':s['channels']}
def member(s, uid): return s and uid in s.get('members', [])

@api.post('/signup')
def signup():
    try: user = register_user(data().get('username'), data().get('password'))
    except ValueError as e: return jsonify(error=str(e)), 400
    session.clear(); session['user_id'] = user['id']; return jsonify(user=public_user(user)), 201
@api.post('/login')
def login():
    user = authenticate(data().get('username'), data().get('password'))
    if not user: return jsonify(error='Invalid username or password'), 401
    session.clear(); session['user_id'] = user['id']; return jsonify(user=public_user(user))
@api.post('/logout')
def logout(): session.clear(); return jsonify(ok=True)
@api.get('/me')
def me():
    user = current_user(); return (jsonify(user=public_user(user)), 200) if user else (jsonify(user=None), 401)
@api.get('/servers')
@login_required
def servers():
    from . import config
    uid = current_user()['id']; result=[]
    for p in config.SERVERS_DIR.iterdir() if config.SERVERS_DIR.exists() else []:
        s=get_server(p.name)
        if s and member(s,uid): result.append(view(s))
    return jsonify(servers=result)
@api.post('/servers')
@login_required
def create_server():
    name=data().get('name'); name=name.strip() if isinstance(name,str) else ''
    if not 2 <= len(name) <= 50: return jsonify(error='Server name must be 2-50 characters'), 400
    uid=current_user()['id']; sid=new_id(); s={'id':sid,'name':name,'owner_id':uid,'members':[uid],'channels':[{'id':'general','name':'general','type':'text'}]}
    save_server(s); save_messages(sid, []); return jsonify(server=view(s)), 201
@api.get('/servers/<server_id>')
@login_required
def server_detail(server_id):
    s=get_server(server_id); uid=current_user()['id']
    if not s: return jsonify(error='Server not found'), 404
    if not member(s,uid): return jsonify(error='Join this server first'), 403
    return jsonify(server=view(s), messages=get_messages(server_id))
@api.post('/servers/<server_id>/join')
@login_required
def join_server(server_id):
    s=get_server(server_id)
    if not s: return jsonify(error='Server not found'), 404
    uid=current_user()['id']
    if uid not in s['members']: s['members'].append(uid); save_server(s)
    return jsonify(server=view(s))
