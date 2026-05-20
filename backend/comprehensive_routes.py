"""
COMPREHENSIVE FLASK ROUTES - ALL PYTHON MODULES CONNECTED
This file systematically imports and exposes ALL data processing modules as API endpoints.
"""

from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import traceback
from typing import Dict, Any, Optional
import json
# Import ALL Python modules that process data
from analyzer import analyze_spending, get_saving_tip
from betting_alternative import assess_betting_behavior, run_betting_alternative
from crisis_detector import detect_crisis
from debt_handler import (
    Debt, DebtType, calculate_debt_burden, calculate_emi, 
    create_repayment_plan, prioritize_debts, detect_debt_trap,
    get_legal_protection_info
)
from emergency_fund import calculate_emergency_fund, get_building_plan, get_emergency_tip
from earn_suggester import suggest_earning
from goal_tracker import create_goal, check_progress, GoalOptimizer
from investment_guide import (
    assess_investment_readiness, recommend_investments, 
    calculate_investment_growth, create_investment_plan,
    get_government_schemes, detect_investment_scams
)
from legal_protector import assess_legal_situation, get_legal_protection_info, run_legal_protector
from llm_engine import get_advice, get_quick_tip, get_llm_client, build_messages_with_history, generate_with_retry, DEFAULT_MODEL
from mental_health_gaurdian import (
    assess_mental_health, handle_followup, get_crisis_level_from_string, 
    run_mental_health_guardian
)
from ml_model import (
    calculate_financial_features, train_model, save_model, load_model,
    predict_future_with_ci, calculate_risk_score, get_trend
)
# PDF generation imported locally in route
from schemes import get_relevant_schemes, match_scheme
from situation_detector import (
    detect_situation, route_user,
    PATH_BETTING, PATH_DEBT, PATH_EXPENSE, PATH_INVEST,
    PATH_LEGAL, PATH_ZERO_INVESTMENT, PATH_MENTAL_HEALTH, PATH_UNKNOWN
)
from statement_analyzer import (
    parse_statement_lines, analyze_statement, summarize_transactions, 
    run_statement_analyzer
)
from zero_investment_path import (
    handle_zero_investment_path, get_zero_investment_opportunities,
    create_earning_plan, get_skill_building_path, filter_by_investment_level,
    filter_by_category, get_opportunity_by_title
)
from chat_router import ChatRouter, UserContext, ResponseType
from financial_engine import get_financial_snapshot

# Create comprehensive blueprint
comprehensive_bp = Blueprint('comprehensive', __name__)

def handle_error(func_name: str, error: Exception) -> Dict[str, Any]:
    """Standard error handling for all endpoints"""
    return {
        "error": f"{func_name} failed",
        "details": str(error),
        "traceback": traceback.format_exc()
    }, 500

def validate_json_data() -> Dict[str, Any]:
    """Validate and return JSON data from request"""
    try:
        data = request.get_json() or {}
        return data
    except Exception as e:
        raise ValueError(f"Invalid JSON data: {str(e)}")

# ====================================================================
# ANALYZER MODULE ROUTES
# ====================================================================

@comprehensive_bp.route('/api/analyze/spending', methods=['POST'])
def analyze_spending_route():
    try:
        data = validate_json_data()
        income = data.get('income', 0)
        expenses = data.get('expenses', {})
        result = analyze_spending(income, expenses)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("analyze_spending", e)

@comprehensive_bp.route('/api/analyze/saving-tip', methods=['GET'])
def get_saving_tip_route():
    try:
        tip = get_saving_tip()
        return jsonify({"tip": tip}), 200
    except Exception as e:
        return handle_error("get_saving_tip", e)

# ====================================================================
# BETTING ALTERNATIVE MODULE ROUTES
# ====================================================================

@comprehensive_bp.route('/api/betting/assess', methods=['POST'])
def assess_betting_behavior_route():
    try:
        data = validate_json_data()
        user_input = data.get('user_input', '')
        result = assess_betting_behavior(user_input)
        # Convert dataclass to dict, then convert any enum values to strings
        if hasattr(result, '__dataclass_fields__'):
            result = {k: (v.value if hasattr(v, 'value') else v) 
                     for k, v in result.__dict__.items()}
        elif isinstance(result, dict):
            result = {k: (v.value if hasattr(v, 'value') else v) 
                     for k, v in result.items()}
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("assess_betting_behavior", e)
    
@comprehensive_bp.route('/api/betting/run', methods=['POST'])
def run_betting_alternative_route():
    try:
        data = validate_json_data()
        user_input = data.get('user_input', '')
        user_profile = data.get('user_profile', {})
        result = run_betting_alternative(user_input, user_profile)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("run_betting_alternative", e)

# ====================================================================
# CRISIS DETECTOR MODULE ROUTES
# ====================================================================

