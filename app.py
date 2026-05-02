# app.py
# Youth Financial Guardian Chatbot
# Connects all modules into one clean Streamlit app

import logging
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from analyzer        import analyze_spending, get_saving_tip
from crisis_detector import detect_crisis
from ml_model        import train_model, predict_future_with_ci, get_trend
from llm_engine      import (
    get_quick_tip,
    generate_with_retry,
    build_messages_with_history,
    DEFAULT_PROVIDER,
    DEFAULT_MODEL,
    LLMError,
)
from schemes         import get_relevant_schemes
from earn_suggester  import suggest_earning
from goal_tracker    import create_goal, check_progress
from emergency_fund  import (
    calculate_emergency_fund,
    get_building_plan,
    get_emergency_tip,
)
from pdf_report      import generate_report

# ─── Logging ─────────────────────────────────────────────────
logging.basicConfig(
    level  = logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt= "%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────
# Page Setup
# ─────────────────────────────────────────
st.set_page_config(
    page_title = "Youth Financial Guardian",
    page_icon  = "💰",
    layout     = "wide",
)

st.title("💰 Youth Financial Guardian")
st.caption("Your personal financial big brother/sister! 🤝")

# ─────────────────────────────────────────
# Session State Initialization
# ─────────────────────────────────────────
DEFAULTS = {
    "savings_rate"   : 0.0,
    "income"         : 0,
    "expenses"       : {},
    "savings_history": [],
    "chat_history"   : [],
}
for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

MAX_CHAT_HISTORY = 10

# ─────────────────────────────────────────
# Sidebar — User Profile
# ─────────────────────────────────────────
st.sidebar.title("👤 Your Profile")
name   = st.sidebar.text_input("Your Name", placeholder="Enter your name")
age    = st.sidebar.number_input("Your Age", min_value=13, max_value=25, value=18)
gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other"])

# ✅ Fixed — was text_input with a list (invalid) → selectbox
occupation = st.sidebar.selectbox(
    "Occupation",
    ["Student", "Self-Employed", "Freelancer", "Farmer",
     "Employed", "Unemployed", "Other"],
)
income = st.sidebar.number_input("Monthly Income (₹)", min_value=0, value=5000)
skills = st.sidebar.multiselect(
    "Your Skills",
    ["Coding", "Drawing", "Writing", "Video Editing",
     "Teaching", "Social Media", "Design"],
)

st.sidebar.markdown("---")
if name:
    st.sidebar.success(f"Hello {name}! 👋")

# ─────────────────────────────────────────
# Expense Input
# ─────────────────────────────────────────
st.markdown("## 📝 Enter Your Monthly Expenses")

expense_col1, expense_col2, expense_col3 = st.columns(3)

with expense_col1:
    food      = st.number_input("🍱 Food (₹)",      min_value=0, value=1500)
    transport = st.number_input("🚌 Transport (₹)", min_value=0, value=500)

with expense_col2:
    entertainment = st.number_input("🎮 Entertainment (₹)", min_value=0, value=300)
    education     = st.number_input("📚 Education (₹)",     min_value=0, value=500)

with expense_col3:
    others = st.number_input("📦 Others (₹)",   min_value=0, value=200)
    debt   = st.number_input("💳 Debt/EMI (₹)", min_value=0, value=0)

expenses = {
    "Food"         : food,
    "Transport"    : transport,
    "Entertainment": entertainment,
    "Education"    : education,
    "Others"       : others,
}

st.session_state.expenses = expenses

# ─────────────────────────────────────────
# Analyze Button
# ─────────────────────────────────────────
if st.button("🔍 Analyze My Finances", width='stretch'):

    st.markdown("---")

    # ── Financial Analysis ────────────────
    st.markdown("## 📊 Financial Analysis")

    result        = analyze_spending(income, expenses, debt)
    savings       = result["savings"]
    savings_rate  = result["savings_rate"]
    health_status = result["financial_health"]

    st.session_state.savings_rate = savings_rate
    st.session_state.income       = income

    # ✅ Fixed — cap history to last 12 months
    if savings > 0:
        st.session_state.savings_history.append(savings)
        st.session_state.savings_history = st.session_state.savings_history[-12:]
        logger.info(
            f"Savings recorded: ₹{savings} | "
            f"History length: {len(st.session_state.savings_history)}"
        )

    analysis_col1, analysis_col2, analysis_col3 = st.columns(3)
    analysis_col1.metric("💰 Monthly Savings", f"₹{savings}")
    analysis_col2.metric("📈 Savings Rate",    f"{savings_rate}%")
    analysis_col3.metric("❤️ Financial Health", health_status)

    st.info(get_saving_tip(savings_rate))

    # ── Expense Pie Chart ─────────────────
    st.markdown("### 🥧 Where Is Your Money Going?")

    # ✅ Fixed — include debt in pie if non-zero
    pie_expenses = {**expenses}
    if debt > 0:
        pie_expenses["Debt/EMI"] = debt

    fig = px.pie(
        values = list(pie_expenses.values()),
        names  = list(pie_expenses.keys()),
        title  = "Your Monthly Expense Breakdown",
        color_discrete_sequence = px.colors.sequential.RdBu,
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Highest Expense ───────────────────
    st.markdown("### 💸 Biggest Expense")
    st.warning(
        f"Your highest expense is **{result['highest_expense_category']}** "
        f"at ₹{result['highest_expense_amount']}"
    )
    st.info(get_quick_tip(result["highest_expense_category"]))

    # ── Crisis Detection ──────────────────
    st.markdown("## 🚨 Crisis Detection")
    crisis = detect_crisis(income, expenses, debt)
    alert  = crisis["level"]

    for msg in crisis["alerts"]:
        if crisis["level"] == "Low Risk":
            st.success(msg)
        elif crisis["level"] == "Medium Risk":
            st.warning(msg)
        else:
            st.error(msg)

    # ── Savings Prediction ────────────────
    st.markdown("## 🔮 Future Savings Prediction")

    history = (
        st.session_state.savings_history
        if len(st.session_state.savings_history) >= 3
        else [savings * (0.9 + i * 0.05) for i in range(6)]
    )

    try:
        model, r2   = train_model(history)
        predictions = predict_future_with_ci(
            model,
            current_months = len(history),
            months_ahead   = 3,
            history        = history,
        )

        logger.info(f"Prediction model R²={r2:.4f}")
        st.write(get_trend(history))

        if r2 < 0.7:
            st.warning(
                f"⚠️ Prediction confidence is low (R²={r2:.2f}). "
                f"Add more months of data for better accuracy."
            )

        # ✅ Renamed months → pred_months to avoid shadowing loop var below
        pred_months = [p["month"]       for p in predictions]
        values      = [p["predicted"]   for p in predictions]
        lowers      = [p["ci_95_lower"] for p in predictions]
        uppers      = [p["ci_95_upper"] for p in predictions]

        fig2 = go.Figure()

        fig2.add_trace(go.Bar(
            x            = pred_months,
            y            = values,
            name         = "Predicted Savings",
            marker_color = ["#4CAF50", "#2196F3", "#FF9800"],
            text         = [f"₹{v:.0f}" for v in values],
            textposition = "auto",
        ))

        fig2.add_trace(go.Scatter(
            x         = pred_months + pred_months[::-1],
            y         = uppers + lowers[::-1],
            fill      = "toself",
            name      = "95% Confidence Interval",
            fillcolor = "rgba(33,150,243,0.15)",
            line      = dict(color="rgba(255,255,255,0)"),
        ))

        fig2.update_layout(
            title       = "Next 3 Months Savings Prediction",
            xaxis_title = "Month",
            yaxis_title = "Predicted Savings (₹)",
        )
        st.plotly_chart(fig2,width='stretch')

    except Exception as e:
        st.error(f"Could not generate prediction: {e}")
        logger.error(f"Prediction failed: {e}")

    # ── Government Schemes ────────────────
    st.markdown("## 🏛 Government Schemes For You")

    # ✅ Fixed — was accidentally at top level (outside button block)
    user_profile = {
        "age"       : age,
        "gender"    : gender.lower(),
        "income"    : income,
        "occupation": occupation,
    }

    schemes = get_relevant_schemes(user_profile, top_n=5)

    if not schemes:
        st.info("No matching schemes right now. Update your profile and check back!")
    else:
        for scheme in schemes:
            with st.expander(
                f"{scheme['emoji']} {scheme['name']} "
                f"(Match: {scheme['eligibility_score']:.0f}%)"
            ):
                st.write(f"📌 {scheme['description']}")
                st.write(f"💰 Benefit: {scheme['benefit']}")
                st.write(f"🔗 [Learn More]({scheme['link']})")

    # ── Earning Suggestions ───────────────
    st.markdown("## 💡 Ways You Can Earn")

    # ✅ Fixed — was accidentally at top level (outside button block)
    earnings = suggest_earning(age=age, skills=skills)

    if not earnings:
        st.info("Add your skills in the sidebar to see personalized earning ideas!")
    else:
        tiers = {
            "immediate"  : ("🚀 Start Today (24 hours)", []),
            "short_term" : ("📅 This Week",              []),
            "medium_term": ("🎯 This Month",             []),
        }

        for idea in earnings:
            tier = idea.get("tier", "short_term")
            if tier in tiers:
                tiers[tier][1].append(idea)

        for tier_key, (tier_label, tier_ideas) in tiers.items():
            if tier_ideas:
                st.markdown(f"### {tier_label}")
                for idea in tier_ideas:
                    trend_badge = " 🔥" if idea.get("trending") else ""
                    with st.expander(
                        f"{idea['emoji']} {idea['title']}{trend_badge}"
                    ):
                        st.write(f"📌 {idea['description']}")
                        st.write(f"🌐 Platform : {idea['platform']}")
                        st.write(f"💰 Earning  : {idea['earning']}")

    # ── PDF Download ──────────────────────
    st.markdown("## 📄 Download Your Report")

    # Build action_plan from earning suggestions for pdf_report
    action_plan = [
        {
            "title"      : idea["title"],
            "description": (
                f"{idea['description']} | "
                f"Platform: {idea['platform']} | "
                f"{idea['earning']}"
            ),
        }
        for idea in (earnings[:5] if earnings else [])
    ]

    try:
        pdf_bytes = generate_report(
            name        = name or "User",
            age         = age,
            income      = income,
            expenses    = expenses,
            result      = result,
            crisis      = crisis,
            schemes     = schemes if schemes else [],
            action_plan = action_plan,
            lang        = "en",
            chart_paths = None,
        )
        st.download_button(
            label               = "📄 Download PDF Report",
            data                = pdf_bytes,
            file_name           = f"financial_report_{name or 'user'}.pdf",
            mime                = "application/pdf",
            use_container_width = True,
        )
        logger.info(f"PDF generated for: {name}")
    except Exception as e:
        st.warning(f"Could not generate PDF: {e}")
        logger.error(f"PDF generation failed: {e}")

# ─────────────────────────────────────────
# Goal Setting & Tracker
# ─────────────────────────────────────────
st.markdown("---")
st.markdown("## 🎯 Set Your Financial Goal")
st.caption("Tell me what you're saving for and I'll help you get there!")

goal_col1, goal_col2, goal_col3 = st.columns(3)

with goal_col1:
    goal_name = st.text_input(
        "What are you saving for?",
        placeholder="e.g. New Phone, Bike, College",
    )

with goal_col2:
    target_amount = st.number_input(
        "How much does it cost? (₹)",
        min_value=100,
        value=10000,
    )

with goal_col3:
    months_to_achieve = st.number_input(
        "In how many months?",
        min_value=1,
        max_value=36,
        value=3,
    )

if st.button("🎯 Track My Goal", width='stretch'):
    if goal_name.strip():
        goal = create_goal(goal_name, target_amount, months_to_achieve)

        monthly_savings = st.session_state.income * (
            st.session_state.savings_rate / 100
        )
        progress = check_progress(goal, monthly_savings)

        st.markdown(f"### Your Goal: {goal_name}")

        goal_target_col, goal_monthly_col = st.columns(2)
        goal_target_col.metric("🎯 Target Amount",     f"₹{target_amount}")
        goal_monthly_col.metric("📅 Monthly Required", f"₹{goal['monthly_required']}")

        st.markdown("#### 📊 Your Progress")
        st.progress(progress["progress_percent"] / 100)
        st.write(f"{progress['progress_percent']}% completed")

        if "🟢" in progress["status"]:
            st.success(f"{progress['status']} — {progress['encouragement']}")
        elif "🟡" in progress["status"]:
            st.warning(f"{progress['status']} — {progress['encouragement']}")
        else:
            st.error(f"{progress['status']} — {progress['encouragement']}")

        st.markdown("#### 📅 Saving Breakdown")
        weekly = goal["monthly_required"] / 4
        daily  = goal["monthly_required"] / 30

        breakdown_col1, breakdown_col2, breakdown_col3 = st.columns(3)
        breakdown_col1.metric("📅 Monthly", f"₹{goal['monthly_required']}")
        breakdown_col2.metric("🗓 Weekly",  f"₹{round(weekly)}")
        breakdown_col3.metric("☀️ Daily", f"₹{round(daily)}")

    else:
        st.warning("Please enter your goal name first! 😊")

# ─────────────────────────────────────────
# Emergency Fund Calculator
# ─────────────────────────────────────────
st.markdown("---")
st.markdown("## 🆘 Emergency Fund Calculator")
st.caption("How much should you keep safe for emergencies? Let's find out!")

ef_col1, ef_col2 = st.columns(2)

with ef_col1:
    ef_expenses = st.number_input(
        "Your Monthly Expenses (₹)",
        min_value = 0,
        value     = int(sum(st.session_state.expenses.values()))
                    if st.session_state.expenses else 0,
        key       = "ef_expenses",
    )

with ef_col2:
    ef_current_savings = st.number_input(
        "How much do you have saved right now? (₹)",
        min_value = 0,
        value     = 0,
        key       = "ef_savings",
    )

if st.button("🆘 Calculate My Emergency Fund", width='stretch'):
    fund = calculate_emergency_fund(ef_expenses)
    plan = get_building_plan(
        fund["recommended_fund"],
        ef_current_savings,
        st.session_state.income,
    )

    st.markdown("### 💰 How Much You Need")
    fund_col1, fund_col2 = st.columns(2)
    fund_col1.metric("Minimum Fund (3 months)",     f"₹{fund['minimum_fund']}")
    fund_col2.metric("Recommended Fund (6 months)", f"₹{fund['recommended_fund']}")

    st.markdown("### 📊 Your Current Progress")
    progress = (
        min(ef_current_savings / fund["recommended_fund"], 1.0)
        if fund["recommended_fund"] > 0 else 0
    )
    st.progress(progress)
    st.write(f"{round(progress * 100, 1)}% of recommended fund built")

    if plan["status"] == "complete":
        st.success("🎉 Amazing! You already have a complete emergency fund!")
    else:
        st.warning(
            f"You still need ₹{plan['remaining']} "
            f"to complete your emergency fund."
        )

        st.markdown("### 🗺 Choose Your Building Plan")
        plan_col1, plan_col2, plan_col3 = st.columns(3)

        for i, p in enumerate(plan["plans"]):
            with [plan_col1, plan_col2, plan_col3][i]:
                st.markdown(f"#### {p['emoji']} {p['name']}")
                st.metric("Monthly Save", f"₹{p['monthly']}")
                st.metric("Time to Goal", f"{p['months']} months")
                st.caption(p["description"])

    st.info(get_emergency_tip(st.session_state.savings_rate))

# ─────────────────────────────────────────
# AI Chatbot with Real Memory
# ─────────────────────────────────────────
st.markdown("---")
st.markdown("## 🤖 Ask Your Financial Guardian")
st.caption("I remember our full conversation! Ask me anything 💬")

for msg in st.session_state.chat_history:
    st.chat_message(msg["role"]).write(msg["content"])

user_message = st.chat_input("Ask me anything about money! 💬")

if user_message and user_message.strip():
    cleaned_message = user_message.strip()

    st.chat_message("user").write(cleaned_message)

    st.session_state.chat_history.append({
        "role"   : "user",
        "content": cleaned_message,
    })

    trimmed_history = st.session_state.chat_history[-MAX_CHAT_HISTORY:]

    messages = build_messages_with_history(
        user_message = cleaned_message,
        chat_history = trimmed_history[:-1],
        income       = st.session_state.income,
        savings_rate = st.session_state.savings_rate,
    )

    with st.spinner("Thinking... 🤔"):
        try:
            advice = generate_with_retry(
                provider    = DEFAULT_PROVIDER,
                model       = DEFAULT_MODEL,
                messages    = messages,
                max_tokens  = 180,
                temperature = 0.4,
            )
            logger.info("Chat response generated successfully")
        except LLMError as e:
            advice = (
                "⚠️ I'm having trouble connecting right now. "
                "Please try again in a moment!"
            )
            logger.error(f"LLM failed in chat: {e}")
        except Exception as e:
            advice = "⚠️ Something went wrong. Please try again!"
            logger.error(f"Unexpected chat error: {e}")

    st.chat_message("assistant").write(advice)
    st.session_state.chat_history.append({
        "role"   : "assistant",
        "content": advice,
    })

if st.session_state.chat_history:
    if st.button("🗑 Clear Chat", width='stretch'):
        st.session_state.chat_history = []
        st.rerun()

st.markdown("---")
st.caption("Made with ❤️ for young India")