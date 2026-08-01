web: gunicorn --worker-class gthread --workers 1 --threads 8 --timeout 120 --graceful-timeout 30 run:app
release: python scripts/migrate_deploy.py
