"""Entry point for YouthFinanceBot backend server."""
import os
from dotenv import load_dotenv
load_dotenv()  # Must be BEFORE any module that reads env vars (e.g., GROQ_API_KEY)

from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(
        host="localhost",
        port=int(os.getenv("BACKEND_PORT", "8000")),
        use_reloader=False
    )