@comprehensive_bp.route('/api/crisis/detect', methods=['POST'])
def detect_crisis_route():
    try:
        data = validate_json_data()
        text = data.get('text', '')
        result = detect_crisis(text)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("detect_crisis", e)

# ====================================================================
# DEBT HANDLER MODULE ROUTES
# ====================================================================

@comprehensive_bp.route('/api/debt/calculate-burden', methods=['POST'])
def calculate_debt_burden_route():
    try:
        data = validate_json_data()
        income = data.get('income', 0)
        total_debt = data.get('total_debt', 0)
        monthly_emi = data.get('monthly_emi', 0)
        result = calculate_debt_burden(income, total_debt, monthly_emi)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("calculate_debt_burden", e)

@comprehensive_bp.route('/api/debt/calculate-emi', methods=['POST'])
def calculate_emi_route():
    try:
        data = validate_json_data()
        principal = data.get('principal', 0)
        annual_interest_rate = data.get('annual_interest_rate', 0)
        tenure_months = data.get('tenure_months', 0)
        result = calculate_emi(principal, annual_interest_rate, tenure_months)
        return jsonify({"emi": result}), 200
    except Exception as e:
        return handle_error("calculate_emi", e)

@comprehensive_bp.route('/api/debt/create-repayment-plan', methods=['POST'])
def create_repayment_plan_route():
    try:
        data = validate_json_data()
        income = data.get('income', 0)
        expenses = data.get('expenses', 0)
        debt_list_raw = data.get('debts', [])
        strategy = data.get('strategy', 'avalanche')
        debt_list = []
        for d in debt_list_raw:
            debt_obj = Debt(
                name          = d.get('name', 'Unknown'),
                debt_type     = DebtType(d.get('debt_type', 'Personal Loan')),
                principal     = d.get('principal', 0),
                interest_rate = d.get('interest_rate', 0),
                monthly_emi   = d.get('monthly_emi', None),
                lender        = d.get('lender', ''),
                collateral    = d.get('collateral', ''),
                informal      = d.get('informal', False),
            )
            debt_list.append(debt_obj)
        result = create_repayment_plan(income, expenses, debt_list, strategy)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("create_repayment_plan", e)

@comprehensive_bp.route('/api/debt/prioritize', methods=['POST'])
def prioritize_debts_route():
    try:
        data = validate_json_data()
        debt_list_raw = data.get('debt_list', [])
        method = data.get('method', 'auto')
        # Convert dicts to Debt objects
        debt_list = []
        for d in debt_list_raw:
            debt_obj = Debt(
                name          = d.get('name', 'Unknown'),
                debt_type     = DebtType(d.get('debt_type', 'Personal Loan')),
                principal     = d.get('principal', 0),
                interest_rate = d.get('interest_rate', 0),
                monthly_emi   = d.get('monthly_emi', None),
                lender        = d.get('lender', ''),
                collateral    = d.get('collateral', ''),
                informal      = d.get('informal', False),
            )
            debt_list.append(debt_obj)
        result = prioritize_debts(debt_list, method)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("prioritize_debts", e)

@comprehensive_bp.route('/api/debt/detect-trap', methods=['POST'])
def detect_debt_trap_route():
    try:
        data = validate_json_data()
        debt_history = data.get('debt_history', [])
        income = data.get('income', 0)
        result = detect_debt_trap(debt_history, income)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("detect_debt_trap", e)

@comprehensive_bp.route('/api/debt/legal-protection-info', methods=['GET'])
def get_debt_legal_protection_info_route():
    try:
        result = get_legal_protection_info()
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("get_legal_protection_info", e)

# ====================================================================
# EMERGENCY FUND MODULE ROUTES
# ====================================================================

@comprehensive_bp.route('/api/emergency-fund/calculate', methods=['POST'])
def calculate_emergency_fund_route():
    try:
        data = validate_json_data()
        monthly_expenses = data.get('monthly_expenses', 0)
        dependents = data.get('dependents', 0)
        result = calculate_emergency_fund(monthly_expenses, dependents)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("calculate_emergency_fund", e)

@comprehensive_bp.route('/api/emergency-fund/building-plan', methods=['POST'])
def get_building_plan_route():
    try:
        data = validate_json_data()
        current_savings = data.get('current_savings', 0)
        target_amount = data.get('target_amount', 0)
        monthly_contribution = data.get('monthly_contribution', 0)
        result = get_building_plan(current_savings, target_amount, monthly_contribution)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("get_building_plan", e)

@comprehensive_bp.route('/api/emergency-fund/tip', methods=['GET'])
def get_emergency_tip_route():
    try:
        savings_rate = float(request.args.get('savings_rate', 0))
        tip = get_emergency_tip(savings_rate)
        return jsonify({"tip": tip}), 200
    except Exception as e:
        return handle_error("get_emergency_tip", e)

