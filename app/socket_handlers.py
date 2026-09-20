from datetime import datetime, timezone
from flask_socketio import emit, join_room
from .auth import current_user
from .config import MAX_MESSAGE_LENGTH
from .storage import get_messages, get_server, new_id, save_messages

def _context(data):
    if not isinstance(data, dict): return None, None, None
    return data.get("server_id"), data.get("room_id"), get_server(data.get("server_id"))

def _authorized(user, server, room_id=None):
    return bool(user and server and user["id"] in server.get("members", []) and
                (room_id is None or any(c.get("id") == room_id for c in server.get("channels", []))))

def register_socket_events(socketio):
    @socketio.on("join-server")
    def join_server(data):
        user = current_user(); server_id, _, server = _context(data)
        if not _authorized(user, server): return emit("error", {"error": "Unauthorized server"})
        join_room(server_id); emit("server-joined", {"server_id": server_id})

    @socketio.on("join-room")
    def join_channel(data):
        user = current_user(); server_id, room_id, server = _context(data)
        if not _authorized(user, server, room_id): return emit("error", {"error": "Unauthorized room"})
        join_room(f"{server_id}:{room_id}")
        history = [m for m in get_messages(server_id) if m.get("room_id") == room_id]
        emit("chat-history", {"room_id": room_id, "messages": history})

    @socketio.on("send-chat-message")
    def send_message(data):
        user = current_user(); server_id, room_id, server = _context(data)
        text = data.get("message", "") if isinstance(data, dict) else ""
        if not _authorized(user, server, room_id): return emit("error", {"error": "Unauthorized message"})
        if not isinstance(text, str): return emit("error", {"error": "Message must be text"})
        text = text.strip()
        if not text or len(text) > MAX_MESSAGE_LENGTH: return emit("error", {"error": "Message must be 1-2000 characters"})
        message = {"id": new_id(), "sender_id": user["id"], "username": user["username"], "message": text,
                   "timestamp": datetime.now(timezone.utc).isoformat(), "room_id": room_id}
        messages = get_messages(server_id); messages.append(message); save_messages(server_id, messages)
        emit("chat-message", message, to=f"{server_id}:{room_id}")

    @socketio.on("typing")
    def typing(data):
        user = current_user(); server_id, room_id, server = _context(data)
        if _authorized(user, server, room_id): emit("typing", {"username": user["username"]}, to=f"{server_id}:{room_id}", include_self=False)

    @socketio.on("stop-typing")
    def stop_typing(data):
        user = current_user(); server_id, room_id, server = _context(data)
        if _authorized(user, server, room_id): emit("stop-typing", {}, to=f"{server_id}:{room_id}", include_self=False)
