web: flask db upgrade && gunicorn --worker-class sync --workers 1 --timeout 60 --bind 0.0.0.0:$PORT run:app