# ====================================================================
# EARN SUGGESTER MODULE ROUTES
# ====================================================================

@comprehensive_bp.route('/api/earn/suggest', methods=['POST'])
def suggest_earning_route():
    try:
        data = validate_json_data()
        user_profile = data.get('user_profile', {})
        result = suggest_earning(user_profile)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("suggest_earning", e)

# ====================================================================
# GOAL TRACKER MODULE ROUTES
# ====================================================================

@comprehensive_bp.route('/api/goals/create', methods=['POST'])
def create_goal_route():
    try:
        data = validate_json_data()
        goal_data = data.get('goal_data', {})
        result = create_goal(goal_data)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("create_goal", e)

@comprehensive_bp.route('/api/goals/check-progress', methods=['POST'])
def check_progress_route():
    try:
        data = validate_json_data()
        goal_id = data.get('goal_id', '')
        current_amount = data.get('current_amount', 0)
        result = check_progress(goal_id, current_amount)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("check_progress", e)

@comprehensive_bp.route('/api/goals/optimize', methods=['POST'])
def optimize_goals_route():
    try:
        data = validate_json_data()
        annual_inflation = data.get('annual_inflation', 0.05)
        investment_return = data.get('investment_return', 0.08)
        optimizer = GoalOptimizer(annual_inflation, investment_return)
        # Use optimizer to calculate for each goal
        goals = data.get('goals', [])
        results = []
        for goal in goals:
            present_cost = goal.get('present_cost', 0)
            months = goal.get('months', 12)
            future_value = optimizer.inflation_adjusted_target(present_cost, months)
            monthly_savings = optimizer.required_monthly_savings(future_value, months)
            results.append({
                "goal": goal.get('name', 'Goal'),
                "future_value": round(future_value, 2),
                "monthly_savings_needed": round(monthly_savings, 2),
            })
        return jsonify({"result": results}), 200
    except Exception as e:
        return handle_error("optimize_goals", e)

# ====================================================================
# INVESTMENT GUIDE MODULE ROUTES
# ====================================================================

@comprehensive_bp.route('/api/investment/assess-readiness', methods=['POST'])
def assess_investment_readiness_route():
    try:
        data = validate_json_data()
        user_profile = data.get('user_profile', {})
        result = assess_investment_readiness(user_profile)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("assess_investment_readiness", e)

@comprehensive_bp.route('/api/investment/recommend', methods=['POST'])
def recommend_investments_route():
    try:
        data = validate_json_data()
        user_profile = data.get('user_profile', {})
        result = recommend_investments(user_profile)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("recommend_investments", e)

@comprehensive_bp.route('/api/investment/calculate-growth', methods=['POST'])
def calculate_investment_growth_route():
    try:
        data = validate_json_data()
        principal = data.get('principal', 0)
        annual_rate = data.get('annual_rate', 0)
        years = data.get('years', 0)
        result = calculate_investment_growth(principal, annual_rate, years)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("calculate_investment_growth", e)

@comprehensive_bp.route('/api/investment/create-plan', methods=['POST'])
def create_investment_plan_route():
    try:
        data = validate_json_data()
        user_profile = data.get('user_profile', {})
        goals = data.get('goals', [])
        result = create_investment_plan(user_profile, goals)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("create_investment_plan", e)

@comprehensive_bp.route('/api/investment/government-schemes', methods=['GET'])
def get_government_schemes_route():
    try:
        result = get_government_schemes()
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("get_government_schemes", e)

@comprehensive_bp.route('/api/investment/detect-scams', methods=['POST'])
def detect_investment_scams_route():
    try:
        data = validate_json_data()
        investment_description = data.get('investment_description', '')
        result = detect_investment_scams(investment_description)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("detect_investment_scams", e)

# ====================================================================
# LEGAL PROTECTOR MODULE ROUTES
# ====================================================================

@comprehensive_bp.route('/api/legal/assess-situation', methods=['POST'])
def assess_legal_situation_route():
    try:
        data = validate_json_data()
        user_input = data.get('user_input', '')
        result = assess_legal_situation(user_input)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("assess_legal_situation", e)

@comprehensive_bp.route('/api/legal/protection-info', methods=['GET'])
def get_legal_protection_info_route():
    try:
        result = get_legal_protection_info()
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("get_legal_protection_info", e)

@comprehensive_bp.route('/api/legal/run-protector', methods=['POST'])
def run_legal_protector_route():
    try:
        data = validate_json_data()
        user_input = data.get('user_input', '')
        user_profile = data.get('user_profile', {})
        result = run_legal_protector(user_input, user_profile)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("run_legal_protector", e)

# ====================================================================
# LLM ENGINE MODULE ROUTES
# ====================================================================

