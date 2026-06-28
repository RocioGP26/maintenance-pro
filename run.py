"""Punto de entrada para Mantis."""
import os

from app import create_app, db

app = create_app()

if __name__ == "__main__":
    debug = os.environ.get("FLASK_ENV", "development") != "production"
    app.run(debug=debug, host="0.0.0.0", port=5000)
