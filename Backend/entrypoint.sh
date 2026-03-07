#!/usr/bin/env bash
set -e

echo "Waiting for DB..."
python - <<'PY'
import os
import time
from sqlalchemy import create_engine, text

db_url = os.environ["DATABASE_URL"]
engine = create_engine(db_url, pool_pre_ping=True)

for _ in range(60):
    try:
        with engine.connect() as c:
            c.execute(text("SELECT 1"))
        print("DB OK")
        break
    except Exception:
        time.sleep(1)
else:
    raise SystemExit("DB not ready")
PY

echo "Running migrations..."
if alembic upgrade head; then
  echo "Migrations OK"
else
  echo "Alembic failed."
fi

echo "Ensuring tables exist..."
python -c "
from app.db.session import engine
from app.models import Base
Base.metadata.create_all(bind=engine)
print('Tables OK')
"

echo "Starting API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000