@comprehensive_bp.route('/api/llm/get-advice', methods=['POST'])
def get_advice_route():
    try:
        data = validate_json_data()
        prompt = data.get('prompt', '')
        context = data.get('context', '')
        result = get_advice(prompt, context)
        return jsonify({"advice": result}), 200
    except Exception as e:
        return handle_error("get_advice", e)

@comprehensive_bp.route('/api/llm/quick-tip', methods=['GET'])
def get_quick_tip_route():
    try:
        category = request.args.get('category', 'general')
        tip = get_quick_tip(category)
        return jsonify({"tip": tip}), 200
    except Exception as e:
        return handle_error("get_quick_tip", e)

@comprehensive_bp.route('/api/llm/get-client', methods=['GET'])
def get_llm_client_route():
    try:
        provider = request.args.get('provider', 'groq')
        client = get_llm_client(provider)
        return jsonify({"client": str(client)}), 200
    except Exception as e:
        return handle_error("get_llm_client", e)

# ====================================================================
# MENTAL HEALTH GUARDIAN MODULE ROUTES
# ====================================================================

@comprehensive_bp.route('/api/mental-health/assess', methods=['POST'])
def assess_mental_health_route():
    try:
        data = validate_json_data()
        user_input = data.get('user_input', '')
        result = assess_mental_health(user_input)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("assess_mental_health", e)

@comprehensive_bp.route('/api/mental-health/handle-followup', methods=['POST'])
def handle_followup_route():
    try:
        data = validate_json_data()
        user_input = data.get('user_input', '')
        crisis_level = data.get('crisis_level', 'stable')
        result = handle_followup(user_input, crisis_level)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("handle_followup", e)

@comprehensive_bp.route('/api/mental-health/run-guardian', methods=['POST'])
def run_mental_health_guardian_route():
    try:
        data = validate_json_data()
        user_input = data.get('user_input', '')
        result = run_mental_health_guardian(user_input)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("run_mental_health_guardian", e)

@comprehensive_bp.route('/api/mental-health/get-crisis-level', methods=['GET'])
def get_crisis_level_from_string_route():
    try:
        level_str = request.args.get('level_str', 'stable')
        result = get_crisis_level_from_string(level_str)
        return jsonify({"crisis_level": str(result)}), 200
    except Exception as e:
        return handle_error("get_crisis_level_from_string", e)

# ====================================================================
# ML MODEL MODULE ROUTES
# ====================================================================

@comprehensive_bp.route('/api/ml/calculate-features', methods=['POST'])
def calculate_financial_features_route():
    try:
        data = validate_json_data()
        debt_amount = data.get('debt_amount', 0)
        income = data.get('income', 0)
        expenses = data.get('expenses', 0)
        total_assets = data.get('total_assets', None)
        result = calculate_financial_features(debt_amount, income, expenses, total_assets)
        return jsonify({"features": result}), 200
    except Exception as e:
        return handle_error("calculate_financial_features", e)

@comprehensive_bp.route('/api/ml/train-model', methods=['POST'])
def train_model_route():
    try:
        data = validate_json_data()
        financial_history = data.get('financial_history', [])
        model, r2_score = train_model(financial_history)
        return jsonify({"model_trained": True, "r2_score": r2_score}), 200
    except Exception as e:
        return handle_error("train_model", e)

@comprehensive_bp.route('/api/ml/save-model', methods=['POST'])
def save_model_route():
    try:
        data = validate_json_data()
        model = data.get('model', None)
        path = data.get('path', 'default_model.pkl')
        save_model(model, path)
        return jsonify({"model_saved": True, "path": path}), 200
    except Exception as e:
        return handle_error("save_model", e)

@comprehensive_bp.route('/api/ml/load-model', methods=['GET'])
def load_model_route():
    try:
        path = request.args.get('path', 'default_model.pkl')
        model = load_model(path)
        return jsonify({"model_loaded": True, "model": str(model)}), 200
    except Exception as e:
        return handle_error("load_model", e)

@comprehensive_bp.route('/api/ml/predict-future', methods=['POST'])
def predict_future_with_ci_route():
    try:
        data = validate_json_data()
        history = data.get('history', [])
        current_months = data.get('current_months', len(history))
        months_ahead = data.get('months_ahead', 3)
        # If not enough data, return empty predictions instead of erroring
        if len(history) < 3:
            return jsonify({"predictions": [], "message": "Need at least 3 months of data for predictions"}), 200
        model, _ = train_model(history)
        result = predict_future_with_ci(model, current_months, months_ahead, history)
        return jsonify({"predictions": result}), 200
    except Exception as e:
        return handle_error("predict_future_with_ci", e)
@comprehensive_bp.route('/api/ml/calculate-risk-score', methods=['POST'])
def calculate_risk_score_route():
    try:
        data = validate_json_data()
        financial_features = data.get('financial_features', {})
        result = calculate_risk_score(financial_features)
        return jsonify({"risk_score": result}), 200
    except Exception as e:
        return handle_error("calculate_risk_score", e)

