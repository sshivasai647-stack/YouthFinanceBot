"""Entry point for YouthFinanceBot backend server."""
import os
from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(
        host="localhost",
        port=int(os.getenv("BACKEND_PORT", "8000")),
        use_reloader=False
    )
