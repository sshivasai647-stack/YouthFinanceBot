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
from situation_detector import (
    detect_situation,
    PATH_BETTING,
    PATH_DEBT,
    PATH_EXPENSE,
    PATH_INVEST,
    PATH_LEGAL,
    PATH_ZERO_INVESTMENT,
    PATH_MENTAL_HEALTH,
    PATH_UNKNOWN,
)
from statement_analyzer import run_statement_analyzer
from betting_alternative import run_betting_alternative
from legal_protector      import run_legal_protector
from pdf_report           import generate_report
from chat_router          import ChatRouter, UserContext, ResponseType

# ─── Logging ─────────────────────────────────────────────────
logging.basicConfig(
    level  = logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt= "%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────
# Page Setup & Professional Styling
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Youth Financial Guardian",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Professional CSS Styling
st.markdown("""
<style>
    /* Professional color scheme */
    :root {
        --primary-color: #1a365d;
        --secondary-color: #2d3748;
        --accent-color: #3182ce;
        --success-color: #38a169;
        --warning-color: #d69e2e;
        --danger-color: #e53e3e;
        --background-color: #f7fafc;
        --card-background: #ffffff;
        --text-primary: #1a202c;
        --text-secondary: #4a5568;
    }

    /* Main container styling */
    .main {
        background-color: var(--background-color);
        color: var(--text-primary);
    }

    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }

    .header-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 300;
    }

    /* Card styling */
    .card {
        background: var(--card-background);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
    }

    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, var(--accent-color), #4299e1);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }

    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: var(--card-background);
        border-right: 3px solid var(--accent-color);
    }

    /* Input styling */
    .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox select {
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.75rem;
        transition: border-color 0.3s ease;
    }

    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus {
        border-color: var(--accent-color);
        box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, var(--secondary-color), var(--primary-color));
        color: white;
        border-radius: 8px;
        font-weight: 600;
        padding: 1rem;
    }

    /* Metric styling */
    .metric-container {
        background: var(--card-background);
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--accent-color);
    }

    .metric-label {
        font-size: 0.9rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Success/Warning/Error styling */
    .success-message {
        background: linear-gradient(135deg, #c6f6d5, #9ae6b4);
        border: 1px solid var(--success-color);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }

    .warning-message {
        background: linear-gradient(135deg, #fef5e7, #fdeaa7);
        border: 1px solid var(--warning-color);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }

    .error-message {
        background: linear-gradient(135deg, #fed7d7, #feb2b2);
        border: 1px solid var(--danger-color);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }

    /* Footer styling */
    .footer {
        background: var(--secondary-color);
        color: white;
        padding: 2rem;
        text-align: center;
        margin-top: 3rem;
        border-radius: 12px;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Responsive design */
    @media (max-width: 768px) {
        .header-title {
            font-size: 2rem;
        }
        .card {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Professional Header
st.markdown("""
<div class="header-container">
    <h1 class="header-title">💰 Youth Financial Guardian</h1>
    <p class="header-subtitle">Your trusted financial companion for a secure future</p>
</div>
""", unsafe_allow_html=True)

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

# Initialize ChatRouter for AI-powered conversation routing
if "chat_router" not in st.session_state:
    st.session_state.chat_router = ChatRouter(
        provider=DEFAULT_PROVIDER,
        model=DEFAULT_MODEL,
        max_history=10
    )

if "messages" not in st.session_state:
    st.session_state.messages = []  # Chat interface messages

MAX_CHAT_HISTORY = 10

# ─────────────────────────────────────────
# Professional Sidebar — User Profile
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h2 style="color: var(--primary-color); margin-bottom: 0.5rem;">👤 Your Profile</h2>
        <p style="color: var(--text-secondary); font-size: 0.9rem;">Tell us about yourself</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Profile inputs with better styling
    name = st.text_input("Full Name", placeholder="Enter your full name", help="Your name will be used in reports")

    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", min_value=13, max_value=35, value=18, help="Age helps us provide age-appropriate advice")
    with col2:
        gender = st.selectbox("Gender", ["Prefer not to say", "Male", "Female", "Other"], help="Optional: Helps us personalize suggestions")

    occupation = st.selectbox(
        "Occupation",
        ["Student", "Self-Employed", "Freelancer", "Farmer", "Employed", "Unemployed", "Other"],
        help="Your occupation affects earning and scheme recommendations"
    )

    income = st.number_input(
        "Monthly Income (₹)",
        min_value=0,
        value=5000,
        step=500,
        help="Your total monthly income from all sources"
    )

    skills = st.multiselect(
        "Your Skills",
        ["Coding", "Writing", "Design", "Teaching", "Video Editing", "Social Media", "Photography", "Music", "Sports", "Other"],
        help="Skills help us suggest earning opportunities"
    )

    st.markdown("---")

    # Profile completion indicator
    if name and age and occupation:
        completion = 100
        if income > 0:
            completion = 100
        if skills:
            completion = 100

        st.progress(completion/100)
        st.success(f"Profile {completion}% Complete ✅")
        st.markdown(f"**Welcome, {name}!** 👋")
    else:
        st.warning("Complete your profile for personalized recommendations")

# ─────────────────────────────────────────
# Main Content Area
# ─────────────────────────────────────────

# Quick Actions Dashboard
st.markdown("""
<div class="card">
    <h3 style="color: var(--primary-color); margin-bottom: 1rem;">🚀 Quick Actions</h3>
    <p style="color: var(--text-secondary);">Get started with our most popular tools</p>
</div>
""", unsafe_allow_html=True)

# Quick action buttons in columns
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📊 Analyze Finances", use_container_width=True):
        st.session_state.active_section = "analysis"
        st.rerun()
with col2:
    if st.button("🧾 Check Statement", use_container_width=True):
        st.session_state.active_section = PATH_EXPENSE
        st.rerun()
with col3:
    if st.button("💡 Get Advice", use_container_width=True):
        st.session_state.active_section = "advice"
        st.rerun()
with col4:
    if st.button("📈 Plan Goals", use_container_width=True):
        st.session_state.active_section = "goals"
        st.rerun()

st.markdown("---")

# ─────────────────────────────────────────
# AI-Powered Situation Analysis
# ─────────────────────────────────────────
st.markdown("""
<div class="card">
    <h3 style="color: var(--primary-color); margin-bottom: 1rem;">🧭 AI Financial Analysis</h3>
    <p style="color: var(--text-secondary);">Describe your financial situation and get personalized guidance</p>
</div>
""", unsafe_allow_html=True)

situation_input = st.text_area(
    "Describe your current financial situation:",
    height=120,
    placeholder=(
        "Example: I'm a college student struggling with loan app harassment, "
        "or I keep losing money on fantasy sports betting..."
    ),
    help="Be specific about your situation for better recommendations"
)

if 'detected_path' not in st.session_state:
    st.session_state.detected_path = None
if 'active_section' not in st.session_state:
    st.session_state.active_section = None
if 'route_result' not in st.session_state:
    st.session_state.route_result = None

# Show last routing result if available
if st.session_state.route_result:
    with st.expander("🔍 Last Routing Result", expanded=False):
        st.json(st.session_state.route_result)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Copy Result", key="copy_route"):
                st.code(str(st.session_state.route_result), language="json")
                st.success("Copied to clipboard!")
        with col2:
            if st.button("🗑 Clear Result", key="clear_route"):
                st.session_state.route_result = None
                st.rerun()


# Show last routing result if available
if st.session_state.route_result:
    with st.expander("🔍 AI Analysis Result", expanded=False):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.json(st.session_state.route_result)
        with col2:
            if st.button("📋 Copy", key="copy_route"):
                st.code(str(st.session_state.route_result), language="json")
                st.success("✅ Copied to clipboard!")
            if st.button("🗑 Clear", key="clear_route"):
                st.session_state.route_result = None
                st.rerun()

# Detection Button
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    detect_button = st.button(
        "🔍 Analyze My Situation",
        use_container_width=True,
        type="primary",
        help="Click to get AI-powered financial analysis"
    )

if detect_button:
    if situation_input.strip():
        with st.spinner("🤖 Analyzing your situation..."):
            route = detect_situation(situation_input)

        st.session_state.detected_path = route.path
        st.session_state.active_section = route.path
        st.session_state.route_result = {
            "path": route.path,
            "confidence": route.confidence,
            "triggers": route.triggers,
            "is_crisis": route.is_crisis,
            "clarification_needed": route.clarification_needed,
            "suggested_question": route.suggested_question,
            "secondary_path": route.secondary_path,
            "display_message": route.display_message,
        }

        # Professional result display
        if route.is_crisis:
            st.error("🚨 Crisis Detected - Immediate Action Required")
        else:
            st.success("✅ Analysis Complete")

        st.markdown("### 📋 Recommended Actions")
        st.info(route.display_message)

        if route.secondary_path:
            st.write(f"**Also related to:** {route.secondary_path.replace('PATH_','').title()}")

        if route.clarification_needed and route.suggested_question:
            st.warning(f"💭 {route.suggested_question}")

        # Action buttons
        st.markdown("### 🎯 Quick Access")
        route_buttons = {
            PATH_LEGAL: ("🛡️ Legal Protection", "Get help with loan harassment and legal issues"),
            PATH_BETTING: ("🎲 Betting Help", "Find alternatives to gambling and fantasy sports"),
            PATH_EXPENSE: ("🧾 Statement Analysis", "Analyze your bank statements and spending"),
            PATH_DEBT: ("💳 Debt Management", "Get help with loans and debt management"),
            PATH_INVEST: ("📈 Investment Planning", "Learn about safe investment options"),
            PATH_ZERO_INVESTMENT: ("💰 Earning Ideas", "Discover ways to increase your income"),
        }

        cols = st.columns(2)
        for i, (path, (label, desc)) in enumerate(route_buttons.items()):
            with cols[i % 2]:
                if st.button(label, help=desc, use_container_width=True):
                    st.session_state.active_section = path
                    st.rerun()

        hints = {
            PATH_MENTAL_HEALTH: (
                "This sounds like a serious emotional crisis. Please seek immediate support from a trusted adult or local helpline, and then use the chat or the other sections for financial guidance."
            ),
            PATH_LEGAL: (
                "Use the Legal Protection Help section below to analyze harassment, hidden fees, or unfair loan app behavior."
            ),
            PATH_BETTING: (
                "Use the Betting & Fantasy Sports Help section below to analyze your pattern and find safer alternatives."
            ),
            PATH_EXPENSE: (
                "Use the Bank Statement Analyzer above or the Analyze My Finances button to track spending and categories."
            ),
            PATH_DEBT: (
                "This looks like debt or loan stress. Use the Legal Protection Help section and the financial analysis section to take control."
            ),
            PATH_INVEST: (
                "You're likely ready to think about investing. Use Analyze My Finances and explore the earning / scheme suggestions below."
            ),
            PATH_ZERO_INVESTMENT: (
                "Start with the earning ideas, government schemes, and saving tools in the app to grow from zero."
            ),
            PATH_UNKNOWN: (
                "Try describing one specific issue: debt, betting losses, hidden loan fees, or where your money is going."
            ),
        }

        if route.path in hints:
            st.markdown(f"**💡 Tip:** {hints[route.path]}")

    else:
        st.warning("⚠️ Please describe your financial situation first.")

# ─────────────────────────────────────────
# Expense Tracking Section
# ─────────────────────────────────────────
st.markdown("""
<div class="card">
    <h3 style="color: var(--primary-color); margin-bottom: 1rem;">📊 Monthly Expense Tracker</h3>
    <p style="color: var(--text-secondary);">Track your spending to understand where your money goes</p>
</div>
""", unsafe_allow_html=True)

# Expense input in organized columns
expense_tabs = st.tabs(["📱 Essentials", "🎯 Lifestyle", "💰 Financial"])

with expense_tabs[0]:  # Essentials
    col1, col2 = st.columns(2)
    with col1:
        food = st.number_input("🍱 Food & Dining", min_value=0, value=1500, step=100,
                              help="Include groceries, restaurants, and food delivery")
        transport = st.number_input("🚌 Transport", min_value=0, value=500, step=50,
                                   help="Bus, auto, petrol, or metro fares")
    with col2:
        education = st.number_input("📚 Education", min_value=0, value=500, step=100,
                                   help="Tuition, books, online courses")
        utilities = st.number_input("💡 Utilities", min_value=0, value=300, step=50,
                                   help="Electricity, water, internet, mobile")

with expense_tabs[1]:  # Lifestyle
    col1, col2 = st.columns(2)
    with col1:
        entertainment = st.number_input("🎬 Entertainment", min_value=0, value=300, step=50,
                                       help="Movies, games, subscriptions")
        shopping = st.number_input("🛍️ Shopping", min_value=0, value=200, step=50,
                                  help="Clothes, gadgets, personal items")
    with col2:
        health = st.number_input("🏥 Health & Fitness", min_value=0, value=200, step=50,
                                help="Gym, medicine, doctor visits")
        others_lifestyle = st.number_input("📦 Other Lifestyle", min_value=0, value=100, step=50,
                                          help="Miscellaneous lifestyle expenses")

with expense_tabs[2]:  # Financial
    col1, col2 = st.columns(2)
    with col1:
        debt = st.number_input("💳 Debt/EMI", min_value=0, value=0, step=100,
                              help="Loan repayments, credit card bills")
        savings = st.number_input("🐖 Savings/Investment", min_value=0, value=0, step=100,
                                 help="Money set aside for future")
    with col2:
        insurance = st.number_input("🛡️ Insurance", min_value=0, value=0, step=50,
                                   help="Health, bike, or other insurance")
        others_financial = st.number_input("💰 Other Financial", min_value=0, value=0, step=50,
                                          help="Taxes, fees, etc.")

# Compile expenses
expenses = {
    "Food & Dining": food,
    "Transport": transport,
    "Education": education,
    "Utilities": utilities,
    "Entertainment": entertainment,
    "Shopping": shopping,
    "Health & Fitness": health,
    "Debt/EMI": debt,
    "Savings/Investment": savings,
    "Insurance": insurance,
    "Other Lifestyle": others_lifestyle,
    "Other Financial": others_financial,
}

st.session_state.expenses = expenses

# Quick expense summary
total_expenses = sum(expenses.values())
if total_expenses > 0:
    st.markdown("### 💡 Expense Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Expenses", f"₹{total_expenses:,}")
    with col2:
        if income > 0:
            expense_ratio = (total_expenses / income) * 100
            st.metric("Expense Ratio", f"{expense_ratio:.1f}%")
        else:
            st.metric("Expense Ratio", "N/A")
    with col3:
        if income > 0:
            remaining = income - total_expenses
            st.metric("Remaining", f"₹{remaining:,}", delta=f"{remaining}")
        else:
            st.metric("Remaining", "N/A")

# ─────────────────────────────────────────
# Professional Tool Sections
# ─────────────────────────────────────────

# Bank Statement Analyzer
with st.expander(
    "🧾 Bank Statement Analyzer",
    expanded=st.session_state.active_section == PATH_EXPENSE,
):
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e6fffa, #b2f5ea); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
        <h4 style="color: #065f46; margin: 0;">📄 Smart Statement Analysis</h4>
        <p style="color: #065f46; margin: 0.5rem 0 0 0; font-size: 0.9rem;">
            Paste your bank/UPI statements and get instant insights
        </p>
    </div>
    """, unsafe_allow_html=True)

    statement_text = st.text_area(
        "Paste your statement lines:",
        height=150,
        placeholder=(
            "Example:\n"
            "2024-04-01 | Swiggy | Food delivery | ₹-350.00\n"
            "2024-04-01 | Salary credit | Income | ₹15000.00\n"
            "2024-04-02 | Uber | Transport | ₹-120.00"
        ),
        help="Copy-paste from your bank statement or UPI app"
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        analyze_statement = st.button("📊 Analyze", use_container_width=True, type="primary")

    if analyze_statement:
        if statement_text.strip():
            with st.spinner("🔍 Analyzing your statements..."):
                stmt_result = run_statement_analyzer(statement_text, income=income)

            # Professional results display
            st.markdown("### 📈 Analysis Results")

            # Summary metrics
            summary = stmt_result["summary"]
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("💰 Total Spent", f"₹{summary['total_spent']:,}")
            with col2:
                if summary["savings_estimate"] is not None:
                    st.metric("💸 Est. Savings", f"₹{summary['savings_estimate']:,}")
                else:
                    st.metric("💸 Est. Savings", "N/A")
            with col3:
                st.metric("📊 Transactions", len(stmt_result.get("transactions", [])))
            with col4:
                if income > 0 and summary["savings_estimate"] is not None:
                    savings_rate = (summary["savings_estimate"] / income) * 100
                    st.metric("📈 Savings Rate", f"{savings_rate:.1f}%")

            # Spending breakdown
            if summary["top_categories"]:
                st.markdown("#### 🏷️ Top Spending Categories")
                for cat in summary["top_categories"]:
                    st.write(f"• **{cat['category']}**: ₹{cat['amount']:,}")

            # Recommendations
            if stmt_result["recommendations"]:
                st.markdown("#### 💡 Smart Recommendations")
                for rec in stmt_result["recommendations"]:
                    st.success(f"✓ {rec}")

            # Transaction details
            if stmt_result["transactions"]:
                st.markdown("#### 📋 Detailed Transactions")
                st.dataframe(
                    stmt_result["transactions"],
                    use_container_width=True,
                    column_config={
                        "amount": st.column_config.NumberColumn("Amount (₹)", format="₹%d"),
                        "date": st.column_config.DateColumn("Date"),
                    }
                )

            # Export option
            if st.button("📄 Generate PDF Report", help="Download detailed financial report"):
                with st.spinner("Generating PDF report..."):
                    pdf_data = generate_report(
                        name=name or "User",
                        age=age,
                        income=income,
                        expenses=expenses,
                        result={
                            "total_income": income,
                            "total_expenses": summary['total_spent'],
                            "savings": summary.get('savings_estimate', 0),
                            "savings_rate": (summary.get('savings_estimate', 0) / income * 100) if income > 0 else 0,
                            "financial_health": "Good" if summary.get('savings_estimate', 0) > 0 else "Needs Attention"
                        },
                        crisis={"level": "Low Risk", "alerts": []},
                        schemes=[],
                        action_plan=[]
                    )
                st.download_button(
                    label="⬇️ Download PDF Report",
                    data=pdf_data,
                    file_name=f"financial_report_{name or 'user'}.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning("⚠️ Please paste your statement text first.")

# ─────────────────────────────────────────
# Betting / Fantasy Sports Help
# ─────────────────────────────────────────
with st.expander(
    "🎲 Betting & Fantasy Sports Help",
    expanded=st.session_state.active_section == PATH_BETTING,
):
    betting_input = st.text_area(
    "Describe your betting or fantasy sports situation:",
    height=140,
    placeholder=(
        "e.g. I keep losing money on Dream11 and I can\'t stop,"
        " or I want a safer alternative to betting."
    ),
)

if st.button("💡 Get Safer Alternatives", key="betting_help"):
    if betting_input.strip():
        betting_result = run_betting_alternative(betting_input, {"income": income})
        st.markdown("---")
        st.markdown("### 🎯 Betting Recovery Plan")
        st.write(betting_result["primary_message"])
        st.write(betting_result["recovery_message"])
        st.info(f"Risk level: {betting_result['risk_level'].title()} | Confidence: {betting_result['confidence']}")

        st.markdown("#### Recommended Actions")
        for action in betting_result["recommended_actions"]:
            st.write(f"- {action}")

        st.markdown("#### Safer Alternatives")
        for alt in betting_result["alternative_activities"]:
            st.write(f"- {alt}")

        st.markdown("#### Money Recovery Tips")
        for tip in betting_result["financial_recovery_tips"]:
            st.write(f"- {tip}")

        st.markdown("#### Support Resources")
        for resource in betting_result["support_resources"]:
            st.write(f"- {resource}")
    else:
        st.warning("Please describe your betting situation first.")

# ─────────────────────────────────────────
# Legal Protection Help
# ─────────────────────────────────────────
with st.expander(
    "🛡️ Legal Protection Help",
    expanded=st.session_state.active_section == PATH_LEGAL,
):
    legal_input = st.text_area(
    "Describe the loan or collection issue you are facing:",
    height=140,
    placeholder=(
        "e.g. Recovery agents are calling me, or the loan app charged me hidden fees."
    ),
)

if st.button("📝 Analyze Legal Issue", key="legal_help"):
    if legal_input.strip():
        legal_result = run_legal_protector(legal_input)
        st.markdown("---")
        st.markdown("### 🧾 Legal Protection Summary")
        st.write(legal_result["primary_message"])
        st.success(legal_result["summary"])
        st.info(f"Issue type: {legal_result['issue_type'].replace('_', ' ').title()} | Confidence: {legal_result['confidence']}")

        st.markdown("#### Your Rights")
        for right in legal_result["legal_rights"]:
            st.write(f"- {right}")

        st.markdown("#### What You Can Do")
        for step in legal_result["action_plan"]:
            st.write(f"- {step}")

        st.markdown("#### Contact Options")
        for contact in legal_result["contact_options"]:
            st.write(f"- {contact}")
    else:
        st.warning("Please describe your legal issue before analyzing.")

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
# AI Chatbot with Intelligent Routing (ChatRouter)
# ─────────────────────────────────────────
st.markdown("---")
st.markdown("## 🤖 AI Financial Guardian Chat")
st.caption("I understand your situation and route you to the right help! 💬")

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        # Display assistant messages with styling based on type
        with st.chat_message("assistant"):
            st.write(msg["content"])
            if msg.get("response_type"):
                st.caption(f"📍 {msg['response_type'].replace('_', ' ').title()}")
            if msg.get("crisis_level"):
                st.error(f"⚠️ Crisis Level: {msg['crisis_level']}")

# User input with chat interface
user_message = st.chat_input("Describe your financial situation or ask for help 💬")

if user_message and user_message.strip():
    cleaned_message = user_message.strip()
    
    # Display user message immediately
    st.chat_message("user").write(cleaned_message)
    st.session_state.messages.append({
        "role": "user",
        "content": cleaned_message
    })
    
    # Update router context with current user info
    user_context = UserContext(
        income=st.session_state.income,
        monthly_expenses=sum(st.session_state.expenses.values()),
        savings_rate=st.session_state.savings_rate,
    )
    st.session_state.chat_router.set_user_context(user_context)
    
    # Process message with ChatRouter (wrapped in async-like behavior)
    with st.spinner("🤖 Analyzing your situation..."):
        try:
            # Use the synchronous version of process_message
            import asyncio
            
            # Create a simple wrapper for synchronous use
            def sync_process_message(user_msg, ctx):
                router = st.session_state.chat_router
                
                # Manually call the routing logic
                crisis_level = router._detect_crisis(user_msg)
                if crisis_level == "Immediate Crisis":
                    return router._generate_crisis_response(user_msg)
                
                path = router._detect_situation(user_msg)
                
                # Route to specialized handler
                routed_response = None
                response_type = ResponseType.GENERAL_ADVICE
                
                if path == PATH_DEBT:
                    routed_response = router._route_to_debt_handler(user_msg)
                    response_type = ResponseType.DEBT_GUIDANCE
                elif path == PATH_BETTING:
                    routed_response = router._route_to_betting_helper(user_msg)
                    response_type = ResponseType.BETTING_HELP
                elif path == PATH_ZERO_INVESTMENT:
                    routed_response = router._route_to_earning_suggester(user_msg)
                    response_type = ResponseType.EARNING_TIP
                elif path == PATH_INVEST:
                    routed_response = router._route_to_investment_guide(user_msg)
                    response_type = ResponseType.INVESTMENT
                elif path == PATH_LEGAL:
                    routed_response = router._route_to_legal_helper(user_msg)
                    response_type = ResponseType.LEGAL
                elif path == PATH_MENTAL_HEALTH:
                    response_type = ResponseType.MENTAL_HEALTH
                elif path == PATH_EXPENSE:
                    response_type = ResponseType.EXPENSE_TRACKING
                elif path == PATH_UNKNOWN:
                    response_type = ResponseType.CLARIFICATION
                
                # Use routed response or generate with LLM
                if routed_response:
                    final_message = routed_response
                else:
                    history = router._get_relevant_history(num_messages=3)
                    messages = build_messages_with_history(
                        user_message=user_msg,
                        chat_history=history,
                        income=ctx.income,
                        savings_rate=ctx.savings_rate,
                    )
                    final_message = generate_with_retry(
                        provider=router.provider,
                        model=router.model,
                        messages=messages,
                        max_tokens=500,
                        temperature=0.7,
                    )
                
                # Create response object
                response = type('RouterResponse', (), {
                    'message': final_message,
                    'response_type': response_type,
                    'path': path,
                    'crisis_level': crisis_level
                })()
                
                return response
            
            # Call the synchronous routing
            response = sync_process_message(cleaned_message, user_context)
            
            logger.info(
                f"Chat routed: path={response.path}, type={response.response_type.value}"
            )
            
        except LLMError as e:
            response_msg = (
                "⚠️ I'm having trouble connecting right now. "
                "Please try again in a moment!"
            )
            response_type = ResponseType.GENERAL_ADVICE
            logger.error(f"LLM failed in chat: {e}")
        except Exception as e:
            response_msg = (
                "⚠️ Something went wrong while analyzing your situation. "
                "Please try again!"
            )
            response_type = ResponseType.GENERAL_ADVICE
            logger.error(f"Unexpected chat error: {e}")
            response = type('obj', (object,), {
                'message': response_msg,
                'response_type': ResponseType.GENERAL_ADVICE,
                'path': None,
                'crisis_level': None
            })()
    
    # Display assistant response
    with st.chat_message("assistant"):
        st.write(response.message)
        
        # Show metadata
        cols = st.columns(3)
        with cols[0]:
            if response.path:
                st.caption(f"🧭 Path: {response.path.replace('PATH_', '').title()}")
        with cols[1]:
            st.caption(f"📍 Type: {response.response_type.value.replace('_', ' ').title()}")
        with cols[2]:
            if response.crisis_level:
                st.caption(f"⚠️ {response.crisis_level}")
    
    # Store in session
    st.session_state.messages.append({
        "role": "assistant",
        "content": response.message,
        "response_type": response.response_type.value,
        "path": response.path,
        "crisis_level": response.crisis_level
    })

# Chat management buttons
col1, col2, col3 = st.columns(3)
with col1:
    if st.session_state.messages:
        if st.button("📋 Show Summary", use_container_width=True):
            summary = st.session_state.chat_router.get_conversation_summary()
            st.info(f"Conversation Summary:\n{summary}")

with col2:
    if st.session_state.messages:
        if st.button("📊 Export Chat", use_container_width=True):
            chat_text = "\n".join([
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in st.session_state.messages
            ])
            st.download_button(
                label="⬇️ Download Chat",
                data=chat_text,
                file_name="financial_chat.txt",
                mime="text/plain",
                use_container_width=True
            )

with col3:
    if st.session_state.messages:
        if st.button("🗑 Clear Chat", use_container_width=True):
            st.session_state.messages.clear()
            st.session_state.chat_router.clear_history()
            st.rerun()

st.markdown("---")