"""
TEST COMPREHENSIVE SYSTEM - DEMONSTRATE ALL MODULES WORKING
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback

# Test imports - only import what we can actually import
try:
    from analyzer import analyze_spending
    analyzer_available = True
except:
    analyzer_available = False

try:
    from debt_handler import calculate_debt_burden, calculate_emi
    debt_available = True
except:
    debt_available = False

try:
    from mental_health_gaurdian import assess_mental_health
    mental_health_available = True
except:
    mental_health_available = False

try:
    from ml_model import get_trend
    ml_available = True
except:
    ml_available = False

try:
    from llm_engine import get_quick_tip
    llm_available = True
except:
    llm_available = False

app = Flask(__name__)

# Enable CORS globally
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

@app.route('/api/health', methods=['GET'])
def health_check():
    modules = []
    if analyzer_available:
        modules.append("analyzer")
    if debt_available:
        modules.append("debt_handler")
    if mental_health_available:
        modules.append("mental_health_gaurdian")
    if ml_available:
        modules.append("ml_model")
    if llm_available:
        modules.append("llm_engine")
    
    return jsonify({
        "status": "healthy",
        "modules_loaded": modules,
        "total_modules": len(modules)
    }), 200

@app.route('/api/test/spending', methods=['POST'])
def test_spending():
    try:
        if not analyzer_available:
            return jsonify({"error": "Analyzer module not available"}), 500
            
        data = request.get_json() or {}
        income = data.get('income', 50000)
        expenses = data.get('expenses', {'food': 5000, 'transport': 2000})
        
        result = analyze_spending(income, expenses)
        return jsonify({"success": True, "result": result}), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/test/debt', methods=['POST'])
def test_debt():
    try:
        if not debt_available:
            return jsonify({"error": "Debt handler module not available"}), 500
            
        data = request.get_json() or {}
        income = data.get('income', 50000)
        debts = data.get('debts', [{'name': 'Personal Loan', 'balance': 100000, 'interest_rate': 12, 'emi': 5000}])
        
        result = calculate_debt_burden(income, debts)
        return jsonify({"success": True, "result": result}), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/test/mental-health', methods=['POST'])
def test_mental_health():
    try:
        if not mental_health_available:
            return jsonify({"error": "Mental health module not available"}), 500
            
        data = request.get_json() or {}
        user_input = data.get('user_input', 'I am feeling stressed about my finances')
        
        result = assess_mental_health(user_input)
        return jsonify({"success": True, "result": str(result)}), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/test/ml-trend', methods=['POST'])
def test_ml_trend():
    try:
        if not ml_available:
            return jsonify({"error": "ML module not available"}), 500
            
        data = request.get_json() or {}
        financial_history = data.get('financial_history', [1000, 1200, 1100, 1300, 1400])
        
        result = get_trend(financial_history)
        return jsonify({"success": True, "result": result}), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/test/llm-tip', methods=['GET'])
def test_llm_tip():
    try:
        if not llm_available:
            return jsonify({"error": "LLM module not available"}), 500
            
        category = request.args.get('category', 'investment')
        result = get_quick_tip(category)
        return jsonify({"success": True, "result": result}), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

if __name__ == '__main__':
    print("🚀 Starting Comprehensive Test Server...")
    print("📊 Available Modules:")
    print(f"   ✅ Analyzer: {analyzer_available}")
    print(f"   ✅ Debt Handler: {debt_available}")
    print(f"   ✅ Mental Health: {mental_health_available}")
    print(f"   ✅ ML Model: {ml_available}")
    print(f"   ✅ LLM Engine: {llm_available}")
    print("🌐 Server running on http://127.0.0.1:5000")
    print("🔗 Test endpoints:")
    print("   GET  /api/health - Check system status")
    print("   POST /api/test/spending - Test spending analysis")
    print("   POST /api/test/debt - Test debt analysis")
    print("   POST /api/test/mental-health - Test mental health")
    print("   POST /api/test/ml-trend - Test ML trend analysis")
    print("   GET  /api/test/llm-tip - Test LLM quick tip")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