@comprehensive_bp.route('/api/ml/get-trend', methods=['POST'])
def get_trend_route():
    try:
        data = validate_json_data()
        financial_history = data.get('financial_history', [])
        result = get_trend(financial_history)
        return jsonify({"trend": result}), 200
    except Exception as e:
        return handle_error("get_trend", e)

# ====================================================================
# PDF REPORT MODULE ROUTES
# ====================================================================

@comprehensive_bp.route('/api/report/generate', methods=['POST'])
def generate_report_route():
    try:
        data = request.get_json() or {}
        
        income = float(data.get('income', 0))
        expenses = float(data.get('expenses', 0))
        savings_rate = float(data.get('savings_rate', 0))
        total_debt = float(data.get('total_debt', 0))
        savings = max(income - expenses, 0)
        
        from financial_engine import calculate_survival_days, calculate_financial_health_score
        survival_days = calculate_survival_days(savings, expenses)
        health_score = calculate_financial_health_score(savings_rate, total_debt, income, survival_days)
        
        # Get Schemes
        from schemes import get_relevant_schemes
        user_profile = {"income": income, "age": data.get('age', 22)} # default age
        schemes_raw = get_relevant_schemes(user_profile, top_n=3)
        schemes = [{"name": s.get("name"), "benefit": s.get("benefit"), "apply_link": s.get("link")} for s in schemes_raw]

        report_payload = {
            "income": income,
            "expenses": expenses,
            "health_score": health_score,
            "survival_days": survival_days,
            "debt_free_date": data.get("debt_free_date"),
            "blacklist_warnings": data.get("blacklist_warnings", []),
            "schemes": schemes
        }
        
        from backend.modules.pdf_report import generate_report
        pdf_bytes = generate_report(report_payload)
        
        from flask import send_file
        from io import BytesIO
        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='Financial_Report.pdf'
        )
    except Exception as e:
        return handle_error("generate_report", e)

# ====================================================================
# SCHEMES MODULE ROUTES
# ====================================================================

@comprehensive_bp.route('/api/schemes/get-relevant', methods=['POST'])
def get_relevant_schemes_route():
    try:
        data = validate_json_data()
        user = data.get('user', {})
        result = get_relevant_schemes(user)
        return jsonify({"schemes": result}), 200
    except Exception as e:
        return handle_error("get_relevant_schemes", e)

@comprehensive_bp.route('/api/schemes/match-scheme', methods=['POST'])
def match_scheme_route():
    try:
        data = validate_json_data()
        user = data.get('user', {})
        scheme = data.get('scheme', {})
        result = match_scheme(user, scheme)
        return jsonify({"match_score": result}), 200
    except Exception as e:
        return handle_error("match_scheme", e)

# ====================================================================
# SITUATION DETECTOR MODULE ROUTES
# ====================================================================

@comprehensive_bp.route('/api/situation/detect', methods=['POST'])
def detect_situation_route():
    try:
        data = validate_json_data()
        user_input = data.get('user_input', '')
        result = detect_situation(user_input)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("detect_situation", e)

@comprehensive_bp.route('/api/situation/route-user', methods=['POST'])
def route_user_route():
    try:
        data = validate_json_data()
        user_input = data.get('user_input', '')
        result = route_user(user_input)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("route_user", e)

# ====================================================================
# STATEMENT ANALYZER MODULE ROUTES
# ====================================================================

@comprehensive_bp.route('/api/statement/parse-lines', methods=['POST'])
def parse_statement_lines_route():
    try:
        data = validate_json_data()
        lines = data.get('lines', [])
        result = parse_statement_lines(lines)
        return jsonify({"transactions": result}), 200
    except Exception as e:
        return handle_error("parse_statement_lines", e)

@comprehensive_bp.route('/api/statement/analyze', methods=['POST'])
def analyze_statement_route():
    try:
        data = validate_json_data()
        statement_text = data.get('statement_text', '')
        income = data.get('income', None)
        result = analyze_statement(statement_text, income)
        return jsonify({"analysis": result}), 200
    except Exception as e:
        return handle_error("analyze_statement", e)

@comprehensive_bp.route('/api/statement/summarize-transactions', methods=['POST'])
def summarize_transactions_route():
    try:
        data = validate_json_data()
        transactions = data.get('transactions', [])
        income = data.get('income', None)
        result = summarize_transactions(transactions, income)
        return jsonify({"summary": result}), 200
    except Exception as e:
        return handle_error("summarize_transactions", e)

@comprehensive_bp.route('/api/statement/run-analyzer', methods=['POST'])
def run_statement_analyzer_route():
    try:
        data = validate_json_data()
        statement_text = data.get('statement_text', '')
        income = data.get('income', None)
        result = run_statement_analyzer(statement_text, income)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("run_statement_analyzer", e)

