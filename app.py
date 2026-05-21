from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify
from flask_cors import CORS
from backend.comprehensive_routes import comprehensive_bp

app = Flask(__name__)
CORS(app, origins=["http://localhost:8000", "http://127.0.0.1:8000"])

app.register_blueprint(comprehensive_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
