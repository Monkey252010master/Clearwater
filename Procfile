web: cd website/backend && python3 -m gunicorn app:app --bind 0.0.0.0:$PORT
release: cd website/backend && python3 -c "from app import db; db.create_all()"