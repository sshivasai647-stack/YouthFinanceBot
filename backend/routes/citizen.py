# Purpose: Citizen REST API — wraps existing domain modules (investment, debt, goals, chat, etc.).
# Existing module dependencies: investment_guide, debt_handler, goal_tracker, analyzer,
# statement_analyzer, schemes, emergency_fund, ml_model, mental_health_gaurdian,
# crisis_detector, betting_alternative, legal_protector, earn_suggester, situation_detector,
# pdf_report, llm_engine via backend.services.chat_router.

"""Citizen routes for YouthFinanceBot (role: citizen)."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from io import BytesIO
from typing import Any

from bson import ObjectId
from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity
from marshmallow import Schema, ValidationError, fields, validate

from analyzer import analyze_spending, get_saving_tip
from betting_alternative import assess_betting_behavior
from crisis_detector import detect_crisis
from debt_handler import (
    Debt,
    DebtType,
    calculate_debt_burden,
    calculate_emi,
    create_repayment_plan,
    detect_debt_trap,
    get_legal_protection_info,
)
from emergency_fund import calculate_emergency_fund, get_building_plan, get_emergency_tip
from goal_tracker import GoalOptimizer, check_progress, create_goal
from investment_guide import (
    calculate_investment_growth,
    create_investment_plan,
    detect_investment_scams,
    get_government_schemes,
)
from legal_protector import assess_legal_situation
from mental_health_gaurdian import CrisisLevel, assess_mental_health, handle_followup
from ml_model import calculate_financial_features, predict_future_with_ci, train_model, calculate_risk_score, get_trend, save_model, load_model
from llm_engine import get_advice, get_quick_tip
from pdf_report import generate_report
from schemes import get_relevant_schemes
from statement_analyzer import analyze_statement, parse_statement_lines
from earn_suggester import suggest_earning
from zero_investment_path import handle_zero_investment_path, get_skill_building_path, filter_by_investment_level, filter_by_category
from situation_detector import detect_situation, route_user

from backend.extensions import get_db, limiter
from backend.middleware.role_required import role_required
from backend.services.chat_router import run_chat_pipeline
from backend.services.duplicate_checker import (
    find_duplicate_goal,
    find_duplicate_investment_plan,
    goal_parameter_hash,
    investment_parameter_hash,
    parse_object_id,
)
from backend.services.notification_service import get_user_email, notify_user
from backend.services.serialize import to_jsonable

citizen_bp = Blueprint("citizen", __name__, url_prefix="/api/citizen")

MAX_UPLOAD_BYTES = 5 * 1024 * 1024


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _user_oid() -> ObjectId:
    try:
        return ObjectId(get_jwt_identity())
    except RuntimeError:
        # Fallback for testing without authentication
        return ObjectId("000000000000000000000000")


def _income_level_str(monthly: float) -> str:
    if monthly <= 20000:
        return "low"
    if monthly <= 60000:
        return "middle"
    return "high"


def _map_debt_type(raw: str) -> DebtType:
    s = (raw or "").strip().lower()
    for dt in DebtType:
        if s == dt.name.lower() or s in dt.value.lower():
            return dt
    return DebtType.PERSONAL_LOAN


def _debts_from_rows(rows: list[dict[str, Any]]) -> list[Debt]:
    out: list[Debt] = []
    for d in rows:
        p = float(d.get("principal", 0))
        r = float(d.get("rate", 0))
        tenure = int(d.get("tenure", 36))
        name = str(d.get("name", "Loan"))
        if d.get("emi") is not None and d.get("emi") != "":
            emi = float(d["emi"])
        else:
            emi = calculate_emi(p, r, tenure)
        out.append(
            Debt(
                name,
                _map_debt_type(str(d.get("type", "Personal Loan"))),
                p,
                r,
                monthly_emi=emi,
            )
        )
    return out


def _trap_history_snapshot(total_debt: float, income: float, n: int = 4) -> list[dict[str, Any]]:
    repay = min(max(total_debt * 0.02, 1.0), income * 0.3) if income > 0 else 200.0
    hist = []
    td = total_debt
    for i in range(n):
        hist.append(
            {
                "month": f"M{i + 1}",
                "total_debt": td,
                "new_debt": 0,
                "monthly_repayment": repay,
            }
        )
        td = max(0.0, td - repay * 0.5)
    return hist


# --- Marshmallow schemas ---
class InvestmentPlanSchema(Schema):
    income = fields.Float(required=True)
    age = fields.Int(required=True, validate=validate.Range(min=16, max=80))
    goals_list = fields.List(fields.Str(), required=True, validate=validate.Length(min=1))
    risk_level = fields.Str(
        required=True, validate=validate.OneOf(["low", "medium", "high", "Low", "Medium", "High"])
    )
    occupation = fields.Str(load_default="salaried")
    duplicate_resolution = fields.Str(
        required=False, validate=validate.OneOf(["force_new", "replace"])
    )
    replace_investment_id = fields.Str(required=False)


class InvestmentGrowthSchema(Schema):
    monthly = fields.Float(required=True)
    return_pct = fields.Float(required=True)
    years = fields.Float(required=True, validate=validate.Range(min=0))


class ScamCheckSchema(Schema):
    description = fields.Str(required=True, validate=validate.Length(min=10))


class DebtAnalyseSchema(Schema):
    debts = fields.List(fields.Dict(), required=True)
    income = fields.Float(required=True)
    expenses = fields.Float(load_default=0.0)


class DebtEmiSchema(Schema):
    principal = fields.Float(required=True)
    rate = fields.Float(required=True)
    months = fields.Int(required=True, validate=validate.Range(min=1))


class GoalCreateSchema(Schema):
    name = fields.Str(required=True)
    category = fields.Str(load_default="general")
    target_amount = fields.Float(required=True)
    deadline_months = fields.Int(required=True, validate=validate.Range(min=1))
    current_savings = fields.Float(load_default=0.0)
    monthly_contribution = fields.Float(required=True)
    duplicate_resolution = fields.Str(
        required=False, validate=validate.OneOf(["force_new", "replace"])
    )
    replace_goal_id = fields.Str(required=False)


class GoalOptimizeSchema(Schema):
    goals = fields.List(fields.Dict(), required=True)
    available_monthly = fields.Float(required=True)


class SpendingAnalyseSchema(Schema):
    income = fields.Float(required=True)
    expenses = fields.Dict(keys=fields.Str(), values=fields.Float(), required=True)
    debt = fields.Float(load_default=0.0)


class EmergencyFundSchema(Schema):
    monthly_expenses = fields.Float(required=True)
    months = fields.Int(load_default=6, validate=validate.Range(min=3, max=24))
    current_savings = fields.Float(load_default=0.0)
    monthly_income = fields.Float(load_default=0.0)


class SavingsPredictSchema(Schema):
    history = fields.List(fields.Float(), required=True, validate=validate.Length(min=3, max=12))
    months_ahead = fields.Int(load_default=3, validate=validate.Range(min=1, max=12))
    debt_amount = fields.Float(load_default=0.0)
    income = fields.Float(load_default=0.0)
    expenses = fields.Float(load_default=0.0)


class MentalHealthSchema(Schema):
    text_input = fields.Str(required=True, validate=validate.Length(min=3))


class BettingSchema(Schema):
    text_input = fields.Str(required=True)


class LegalAssessSchema(Schema):
    text_input = fields.Str(required=True)


class ChatSchema(Schema):
    message = fields.Str(required=True, validate=validate.Length(min=1, max=8000))
    chat_history = fields.List(fields.Dict(), load_default=list)
    income = fields.Float(load_default=0.0)
    savings_rate = fields.Float(load_default=0.0)
    age = fields.Int(load_default=22, validate=validate.Range(min=16, max=99))
    risk_appetite = fields.Str(load_default="medium")
    goal = fields.Str(load_default="retirement")
    expenses = fields.Dict(keys=fields.Str(), values=fields.Float(), load_default=dict)
    debts = fields.List(fields.Dict(), load_default=list)
    skills = fields.List(fields.Str(), load_default=list)
    debt_monthly = fields.Float(load_default=0.0)
    goal_target_amount = fields.Float(load_default=None, allow_none=True)
    goal_months = fields.Int(load_default=None, allow_none=True)
    goal_monthly_saving = fields.Float(load_default=None, allow_none=True)


class ProfileUpdateSchema(Schema):
    name = fields.Str(required=False, validate=validate.Length(min=2, max=80))
    age = fields.Int(required=False, validate=validate.Range(min=16, max=100))
    phone = fields.Str(required=False, validate=validate.Length(max=20))
    email = fields.Email(required=False)


# --- Routes ---


@citizen_bp.get("/profile")
# @role_required("citizen")  # Temporarily disabled for testing
def get_profile():
    db = get_db()
    u = db.users.find_one({"_id": _user_oid()})
    if not u:
        return jsonify({"error": "User not found"}), 404
    payload = {
        "id": str(u["_id"]),
        "email": u["email"],
        "phone": u.get("phone", ""),
        "name": u.get("name", ""),
        "age": u.get("age"),
        "role": u.get("role", "citizen"),
    }
    return jsonify(payload), 200


@citizen_bp.put("/profile")
# @role_required("citizen")  # Temporarily disabled for testing
def put_profile():
    try:
        data = ProfileUpdateSchema().load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400
    if not data:
        return jsonify({"error": "No fields to update"}), 400
    db = get_db()
    email = data.get("email")
    if email:
        other = db.users.find_one({"email": email.strip().lower(), "_id": {"$ne": _user_oid()}})
        if other:
            return jsonify({"error": "Email already in use"}), 409
    set_doc: dict[str, Any] = {}
    if "name" in data:
        set_doc["name"] = data["name"].strip()
    if "age" in data:
        set_doc["age"] = data["age"]
    if "phone" in data:
        set_doc["phone"] = data["phone"].strip()
    if email:
        set_doc["email"] = email.strip().lower()
    db.users.update_one({"_id": _user_oid()}, {"$set": set_doc})
    return jsonify({"message": "Profile updated"}), 200


@citizen_bp.post("/investment/plan")
@role_required("citizen")
@limiter.limit("20 per minute")
def investment_plan():
    try:
        body = InvestmentPlanSchema().load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400

    income = float(body["income"])
    age = int(body["age"])
    goals_list = [str(g).strip() for g in body["goals_list"]]
    risk = str(body["risk_level"]).lower()
    occupation = str(body.get("occupation", "salaried")).strip()
    db = get_db()
    uid = _user_oid()
    param_hash = investment_parameter_hash(income, goals_list, risk)
    dup = find_duplicate_investment_plan(db.investment_plans, uid, param_hash)
    res_policy = body.get("duplicate_resolution")

    if dup and res_policy != "force_new":
        if res_policy == "replace":
            rid = parse_object_id((body.get("replace_investment_id") or str(dup["_id"])))
            if not rid or not db.investment_plans.find_one({"_id": rid, "user_id": uid}):
                return jsonify({"error": "Invalid replace_investment_id"}), 400
            db.investment_plans.delete_one({"_id": rid, "user_id": uid})
        elif res_policy != "replace":
            return (
                jsonify(
                    {
                        "error": "duplicate_investment_plan",
                        "message": "You already have a plan with similar inputs. Choose duplicate_resolution: force_new, or replace.",
                        "existing_id": str(dup["_id"]),
                        "existing": to_jsonable(dup),
                    }
                ),
                409,
            )

    plan = create_investment_plan(income, age, goals_list, risk)
    level = _income_level_str(income)
    schemes = get_government_schemes(level, occupation, age)

    now = _utc_now()
    doc = {
        "user_id": uid,
        "parameter_hash": param_hash,
        "monthly_investment": income,
        "risk_profile": risk,
        "recommended": plan,
        "government_schemes": schemes,
        "warnings": [plan.get("warning", "")] if plan.get("warning") else [],
        "tips": [plan.get("hope_message", "")] if plan.get("hope_message") else [],
        "created_at": now,
        "updated_at": now,
    }
    db.investment_plans.insert_one(doc)
    email = get_user_email(db.users, uid)
    notify_user(
        db.notifications,
        user_id=uid,
        notif_type="investment_plan_ready",
        message="Your investment plan is ready — open the Investment screen to review it.",
        send_email=True,
        email_subject="YouthFinanceBot — Your plan is ready!",
        recipient_email=email,
    )
    return jsonify(to_jsonable({"plan": plan, "government_schemes": schemes})), 200


@citizen_bp.post("/investment/scam-check")
# @role_required("citizen")  # Temporarily disabled for testing
def investment_scam_check():
    try:
        body = ScamCheckSchema().load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400
    raw = detect_investment_scams(body["description"])
    score = int(raw.get("details", {}).get("risk_score_out_of_100", 0))
    red_flags = raw.get("details", {}).get("red_flags_found", [])
    advice = " ".join(
        filter(
            None,
            [
                raw.get("how_to_start", ""),
                raw.get("warning", ""),
                raw.get("hope_message", ""),
            ],
        )
    )
    return jsonify(
        {
            "is_scam": score >= 60 or "High" in str(raw.get("recommendation", "")),
            "red_flags": red_flags,
            "advice": advice.strip(),
            "raw": to_jsonable(raw),
        }
    ), 200


@citizen_bp.post("/investment/growth")
# @role_required("citizen")  # Temporarily disabled for testing
def investment_growth():
    try:
        body = InvestmentGrowthSchema().load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400
    out = calculate_investment_growth(
        amount=body["monthly"],
        rate=body["return_pct"],
        years=body["years"],
        frequency="monthly",
    )
    return jsonify(to_jsonable(out)), 200


@citizen_bp.post("/debt/analyse")
# @role_required("citizen")  # Temporarily disabled for testing
def debt_analyse():
    try:
        raw_data = request.get_json() or {}
        
        # Handle frontend format: {monthly_income, debts}
        if "monthly_income" in raw_data and "debts" in raw_data:
            income = float(raw_data["monthly_income"])
            month_exp = 0.0  # Default expenses
            rows = raw_data["debts"]
        else:
            # Handle original backend format: {income, expenses, debts}
            body = DebtAnalyseSchema().load(raw_data)
            income = float(body["income"])
            month_exp = float(body["expenses"])
            rows = body["debts"]
            
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400
    except Exception as err:
        return jsonify({"error": "Data processing failed", "details": str(err)}), 400
    dlist = _debts_from_rows(rows)
    total_princ = sum(d.principal for d in dlist)
    total_emi = sum(d.monthly_emi for d in dlist)

    burden = calculate_debt_burden(income, total_princ, total_emi)
    hist = _trap_history_snapshot(total_princ, income)
    trap = detect_debt_trap(hist, income)
    repayment = create_repayment_plan(income, month_exp, dlist) if income > 0 else {"status": "error"}

    now = _utc_now()
    doc = {
        "user_id": _user_oid(),
        "monthly_income": income,
        "debts": rows,
        "burden": burden,
        "repayment_plan": repayment,
        "trap": trap,
        "created_at": now,
    }
    db = get_db()
    db.debts.insert_one(doc)
    uid = _user_oid()
    email = get_user_email(db.users, uid)
    tstatus = str(trap.get("status", ""))
    if "Trap" in tstatus or trap.get("spiral_detected"):
        notify_user(
            db.notifications,
            user_id=uid,
            notif_type="debt_risk",
            message="⚠️ We detected possible debt risk patterns. Review your repayment plan and consider speaking to a counsellor.",
            send_email=True,
            email_subject="YouthFinanceBot — Debt risk alert",
            recipient_email=email,
        )

    return jsonify(to_jsonable({"burden": burden, "debt_trap": trap, "repayment_plan": repayment})), 200


@citizen_bp.post("/debt/emi")
# @role_required("citizen")  # Temporarily disabled for testing
def debt_emi():
    try:
        body = DebtEmiSchema().load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400
    emi = calculate_emi(body["principal"], body["rate"], body["months"])
    return jsonify({"emi": emi}), 200


@citizen_bp.get("/debt/legal-info")
# @role_required("citizen")  # Temporarily disabled for testing
def debt_legal_info():
    dtype = request.args.get("type", "")
    info = get_legal_protection_info()
    return jsonify({"debt_type_query": dtype, "info": to_jsonable(info)}), 200


@citizen_bp.post("/goals/create")
# @role_required("citizen")  # Temporarily disabled for testing
def goals_create():
    try:
        body = GoalCreateSchema().load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400

    db = get_db()
    uid = _user_oid()
    param_hash = goal_parameter_hash(body["name"], float(body["target_amount"]), int(body["deadline_months"]))
    dup = find_duplicate_goal(db.goals, uid, param_hash)
    res_policy = body.get("duplicate_resolution")
    if dup and res_policy != "force_new":
        if res_policy == "replace":
            rid = parse_object_id((body.get("replace_goal_id") or str(dup["_id"])))
            if not rid or not db.goals.find_one({"_id": rid, "user_id": uid}):
                return jsonify({"error": "Invalid replace_goal_id"}), 400
            db.goals.delete_one({"_id": rid, "user_id": uid})
        elif res_policy != "replace":
            return (
                jsonify(
                    {
                        "error": "duplicate_goal",
                        "message": "You already track this goal. Use duplicate_resolution: force_new, or replace.",
                        "existing_id": str(dup["_id"]),
                        "existing": to_jsonable(dup),
                    }
                ),
                409,
            )

    base = create_goal(body["name"], float(body["target_amount"]), int(body["deadline_months"]))
    opt = GoalOptimizer()
    adj = opt.inflation_adjusted_target(float(body["target_amount"]), int(body["deadline_months"]))
    prog = check_progress(base, float(body["monthly_contribution"]))
    now = _utc_now()
    doc = {
        "user_id": uid,
        "parameter_hash": param_hash,
        "name": body["name"],
        "category": body.get("category", "general"),
        "target_amount": float(body["target_amount"]),
        "current_savings": float(body.get("current_savings", 0)),
        "monthly_contribution": float(body["monthly_contribution"]),
        "deadline_months": int(body["deadline_months"]),
        "inflation_adjusted_target": adj,
        "on_track": prog["progress_percent"] >= 60,
        "shortfall": prog.get("monthly_gap", 0),
        "goal_payload": base,
        "created_at": now,
        "updated_at": now,
    }
    ins = db.goals.insert_one(doc)
    out = {**doc, "id": str(ins.inserted_id), "progress_check": prog}
    if prog.get("progress_percent", 100) < 60:
        email = get_user_email(db.users, uid)
        notify_user(
            db.notifications,
            user_id=uid,
            notif_type="goal_attention",
            message="⚠️ A new goal may need a higher monthly contribution to stay on track.",
            send_email=True,
            email_subject="YouthFinanceBot — Goal check-in",
            recipient_email=email,
        )
    return jsonify(to_jsonable(out)), 201


@citizen_bp.get("/goals")
# @role_required("citizen")  # Temporarily disabled for testing
def goals_list():
    db = get_db()
    uid = _user_oid()
    cursor = db.goals.find({"user_id": uid}).sort("created_at", -1)
    out = []
    today = _utc_now().date().isoformat()
    for g in cursor:
        gp = g.get("goal_payload")
        mc = float(g.get("monthly_contribution", 0))
        prog = check_progress(gp, mc) if gp else {}
        pct = float(prog.get("progress_percent", 0))
        if pct < 60:
            email = get_user_email(db.users, uid)
            notify_user(
                db.notifications,
                user_id=uid,
                notif_type="goal_behind",
                message=f"Goal \"{g.get('name', 'goal')}\" may need attention — savings pace looks behind schedule.",
                send_email=True,
                email_subject="YouthFinanceBot — Goal needs attention",
                recipient_email=email,
                dedup_key=f"goal_behind:{g['_id']}:{today}",
                dedup_hours=36,
            )
        item = {
            "id": str(g["_id"]),
            "name": g.get("name"),
            "category": g.get("category"),
            "target_amount": g.get("target_amount"),
            "inflation_adjusted_target": g.get("inflation_adjusted_target"),
            "monthly_contribution": mc,
            "deadline_months": g.get("deadline_months"),
            "on_track": pct >= 60,
            "progress": prog,
        }
        out.append(item)
    return jsonify({"goals": to_jsonable(out)}), 200


@citizen_bp.post("/goals/optimize")
# @role_required("citizen")  # Temporarily disabled for testing
def goals_optimize():
    try:
        body = GoalOptimizeSchema().load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400
    opt = GoalOptimizer()
    ranked = opt.prioritize_goals(body["goals"], float(body["available_monthly"]))
    return jsonify({"optimized": to_jsonable(ranked)}), 200


@citizen_bp.post("/spending/analyse")
# @role_required("citizen")  # Temporarily disabled for testing
def spending_analyse():
    try:
        raw_data = request.get_json() or {}
        
        # Handle frontend format: {monthly_income, spending_data}
        if "monthly_income" in raw_data and "spending_data" in raw_data:
            income = float(raw_data["monthly_income"])
            expenses = {}
            debt_pay = 0.0
            
            # Parse spending_data string format: "Category, Amount, Date\n..."
            for line in raw_data["spending_data"].strip().split('\n'):
                if line.strip():
                    parts = line.split(',')
                    if len(parts) >= 2:
                        category = parts[0].strip()
                        try:
                            amount = float(parts[1].strip())
                            expenses[category] = expenses.get(category, 0) + amount
                        except ValueError:
                            continue
        else:
            # Handle original backend format: {income, expenses, debt}
            body = SpendingAnalyseSchema().load(raw_data)
            income = float(body["income"])
            expenses = {k: float(v) for k, v in body["expenses"].items()}
            debt_pay = float(body.get("debt", 0))
            
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400
    except Exception as err:
        return jsonify({"error": "Data processing failed", "details": str(err)}), 400
    result = analyze_spending(income, expenses, debt_pay)
    tip = get_saving_tip(float(result["savings_rate"]))
    now = _utc_now()
    get_db().spending_logs.insert_one(
        {
            "user_id": _user_oid(),
            "income": income,
            "expenses": expenses,
            "debt_monthly": debt_pay,
            "savings_rate": result["savings_rate"],
            "analysis": result,
            "saving_tip": tip,
            "created_at": now,
        }
    )
    return jsonify(to_jsonable({"analysis": result, "saving_tip": tip})), 200


@citizen_bp.post("/statement/upload")
# @role_required("citizen")  # Temporarily disabled for testing
def statement_upload():
    income_override = None
    if request.form.get("income"):
        try:
            income_override = float(request.form.get("income", ""))
        except ValueError:
            return jsonify({"error": "Invalid income"}), 400
    if "file" not in request.files:
        return jsonify({"error": "Missing file field 'file'"}), 400
    f = request.files["file"]
    raw_bytes = f.read()
    if len(raw_bytes) > MAX_UPLOAD_BYTES:
        return jsonify({"error": "File too large (max 5 MB)"}), 400
    name = (f.filename or "").lower()
    if not name.endswith((".csv", ".txt", ".text")):
        return jsonify({"error": "Only .csv or .txt uploads are allowed"}), 400
    text = raw_bytes.decode("utf-8", errors="replace")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    parsed = parse_statement_lines(lines)
    stmt_lines_joined = "\n".join(lines)
    analyzed = analyze_statement(stmt_lines_joined, income=income_override)
    return jsonify(to_jsonable(analyzed)), 200


@citizen_bp.post("/emergency-fund/calculate")
# @role_required("citizen")  # Temporarily disabled for testing
def emergency_fund_calc():
    try:
        body = EmergencyFundSchema().load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400
    monthly_exp = float(body["monthly_expenses"])
    months = int(body["months"])
    calc = calculate_emergency_fund(monthly_exp, months)
    target = float(calc["recommended_fund"])
    current = float(body.get("current_savings", 0))
    income = float(body.get("monthly_income", 0))
    plans = get_building_plan(target, current, income if income > 0 else monthly_exp) if income > 0 else {"note": "Provide monthly_income for speed plans"}
    savings_rate = 0.0
    if income > 0:
        savings_rate = max(0.0, ((income - monthly_exp) / income) * 100)
    tip = get_emergency_tip(savings_rate)
    return jsonify(
        to_jsonable(
            {
                "emergency_calc": calc,
                "building_plan": plans,
                "tip": tip,
            }
        )
    ), 200


@citizen_bp.post("/savings/predict")
# @role_required("citizen")  # Temporarily disabled for testing
def savings_predict():
    try:
        body = SavingsPredictSchema().load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400
    history = [float(x) for x in body["history"]]
    model, _r2 = train_model(history)
    preds = predict_future_with_ci(
        model,
        current_months=len(history),
        months_ahead=int(body["months_ahead"]),
        history=history,
    )
    features = calculate_financial_features(
        debt_amount=float(body.get("debt_amount", 0)),
        income=float(body.get("income", 0)),
        expenses=float(body.get("expenses", 0)),
    )
    forecast = [p["predicted"] for p in preds]
    lower = [p["ci_95_lower"] for p in preds]
    upper = [p["ci_95_upper"] for p in preds]
    labels = [p["month"] for p in preds]
    return jsonify(
        {
            "forecast": forecast,
            "lower_bound": lower,
            "upper_bound": upper,
            "labels": labels,
            "details": to_jsonable(preds),
            "financial_features": features,
        }
    ), 200


@citizen_bp.post("/mental-health/assess")
@role_required("citizen")
@limiter.limit("20 per minute")
def mental_health_assess():
    try:
        body = MentalHealthSchema().load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400
    text = body["text_input"].strip()
    result = assess_mental_health(text)
    crisis_scan = None
    if result.crisis_level != CrisisLevel.STABLE:
        crisis_scan = detect_crisis(0, {}, 0, text=text)
    now = _utc_now()
    db = get_db()
    uid = _user_oid()
    db.mental_health_logs.insert_one(
        {
            "user_id": uid,
            "crisis_level": result.crisis_level.value,
            "flagged": result.crisis_level != CrisisLevel.STABLE,
            "created_at": now,
        }
    )
    if result.crisis_level != CrisisLevel.STABLE:
        notify_user(
            db.notifications,
            user_id=uid,
            notif_type="crisis_support",
            message="Support resources and guidance have been shared based on your check-in. You are not alone.",
            send_email=True,
            email_subject="YouthFinanceBot — Support resources",
            recipient_email=get_user_email(db.users, uid),
        )
    return jsonify(
        to_jsonable(
            {
                "assessment": result,
                "crisis_scan": crisis_scan,
            }
        )
    ), 200


@citizen_bp.post("/betting/assess")
# @role_required("citizen")  # Temporarily disabled for testing
def betting_assess():
    try:
        body = BettingSchema().load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400
    r = assess_betting_behavior(body["text_input"])
    return jsonify(to_jsonable(r)), 200


@citizen_bp.post("/legal/assess")
# @role_required("citizen")  # Temporarily disabled for testing
def legal_assess():
    try:
        body = LegalAssessSchema().load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400
    r = assess_legal_situation(body["text_input"])
    return jsonify(to_jsonable(r)), 200


@citizen_bp.get("/earn/suggest")
# @role_required("citizen")  # Temporarily disabled for testing
def earn_suggest():
    try:
        age = int(request.args.get("age", "20"))
    except ValueError:
        return jsonify({"error": "Invalid age"}), 400
    skills = request.args.getlist("skills") or request.args.getlist("skills[]")
    if not skills and request.args.get("skills"):
        skills = [s.strip() for s in str(request.args.get("skills")).split(",") if s.strip()]
    ideas = suggest_earning(age, skills or ["writing"])
    return jsonify({"suggestions": to_jsonable(ideas)}), 200


@citizen_bp.get("/schemes")
# @role_required("citizen")  # Temporarily disabled for testing
def schemes_list():
    try:
        age = int(request.args.get("age", "22"))
        income = float(request.args.get("income", "0"))
        state = request.args.get("state", "Maharashtra")
        occupation = request.args.get("occupation", "Salaried")
        gender = request.args.get("gender", "any")
    except ValueError:
        return jsonify({"error": "Invalid numeric query params"}), 400
    profile = {
        "age": age,
        "gender": gender,
        "income": income,
        "state": state,
        "occupation": occupation,
    }
    schemes = get_relevant_schemes(profile, top_n=8)
    get_db().scheme_matches.insert_one(
        {
            "user_id": _user_oid(),
            "schemes": [{"name": s.get("name"), "score": s.get("eligibility_score"), "eligible": True} for s in schemes],
            "created_at": _utc_now(),
        }
    )
    return jsonify({"schemes": to_jsonable(schemes)}), 200


@citizen_bp.post("/zero-investment/analyze")
# @role_required("citizen")  # Temporarily disabled for testing
def zero_investment_analyze():
    try:
        body = {
            "user_input": request.get_json().get("user_input", ""),
            "age": request.get_json().get("age", 18),
            "skills": request.get_json().get("skills", ["basic computer skills"]),
            "has_smartphone": request.get_json().get("has_smartphone", True),
            "has_internet": request.get_json().get("has_internet", True)
        }
    except Exception as err:
        return jsonify({"error": "Invalid request data", "details": str(err)}), 400
    
    result = handle_zero_investment_path(
        user_input=body["user_input"],
        user_profile={
            "age": body["age"],
            "skills": body["skills"],
            "has_smartphone": body["has_smartphone"],
            "has_internet": body["has_internet"]
        }
    )
    return jsonify(to_jsonable(result)), 200


@citizen_bp.post("/situation/detect")
# @role_required("citizen")  # Temporarily disabled for testing
def situation_detect():
    try:
        body = {
            "user_input": request.get_json().get("user_input", "")
        }
    except Exception as err:
        return jsonify({"error": "Invalid request data", "details": str(err)}), 400
    
    result = detect_situation(body["user_input"])
    return jsonify(to_jsonable(result)), 200


@citizen_bp.post("/route/user")
# @role_required("citizen")  # Temporarily disabled for testing
def route_user_endpoint():
    try:
        body = {
            "user_input": request.get_json().get("user_input", "")
        }
    except Exception as err:
        return jsonify({"error": "Invalid request data", "details": str(err)}), 400
    
    result = route_user(body["user_input"])
    return jsonify(to_jsonable(result)), 200


@citizen_bp.post("/llm/advice")
# @role_required("citizen")  # Temporarily disabled for testing
def llm_advice():
    try:
        body = {
            "prompt": request.get_json().get("prompt", ""),
            "context": request.get_json().get("context", ""),
            "category": request.get_json().get("category", "general")
        }
    except Exception as err:
        return jsonify({"error": "Invalid request data", "details": str(err)}), 400
    
    try:
        advice = get_advice(body["prompt"], body["context"])
        return jsonify({"advice": advice}), 200
    except Exception as err:
        return jsonify({"error": "LLM service unavailable", "details": str(err)}), 500


@citizen_bp.get("/llm/quick-tip")
# @role_required("citizen")  # Temporarily disabled for testing
def llm_quick_tip():
    try:
        category = request.args.get("category", "general")
        tip = get_quick_tip(category)
        return jsonify({"tip": tip}), 200
    except Exception as err:
        return jsonify({"error": "Tip service unavailable", "details": str(err)}), 500


@citizen_bp.post("/ml/risk-score")
# @role_required("citizen")  # Temporarily disabled for testing
def ml_risk_score():
    try:
        body = {
            "financial_features": request.get_json().get("financial_features", {})
        }
    except Exception as err:
        return jsonify({"error": "Invalid request data", "details": str(err)}), 400
    
    try:
        risk_score = calculate_risk_score(body["financial_features"])
        return jsonify({"risk_score": risk_score}), 200
    except Exception as err:
        return jsonify({"error": "Risk calculation failed", "details": str(err)}), 500


@citizen_bp.post("/ml/trend")
# @role_required("citizen")  # Temporarily disabled for testing
def ml_trend():
    try:
        body = {
            "financial_history": request.get_json().get("financial_history", [])
        }
    except Exception as err:
        return jsonify({"error": "Invalid request data", "details": str(err)}), 400
    
    try:
        trend = get_trend(body["financial_history"])
        return jsonify({"trend": trend}), 200
    except Exception as err:
        return jsonify({"error": "Trend analysis failed", "details": str(err)}), 500


@citizen_bp.post("/ml/features")
# @role_required("citizen")  # Temporarily disabled for testing
def ml_features():
    try:
        body = {
            "debt_amount": request.get_json().get("debt_amount", 0),
            "income": request.get_json().get("income", 0),
            "expenses": request.get_json().get("expenses", 0),
            "total_assets": request.get_json().get("total_assets", None)
        }
    except Exception as err:
        return jsonify({"error": "Invalid request data", "details": str(err)}), 400
    
    try:
        features = calculate_financial_features(
            debt_amount=body["debt_amount"],
            income=body["income"],
            expenses=body["expenses"],
            total_assets=body["total_assets"]
        )
        return jsonify({"features": features}), 200
    except Exception as err:
        return jsonify({"error": "Feature calculation failed", "details": str(err)}), 500


@citizen_bp.post("/ml/train")
# @role_required("citizen")  # Temporarily disabled for testing
def ml_train():
    try:
        body = {
            "financial_history": request.get_json().get("financial_history", [])
        }
    except Exception as err:
        return jsonify({"error": "Invalid request data", "details": str(err)}), 400
    
    try:
        model, r2 = train_model(body["financial_history"])
        return jsonify({"model_trained": True, "r2_score": r2}), 200
    except Exception as err:
        return jsonify({"error": "Model training failed", "details": str(err)}), 500


@citizen_bp.post("/ml/predict")
# @role_required("citizen")  # Temporarily disabled for testing
def ml_predict():
    try:
        body = {
            "financial_history": request.get_json().get("financial_history", []),
            "months_ahead": request.get_json().get("months_ahead", 6)
        }
    except Exception as err:
        return jsonify({"error": "Invalid request data", "details": str(err)}), 400
    
    try:
        model, _r2 = train_model(body["financial_history"])
        predictions = predict_future_with_ci(
            model,
            current_months=len(body["financial_history"]),
            months_ahead=body["months_ahead"],
            history=body["financial_history"]
        )
        return jsonify({"predictions": predictions}), 200
    except Exception as err:
        return jsonify({"error": "Prediction failed", "details": str(err)}), 500


@citizen_bp.post("/mental-health/followup")
# @role_required("citizen")  # Temporarily disabled for testing
def mental_health_followup():
    try:
        body = {
            "user_input": request.get_json().get("user_input", ""),
            "crisis_level": request.get_json().get("crisis_level", "stable")
        }
    except Exception as err:
        return jsonify({"error": "Invalid request data", "details": str(err)}), 400
    
    try:
        result = handle_followup(body["user_input"], body["crisis_level"])
        return jsonify(result), 200
    except Exception as err:
        return jsonify({"error": "Followup failed", "details": str(err)}), 500


@citizen_bp.post("/zero-investment/skill-path")
# @role_required("citizen")  # Temporarily disabled for testing
def zero_investment_skill_path():
    try:
        body = {
            "user_profile": request.get_json().get("user_profile", {})
        }
    except Exception as err:
        return jsonify({"error": "Invalid request data", "details": str(err)}), 400
    
    try:
        skill_path = get_skill_building_path(body["user_profile"])
        return jsonify(skill_path), 200
    except Exception as err:
        return jsonify({"error": "Skill path generation failed", "details": str(err)}), 500


@citizen_bp.get("/zero-investment/filter")
# @role_required("citizen")  # Temporarily disabled for testing
def zero_investment_filter():
    try:
        investment_level = request.args.get("investment_level", "zero")
        category = request.args.get("category", None)
        
        # This would need the actual opportunities list, for now return empty
        opportunities = []
        
        if investment_level:
            opportunities = filter_by_investment_level(investment_level)
        if category:
            opportunities = filter_by_category(category)
            
        return jsonify({"opportunities": opportunities}), 200
    except Exception as err:
        return jsonify({"error": "Filter failed", "details": str(err)}), 500


@citizen_bp.post("/debt/prioritize")
# @role_required("citizen")  # Temporarily disabled for testing
def debt_prioritize():
    try:
        body = {
            "debts": request.get_json().get("debts", []),
            "method": request.get_json().get("method", "auto")
        }
    except Exception as err:
        return jsonify({"error": "Invalid request data", "details": str(err)}), 400
    
    try:
        prioritized = prioritize_debts(body["debts"], body["method"])
        return jsonify(prioritized), 200
    except Exception as err:
        return jsonify({"error": "Debt prioritization failed", "details": str(err)}), 500


@citizen_bp.post("/debt/detect-trap")
# @role_required("citizen")  # Temporarily disabled for testing
def debt_detect_trap():
    try:
        body = {
            "debt_history": request.get_json().get("debt_history", []),
            "income": request.get_json().get("income", 0)
        }
    except Exception as err:
        return jsonify({"error": "Invalid request data", "details": str(err)}), 400
    
    try:
        trap_detected = detect_debt_trap(body["debt_history"], body["income"])
        return jsonify(trap_detected), 200
    except Exception as err:
        return jsonify({"error": "Debt trap detection failed", "details": str(err)}), 500


@citizen_bp.post("/chat")
# @role_required("citizen")  # Temporarily disabled for testing
@limiter.limit("30 per minute")
def chat():
    try:
        body = ChatSchema().load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400

    hist_raw = body.get("chat_history") or []
    hist: list[dict[str, str]] = []
    for m in hist_raw:
        if isinstance(m, dict) and m.get("role") and m.get("content") is not None:
            hist.append({"role": str(m["role"]), "content": str(m["content"])})

    t0 = time.perf_counter()
    pipeline = run_chat_pipeline(
        user_message=body["message"].strip(),
        chat_history=hist,
        income=float(body.get("income", 0)),
        savings_rate=float(body.get("savings_rate", 0)),
        age=int(body.get("age", 22)),
        risk_appetite=str(body.get("risk_appetite", "medium")),
        goal=str(body.get("goal", "retirement")),
        expenses=body.get("expenses") or {},
        debts_payload=body.get("debts") or [],
        skills=body.get("skills") or [],
        monthly_debt_payment=float(body.get("debt_monthly", 0)),
        goal_target_amount=body.get("goal_target_amount"),
        goal_months=body.get("goal_months"),
        goal_monthly_saving=body.get("goal_monthly_saving"),
    )
    latency_ms = int((time.perf_counter() - t0) * 1000)

    now = _utc_now()
    uid = _user_oid()
    db = get_db()
    if not pipeline.get("skip_llm"):
        db.ai_usage.insert_one(
            {
                "user_id": uid,
                "latency_ms": latency_ms,
                "had_llm_error": bool(pipeline.get("llm_error")),
                "route": pipeline.get("route"),
                "created_at": now,
            }
        )
    user_turn = {"role": "user", "content": body["message"].strip(), "timestamp": now, "route": None}
    assistant_turn = {
        "role": "assistant",
        "content": pipeline["reply"],
        "timestamp": now,
        "route": pipeline["route"],
    }
    db.chat_sessions.update_one(
        {"user_id": uid},
        {
            "$push": {"messages": {"$each": [user_turn, assistant_turn], "$slice": -200}},
            "$set": {"updated_at": now},
            "$setOnInsert": {"user_id": uid, "created_at": now},
        },
        upsert=True,
    )

    det = pipeline.get("detection") or {}
    if (
        pipeline.get("route") == "crisis"
        or det.get("is_crisis")
        or det.get("path", "").endswith("_F")
        or pipeline.get("route") == "mental_health"
    ):
        notify_user(
            db.notifications,
            user_id=uid,
            notif_type="chat_crisis",
            message="We linked wellbeing-related guidance to your last chat. If you are in immediate danger, contact local emergency services.",
            send_email=True,
            email_subject="YouthFinanceBot — Crisis support",
            recipient_email=get_user_email(db.users, uid),
            dedup_key=f"chat_crisis:{uid}:{now.date().isoformat()}",
            dedup_hours=12,
        )

    return jsonify(
        {
            "reply": pipeline["reply"],
            "route": pipeline["route"],
            "suggestions": pipeline["suggestions"],
            "detection": pipeline["detection"],
            "context": to_jsonable(pipeline.get("context") or {}),
            "skip_llm": bool(pipeline.get("skip_llm")),
            "llm_error": pipeline.get("llm_error"),
        }
    ), 200


@citizen_bp.delete("/chat/history")
# @role_required("citizen")  # Temporarily disabled for testing
def chat_history_clear():
    get_db().chat_sessions.delete_one({"user_id": _user_oid()})
    return jsonify({"message": "Chat history cleared"}), 200


@citizen_bp.get("/report/download")
# @role_required("citizen")  # Temporarily disabled for testing
def report_download():
    db = get_db()
    uid = _user_oid()
    u = db.users.find_one({"_id": uid})
    if not u:
        return jsonify({"error": "User not found"}), 404
    spend = db.spending_logs.find_one({"user_id": uid}, sort=[("created_at", -1)])
    income = float(spend.get("income", 0)) if spend else 0.0
    expenses = spend.get("expenses", {}) if spend else {}
    if spend and spend.get("analysis"):
        result = spend["analysis"]
    else:
        result = {
            "total_income": income,
            "total_expenses": sum(expenses.values()) if expenses else 0,
            "savings": max(0, income - sum(expenses.values())) if expenses else 0,
            "savings_rate": 0.0,
            "financial_health": "N/A",
        }

    crisis = detect_crisis(income if income > 0 else 0, expenses if expenses else {"Other": 0}, 0)

    profile = {
        "age": u.get("age", 22),
        "gender": "any",
        "income": income,
        "state": "India",
        "occupation": "General",
    }
    schemes = get_relevant_schemes(profile, top_n=5)
    action_plan = []
    for g in db.goals.find({"user_id": uid}).limit(5):
        action_plan.append(
            {"title": g.get("name", "Goal"), "description": f"Target ₹{g.get('target_amount', 0):,.0f}"}
        )
    if not action_plan:
        action_plan = [{"title": "Track spending", "description": "Log income and expenses monthly."}]

    pdf_bytes = generate_report(
        name=u.get("name", "User"),
        age=int(u.get("age", 18)),
        income=income,
        expenses=expenses if isinstance(expenses, dict) else {},
        result=result,
        crisis=crisis,
        schemes=schemes,
        action_plan=action_plan,
        lang="en",
        chart_paths=None,
    )
    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="youth_finance_report.pdf",
    )


@citizen_bp.get("/notifications")
# @role_required("citizen")  # Temporarily disabled for testing
def notifications_list():
    cursor = get_db().notifications.find({"user_id": _user_oid()}).sort("created_at", -1).limit(100)
    out = []
    for n in cursor:
        out.append(
            {
                "id": str(n["_id"]),
                "type": n.get("type", "info"),
                "message": n.get("message", ""),
                "read": bool(n.get("read", False)),
                "created_at": n.get("created_at"),
            }
        )
    return jsonify({"notifications": to_jsonable(out)}), 200


@citizen_bp.patch("/notifications/read-all")
# @role_required("citizen")  # Temporarily disabled for testing
def notifications_mark_all_read():
    get_db().notifications.update_many(
        {"user_id": _user_oid(), "read": {"$ne": True}},
        {"$set": {"read": True}},
    )
    return jsonify({"message": "All notifications marked read"}), 200


@citizen_bp.patch("/notifications/<notif_id>/read")
# @role_required("citizen")  # Temporarily disabled for testing
def notification_read(notif_id: str):
    try:
        nid = ObjectId(notif_id)
    except Exception:
        return jsonify({"error": "Invalid id"}), 400
    res = get_db().notifications.update_one(
        {"_id": nid, "user_id": _user_oid()},
        {"$set": {"read": True}},
    )
    if res.matched_count == 0:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "Marked read"}), 200