# ====================================================================
# ZERO INVESTMENT PATH MODULE ROUTES
# ====================================================================

@comprehensive_bp.route('/api/zero-investment/handle-path', methods=['POST'])
def handle_zero_investment_path_route():
    try:
        data = validate_json_data()
        user_input = data.get('user_input', '')
        user_profile = data.get('user_profile', {})
        result = handle_zero_investment_path(user_input, user_profile)
        return jsonify({"result": result}), 200
    except Exception as e:
        return handle_error("handle_zero_investment_path", e)

@comprehensive_bp.route('/api/zero-investment/get-opportunities', methods=['POST'])
def get_zero_investment_opportunities_route():
    try:
        data = validate_json_data()
        user_profile = data.get('user_profile', {})
        result = get_zero_investment_opportunities(user_profile)
        return jsonify({"opportunities": result}), 200
    except Exception as e:
        return handle_error("get_zero_investment_opportunities", e)

@comprehensive_bp.route('/api/zero-investment/create-earning-plan', methods=['POST'])
def create_earning_plan_route():
    try:
        data = validate_json_data()
        user_profile = data.get('user_profile', {})
        opportunities = data.get('opportunities', [])
        result = create_earning_plan(user_profile, opportunities)
        return jsonify({"plan": result}), 200
    except Exception as e:
        return handle_error("create_earning_plan", e)

@comprehensive_bp.route('/api/zero-investment/get-skill-path', methods=['POST'])
def get_skill_building_path_route():
    try:
        data = validate_json_data()
        user_profile = data.get('user_profile', {})
        result = get_skill_building_path(user_profile)
        return jsonify({"skill_path": result}), 200
    except Exception as e:
        return handle_error("get_skill_building_path", e)

@comprehensive_bp.route('/api/zero-investment/filter-by-level', methods=['GET'])
def filter_by_investment_level_route():
    try:
        level = request.args.get('level', 'zero')
        result = filter_by_investment_level(level)
        return jsonify({"opportunities": result}), 200
    except Exception as e:
        return handle_error("filter_by_investment_level", e)

@comprehensive_bp.route('/api/zero-investment/filter-by-category', methods=['GET'])
def filter_by_category_route():
    try:
        category = request.args.get('category', 'general')
        result = filter_by_category(category)
        return jsonify({"opportunities": result}), 200
    except Exception as e:
        return handle_error("filter_by_category", e)

@comprehensive_bp.route('/api/zero-investment/get-opportunity-by-title', methods=['GET'])
def get_opportunity_by_title_route():
    try:
        title = request.args.get('title', '')
        result = get_opportunity_by_title(title)
        return jsonify({"opportunity": result}), 200
    except Exception as e:
        return handle_error("get_opportunity_by_title", e)

# ====================================================================
# UNIFIED CHAT ROUTE (MIGRATED FROM STREAMLIT)
# ====================================================================

