from datetime import datetime, timezone
from flask import request
from flask_socketio import emit, join_room
from .auth import current_user
from .config import MAX_MESSAGE_LENGTH
from .storage import get_messages, get_server, new_id, save_messages

def register_socket_events(socketio):
    @socketio.on('join-server')
    def join_server(d):
        u=current_user(); sid=d.get('server_id') if isinstance(d,dict) else None; s=get_server(sid) if sid else None
        if not u or not s or u['id'] not in s.get('members',[]): return emit('error',{'error':'Unauthorized server'})
        join_room(sid); emit('server-joined',{'server_id':sid})
    @socketio.on('join-room')
    def join_channel(d):
        u=current_user(); sid=d.get('server_id') if isinstance(d,dict) else None; rid=d.get('room_id') if isinstance(d,dict) else None; s=get_server(sid) if sid else None
        if not u or not s or u['id'] not in s.get('members',[]) or not any(c['id']==rid for c in s.get('channels',[])): return emit('error',{'error':'Unauthorized room'})
        join_room(f'{sid}:{rid}'); emit('chat-history',{'room_id':rid,'messages':[m for m in get_messages(sid) if m.get('room_id')==rid]})
    @socketio.on('send-chat-message')
    def send_message(d):
        u=current_user(); sid=d.get('server_id') if isinstance(d,dict) else None; rid=d.get('room_id') if isinstance(d,dict) else None; text=d.get('message','') if isinstance(d,dict) else ''; s=get_server(sid) if sid else None
        if not u or not s or u['id'] not in s.get('members',[]) or not any(c['id']==rid for c in s.get('channels',[])): return emit('error',{'error':'Unauthorized message'})
        text=text.strip()
        if not text or len(text)>MAX_MESSAGE_LENGTH: return emit('error',{'error':'Message must be 1-2000 characters'})
        m={'id':new_id(),'sender_id':u['id'],'username':u['username'],'message':text,'timestamp':datetime.now(timezone.utc).isoformat(),'room_id':rid}; messages=get_messages(sid); messages.append(m); save_messages(sid,messages); emit('chat-message',m,to=f'{sid}:{rid}')
    @socketio.on('typing')
    def typing(d):
        u=current_user(); sid=d.get('server_id') if isinstance(d,dict) else None; rid=d.get('room_id') if isinstance(d,dict) else None
        if u: emit('typing',{'username':u['username']},to=f'{sid}:{rid}',include_self=False)
    @socketio.on('stop-typing')
    def stop_typing(d):
        u=current_user(); sid=d.get('server_id') if isinstance(d,dict) else None; rid=d.get('room_id') if isinstance(d,dict) else None
        if u: emit('stop-typing',{},to=f'{sid}:{rid}',include_self=False)
