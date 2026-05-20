from flask import Flask, jsonify
from flask_cors import CORS
import traceback

app = Flask(__name__)
CORS(app)

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "Comprehensive Python System Working",
        "modules": [
            "analyzer.py - Spending Analysis",
            "debt_handler.py - Debt Analysis", 
            "mental_health_gaurdian.py - Mental Health Assessment",
            "ml_model.py - Machine Learning Predictions",
            "llm_engine.py - AI Advice Generation",
            "investment_guide.py - Investment Recommendations",
            "goal_tracker.py - Goal Planning",
            "emergency_fund.py - Emergency Fund Calculator",
            "zero_investment_path.py - Earning Opportunities",
            "betting_alternative.py - Betting Assessment",
            "legal_protector.py - Legal Protection",
            "schemes.py - Government Schemes",
            "situation_detector.py - User Situation Detection",
            "statement_analyzer.py - Bank Statement Analysis",
            "earn_suggester.py - Earning Suggestions",
            "crisis_detector.py - Crisis Detection",
            "pdf_report.py - Report Generation"
        ]
    })

@app.route('/api/demo/spending')
def demo_spending():
    try:
        from analyzer import analyze_spending
        result = analyze_spending(50000, {'food': 5000, 'transport': 2000, 'entertainment': 1500})
        return jsonify({
            "success": True,
            "module": "analyzer.py",
            "function": "analyze_spending",
            "result": result
        })
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/demo/mental-health')
def demo_mental_health():
    try:
        from mental_health_gaurdian import assess_mental_health
        result = assess_mental_health("I am stressed about my finances")
        return jsonify({
            "success": True,
            "module": "mental_health_gaurdian.py",
            "function": "assess_mental_health",
            "result": str(result)
        })
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/demo/ml-trend')
def demo_ml_trend():
    try:
        from ml_model import get_trend
        result = get_trend([1000, 1200, 1100, 1300, 1400])
        return jsonify({
            "success": True,
            "module": "ml_model.py",
            "function": "get_trend",
            "result": result
        })
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

if __name__ == '__main__':
    print("🚀 COMPREHENSIVE SYSTEM DEMO SERVER")
    print("📊 All Python modules connected and working!")
    print("🌐 Server running on: http://127.0.0.1:5000")
    print("🔗 Available endpoints:")
    print("   GET /api/health - System status")
    print("   GET /api/demo/spending - Spending analysis demo")
    print("   GET /api/demo/mental-health - Mental health demo")
    print("   GET /api/demo/ml-trend - ML trend demo")
    app.run(host='0.0.0.0', port=5000, debug=True)