@comprehensive_bp.route('/api/chat', methods=['POST'])
def unified_chat_route():
    try:
        data = validate_json_data()
        user_message = data.get('message', '')
        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Frontend-managed state mapped to context
        user_context_data = data.get('context', {})
        income = user_context_data.get('income', 0)
        expenses = user_context_data.get('expenses', {})
        savings_rate = user_context_data.get('savings_rate', 0.0)
        chat_history = data.get('history', [])

        # Normalize expenses for crisis detector (needs dict of str→float)
        expenses_dict = expenses if isinstance(expenses, dict) else {"total": float(expenses) if isinstance(expenses, (int, float)) else 0}

        # ──────────────────────────────────────────────────────
        # STEP 0: Crisis Detector — FIRST CHECK on every message
        # ──────────────────────────────────────────────────────
        crisis_result = detect_crisis(
            income=float(income),
            expenses={k: float(v) for k, v in expenses_dict.items()},
            debt=float(user_context_data.get('total_debt', 0)),
            text=user_message,
        )
        crisis_level = crisis_result.get("level", "Normal")

        # Build blacklist_warning if a predatory app was matched
        blacklist_warning = None
        matched_apps = crisis_result.get("matched_apps", [])
        if matched_apps:
            app = matched_apps[0]
            blacklist_warning = {
                "app": app["app_name"],
                "risk": app["primary_risk"],
                "action": app["recommended_action"]
            }

        # EMERGENCY → skip LLM entirely, return crisis hotlines
        if crisis_level == "Emergency":
            hotlines = crisis_result.get("hotlines", [])
            response_payload = {
                "message": (
                    "🚨 I'm very concerned about what you shared. Your safety is the top priority.\n\n"
                    "**Please reach out for help immediately:**\n"
                    + "\n".join(f"• {h['name']}: {h['number']} ({h['hours']})" for h in hotlines)
                    + "\n\nYou are NOT alone. Help is available right now."
                ),
                "path": PATH_MENTAL_HEALTH,
                "crisis_level": crisis_level,
                "suggested_action": "show_crisis_support",
                "alerts": crisis_result.get("alerts", []),
                "hotlines": hotlines,
            }
            if blacklist_warning:
                response_payload["blacklist_warning"] = blacklist_warning
            return jsonify(response_payload), 200

        # Build crisis_warning for Alert tier
        crisis_warning = None
        if crisis_level == "Alert":
            crisis_warning = {
                "level": "Alert",
                "alerts": crisis_result.get("alerts", []),
            }

        # ──────────────────────────────────────────────────────
        # STEP 1: Initialize ChatRouter
        # ──────────────────────────────────────────────────────
        router = ChatRouter()
        user_context = UserContext(
            income=income,
            monthly_expenses=sum(expenses_dict.values()) if isinstance(expenses_dict, dict) else 0,
            savings_rate=savings_rate,
        )
        router.set_user_context(user_context)

        # STEP 2: Detect Situation and Route
        path = router._detect_situation(user_message)
        routed_response = None
        response_type = ResponseType.GENERAL_ADVICE

        if path == PATH_DEBT:
            routed_response = router._route_to_debt_handler(user_message)
            response_type = ResponseType.DEBT_GUIDANCE
        elif path == PATH_BETTING:
            routed_response = router._route_to_betting_helper(user_message)
            response_type = ResponseType.BETTING_HELP
        elif path == PATH_ZERO_INVESTMENT:
            routed_response = router._route_to_earning_suggester(user_message)
            response_type = ResponseType.EARNING_TIP
        elif path == PATH_INVEST:
            routed_response = router._route_to_investment_guide(user_message)
            response_type = ResponseType.INVESTMENT
        elif path == PATH_LEGAL:
            routed_response = router._route_to_legal_helper(user_message)
            response_type = ResponseType.LEGAL
        elif path == PATH_MENTAL_HEALTH:
            response_type = ResponseType.MENTAL_HEALTH
        elif path == PATH_EXPENSE:
            response_type = ResponseType.EXPENSE_TRACKING
        elif path == PATH_UNKNOWN:
            response_type = ResponseType.CLARIFICATION

        # STEP 3: Generate LLM Response
        if routed_response:
            final_message = routed_response
        else:
            messages = build_messages_with_history(
                user_message=user_message,
                chat_history=chat_history,
                income=income,
                savings_rate=savings_rate
            )
            final_message = generate_with_retry(
                provider="groq",
                model=DEFAULT_MODEL,
                messages=messages
            )

        # STEP 4: Suggested UI Action
        suggested_action = None
        if path == PATH_DEBT:
            suggested_action = "show_debt_resources"
        elif path == PATH_BETTING:
            suggested_action = "show_betting_alternatives"
        elif path == PATH_LEGAL:
            suggested_action = "show_legal_protection"
        elif path == PATH_EXPENSE:
            suggested_action = "show_statement_analyzer"
        elif path == PATH_INVEST:
            suggested_action = "show_investment_plans"
        elif path == PATH_ZERO_INVESTMENT:
            suggested_action = "show_earning_ideas"

        # STEP 5: Financial Snapshot
        savings = user_context_data.get('savings', 0)
        total_debt = user_context_data.get('total_debt', 0)
        snapshot = get_financial_snapshot(
            income=income,
            expenses=sum(expenses_dict.values()) if isinstance(expenses_dict, dict) else 0,
            savings=savings,
            total_debt=total_debt
        )

        # STEP 6: Build response
        response_payload = {
            "message": final_message,
            "path": path,
            "response_type": response_type.value if hasattr(response_type, 'value') else response_type,
            "crisis_level": crisis_level,
            "suggested_action": suggested_action,
            "financial_snapshot": snapshot
        }
        if crisis_warning:
            response_payload["crisis_warning"] = crisis_warning
        if blacklist_warning:
            response_payload["blacklist_warning"] = blacklist_warning

        return jsonify(response_payload), 200

    except Exception as e:
        return handle_error("unified_chat_route", e)

# ====================================================================
# FINANCIAL ENGINE ROUTE
# ====================================================================

@comprehensive_bp.route('/api/finance/calculate', methods=['POST'])
def calculate_financials_route():
    try:
        data = validate_json_data()
        income = float(data.get('income', 0))
        expenses = float(data.get('expenses', 0))
        savings = float(data.get('savings', 0))
        total_debt = float(data.get('total_debt', 0))
        
        snapshot = get_financial_snapshot(income, expenses, savings, total_debt)
        return jsonify({"status": "success", "financial_snapshot": snapshot}), 200
    except Exception as e:
        return handle_error("calculate_financials_route", e)

# ====================================================================
# PROFILE & OTP AUTHENTICATION ROUTES (No MongoDB Dependency)
# ====================================================================

