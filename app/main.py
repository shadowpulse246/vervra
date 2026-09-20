"""Application entrypoint for WSGI imports and local development."""
from . import app, socketio, create_app

__all__ = ["app", "socketio", "create_app"]
