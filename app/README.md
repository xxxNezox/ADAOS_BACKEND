├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── models.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── rasa.py
│   │   └── whisper.py
│   └── utils/
│       ├── __init__.py
│       └── server_error_handler.py

└── .env
```
SQLALCHEMY_DATABASE_URL="sqlite+aiosqlite:///./db.sqlite3"
WHISPER_SERVER_URL="http://localhost:8001/transcribe"
RASA_SERVER_URL="http://localhost:5005/webhooks/rest/webhook"
```