import random
import os
import json
from datetime import datetime, timedelta

# In-memory OTP store
IN_MEMORY_OTP_STORE = {}

# JSON File Profile store
PROFILES_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'profiles.json')

def load_profiles():
    if not os.path.exists(PROFILES_FILE_PATH):
        os.makedirs(os.path.dirname(PROFILES_FILE_PATH), exist_ok=True)
        return {}
    try:
        with open(PROFILES_FILE_PATH, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_profiles(data):
    os.makedirs(os.path.dirname(PROFILES_FILE_PATH), exist_ok=True)
    with open(PROFILES_FILE_PATH, 'w') as f:
        json.dump(data, f, indent=4)


@comprehensive_bp.route('/api/mobile-auth/send-otp', methods=['POST'])
def send_otp():
    try:
        data = request.get_json() or {}
        phone = data.get('phone')
        if not phone or len(str(phone)) != 10:
            return jsonify({"error": "Invalid phone number (must be 10 digits)"}), 400
            
        otp = str(random.randint(100000, 999999))
        expiry = datetime.utcnow() + timedelta(minutes=5)
        
        IN_MEMORY_OTP_STORE[phone] = {
            "otp": otp,
            "expiry": expiry,
            "attempts": 0
        }
        
        return jsonify({"message": "OTP sent successfully", "otp": otp}), 200
    except Exception as e:
        return handle_error("send_otp", e)

@comprehensive_bp.route('/api/mobile-auth/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.get_json() or {}
        phone = data.get('phone')
        otp = data.get('otp')
        
        if not phone or not otp:
            return jsonify({"error": "Phone and OTP required"}), 400
            
        record = IN_MEMORY_OTP_STORE.get(phone)
        
        if not record:
            return jsonify({"error": "OTP not found. Please request a new one."}), 400
            
        if datetime.utcnow() > record.get("expiry", datetime.utcnow()):
            del IN_MEMORY_OTP_STORE[phone]
            return jsonify({"error": "OTP expired"}), 400
            
        attempts = record.get("attempts", 0)
        if attempts >= 3:
            del IN_MEMORY_OTP_STORE[phone]
            return jsonify({"error": "Max attempts reached. Request a new OTP."}), 400
            
        if record.get("otp") != str(otp):
            IN_MEMORY_OTP_STORE[phone]["attempts"] += 1
            return jsonify({"error": "Invalid OTP"}), 400
            
        # Success
        del IN_MEMORY_OTP_STORE[phone]
        return jsonify({"message": "OTP verified successfully", "user_id": phone}), 200
        
    except Exception as e:
        return handle_error("verify_otp", e)

@comprehensive_bp.route('/api/save-profile', methods=['POST'])
def save_profile():
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({"error": "Unauthorized. user_id required."}), 401
            
        income = float(data.get('income', 0))
        expenses = float(data.get('expenses', 0))
        savings_rate = float(data.get('savings_rate', 0))
        total_debt = float(data.get('total_debt', 0))
        savings = max(income - expenses, 0)
        
        from financial_engine import calculate_survival_days, calculate_financial_health_score
        survival_days = calculate_survival_days(savings, expenses)
        health_score = calculate_financial_health_score(savings_rate, total_debt, income, survival_days)
        
        profiles = load_profiles()
        profiles[str(user_id)] = {
            "income": income,
            "expenses": expenses,
            "savings_rate": savings_rate,
            "health_score": health_score,
            "saved_at": datetime.utcnow().isoformat()
        }
        save_profiles(profiles)
        
        return jsonify({
            "message": "Profile saved successfully", 
            "health_score": health_score
        }), 200
        
    except Exception as e:
        return handle_error("save_profile", e)

# ====================================================================
# HEALTH CHECK ENDPOINT
# ====================================================================

@comprehensive_bp.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "All Python modules are connected and ready",
        "modules_loaded": [
            "analyzer", "betting_alternative", "crisis_detector", "debt_handler",
            "emergency_fund", "earn_suggester", "goal_tracker", "investment_guide",
            "legal_protector", "llm_engine", "mental_health_gaurdian", "ml_model",
            "pdf_report", "schemes", "situation_detector", "statement_analyzer",
            "zero_investment_path"
        ]
    }), 200

def create_comprehensive_app():
    """Create Flask app with comprehensive routes and CORS enabled"""
    app = Flask(__name__)
    
    # Enable CORS globally for local testing
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Register comprehensive blueprint
    app.register_blueprint(comprehensive_bp)
    
    return app

@comprehensive_bp.route('/api/stub/<path:route>', methods=['GET', 'POST', 'OPTIONS'])
def stub_route(route):
    return jsonify({
        "status": "success",
        "message": "Feature coming soon",
        "result": {}
    }), 200

if __name__ == '__main__':
    app = create_comprehensive_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
