# API Package

## Local development

```bash
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -e .[test]
alembic upgrade head
python -m healthos_api.cli create-admin --email you@example.com --password "change-me"
uvicorn healthos_api.main:app --reload
```

The private v1 has no public registration endpoint. Create the first user through the CLI, then use `POST /auth/login`.
