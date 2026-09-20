# Vervra

A lightweight Discord-style community chat MVP using Flask, Flask-SocketIO, vanilla JavaScript, and JSON persistence.

```bash
python -m pip install -r requirements.txt
python server.py
```

Open http://localhost:3000. `PORT` overrides the default port of 3000. Data is stored under `data/` and is never cleared on startup.

Run tests with `python -m unittest discover -s tests -v`.
