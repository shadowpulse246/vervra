from flask import Flask, send_from_directory
from flask_socketio import SocketIO
from . import config
from .routes import api
from .socket_handlers import register_socket_events
from .storage import ensure_storage

socketio=SocketIO(cors_allowed_origins='*', async_mode='threading')
def create_app(test_config=None):
    app=Flask(__name__, static_folder=None); app.config.update(SECRET_KEY=config.SECRET_KEY)
    if test_config: app.config.update(test_config)
    ensure_storage(); app.register_blueprint(api)
    @app.get('/')
    def index(): return send_from_directory(str(config.BASE_DIR/'public'), 'index.html')
    @app.get('/<path:path>')
    def assets(path): return send_from_directory(str(config.BASE_DIR/'public'), path)
    socketio.init_app(app); register_socket_events(socketio); return app
app=create_app()
