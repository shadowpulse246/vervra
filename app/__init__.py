from flask import Flask, send_from_directory
from flask_socketio import SocketIO

from . import config
from .routes import api
from .socket_handlers import register_socket_events
from .storage import ensure_storage

socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")
_events_registered = False

def create_app(test_config=None):
    """Create the Flask application without depending on the current directory."""
    global _events_registered
    app = Flask(__name__, static_folder=None)
    app.config.update(SECRET_KEY=config.SECRET_KEY)
    if test_config:
        app.config.update(test_config)
    ensure_storage()
    app.register_blueprint(api)

    @app.get("/")
    def index():
        return send_from_directory(str(config.PUBLIC_DIR), "index.html")

    @app.get("/<path:path>")
    def assets(path):
        return send_from_directory(str(config.PUBLIC_DIR), path)

    socketio.init_app(app)
    if not _events_registered:
        register_socket_events(socketio)
        _events_registered = True
    return app

app = create_app()
