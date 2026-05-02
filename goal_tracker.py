# goal_tracker.py
# Purpose: Financial goal creation, tracking, and multi-goal optimization

import copy
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def _is_unfunded(months) -> bool:
    """Single source of truth for 'goal cannot be funded' check."""
    return months == float("inf") or months >= 600


# ─────────────────────────────────────────────────────────────
# SIMPLE FUNCTIONS — used by app.py imports
# ─────────────────────────────────────────────────────────────

def create_goal(
    goal_name        : str,
    target_amount    : float,
    months_to_achieve: int,
) -> Dict:
    """
    Creates a goal dict with monthly required savings.
    Used by app.py simple goal tracker section.

    Args:
        goal_name         : Display name for the goal
        target_amount     : Total amount needed (₹)
        months_to_achieve : How many months to reach it

    Returns:
        Goal dict with monthly_required pre-calculated
    """
    if target_amount <= 0:
        raise ValueError(f"target_amount must be positive, got {target_amount}")
    if months_to_achieve <= 0:
        raise ValueError(
            f"months_to_achieve must be positive, got {months_to_achieve}"
        )

    monthly_required = round(target_amount / months_to_achieve, 2)

    goal = {
        "name"            : goal_name,
        "target_amount"   : target_amount,
        "months"          : months_to_achieve,
        "monthly_required": monthly_required,
        "created_at"      : datetime.now().date().isoformat(),
    }

    logger.info(
        f"Goal created: '{goal_name}' | "
        f"Target=₹{target_amount} | "
        f"Monthly=₹{monthly_required} | "
        f"Months={months_to_achieve}"
    )
    return goal


def check_progress(
    goal           : Dict,
    current_monthly: float,
) -> Dict:
    """
    Checks progress toward a goal given current monthly savings.
    Used by app.py simple goal tracker section.

    Args:
        goal            : Goal dict from create_goal()
        current_monthly : What user is actually saving per month (₹)

    Returns:
        dict with progress_percent, status, encouragement, monthly_gap
    """
    monthly_required = goal["monthly_required"]

    if monthly_required <= 0:
        progress_percent = 100.0
    else:
        progress_percent = round(
            min((current_monthly / monthly_required) * 100, 100), 1
        )

    if progress_percent >= 100:
        status        = "🟢 On Track"
        encouragement = "You're fully on track! Keep it up! 🎉"
    elif progress_percent >= 60:
        status        = "🟡 Almost There"
        encouragement = (
            f"Save ₹{monthly_required - current_monthly:.0f} more/month "
            f"to hit your goal!"
        )
    else:
        status        = "🔴 Needs Attention"
        encouragement = (
            f"You need ₹{monthly_required - current_monthly:.0f} more/month. "
            f"Let's find ways to save!"
        )

    logger.info(
        f"Progress check: '{goal['name']}' | "
        f"Progress={progress_percent}% | Status={status}"
    )

    return {
        "progress_percent": progress_percent,
        "status"          : status,
        "encouragement"   : encouragement,
        "monthly_gap"     : max(monthly_required - current_monthly, 0),
    }


# ─────────────────────────────────────────────────────────────
# ADVANCED MATH ENGINE
# ─────────────────────────────────────────────────────────────

class GoalOptimizer:
    """
    Inflation-aware goal optimization engine.

    Formulas used:
    - Inflation-adjusted target : FV = PV × (1 + i)^n
    - Real return               : r_real = (1 + r_nominal)/(1 + i) - 1
    - Monthly savings (PMT)     : PMT = FV × r / [(1 + r)^n - 1]
    """

    def __init__(
        self,
        annual_inflation : float = 0.05,
        investment_return: float = 0.08,
    ):
        self.annual_inflation  = annual_inflation
        self.investment_return = investment_return
        self.monthly_inflation = (1 + annual_inflation) ** (1 / 12) - 1
        self.monthly_return    = (1 + investment_return) ** (1 / 12) - 1
        self.real_return       = self._calculate_real_return()

    def _calculate_real_return(self) -> float:
        return (1 + self.monthly_return) / (1 + self.monthly_inflation) - 1

    def inflation_adjusted_target(
        self,
        present_cost: float,
        months      : int,
    ) -> float:
        return present_cost * (1 + self.monthly_inflation) ** months

    def required_monthly_savings(
        self,
        future_value: float,
        months      : int,
    ) -> float:
        if self.real_return == 0 or months == 0:
            return future_value / max(months, 1)
        return future_value * self.real_return / (
            (1 + self.real_return) ** months - 1
        )

    def months_to_goal(
        self,
        target         : float,
        monthly_savings: float,
        current_saved  : float = 0,
    ) -> Tuple[int, List[Dict]]:
        """
        Iterative timeline calculation with inflation-adjusted target.
        Capped at 600 months (50 years).

        Args:
            target          : Goal amount in today's ₹
            monthly_savings : How much saved each month
            current_saved   : Already saved amount (default 0)
        """
        months  = 0
        balance = current_saved
        history = []

        while balance < target and months < 600:
            months          += 1
            balance         *= (1 + self.real_return)
            balance         += monthly_savings
            adjusted_target  = target * (1 + self.monthly_inflation) ** months

            history.append({
                "month"  : months,
                "balance": round(balance, 2),
                "target" : round(adjusted_target, 2),
                "deficit": round(adjusted_target - balance, 2),
            })

            if balance >= adjusted_target:
                break

        if months >= 600:
            logger.warning(
                f"months_to_goal hit 600-month cap | "
                f"target=₹{target} | monthly_savings=₹{monthly_savings}"
            )

        return months, history

    def prioritize_goals(
        self,
        goals              : List[Dict],
        available_monthly  : float,
        emergency_fund_months: int = 3,
    ) -> List[Dict]:
        """
        Returns a new list — never mutates the input goals.
        Priority: emergency > high debt > moderate debt > investment > luxury

        Args:
            goals               : List of goal dicts (not mutated)
            available_monthly   : Total monthly savings capacity (₹)
            emergency_fund_months: Context passed for future use
        """
        PRIORITY_MAP = {
            "emergency"    : 1,
            "debt_high"    : 2,
            "debt_moderate": 3,
            "investment"   : 4,
            "luxury"       : 5,
        }

        goals_copy   = copy.deepcopy(goals)
        sorted_goals = sorted(
            goals_copy,
            key=lambda x: (
                PRIORITY_MAP.get(x["type"], 99),
                -x.get("urgency", 0),
            ),
        )

        remaining  = available_monthly
        allocation = []

        for goal in sorted_goals:
            required  = self.required_monthly_savings(
                goal["target_amount"],
                goal.get("months", 12),
            )
            allocated = min(required, remaining)

            if allocated > 0:
                goal["allocated_monthly"] = round(allocated, 2)
                # ✅ Fixed — pass current_saved so partial progress counts
                goal["achievement_months"] = self.months_to_goal(
                    goal["target_amount"],
                    allocated,
                    current_saved = goal.get("current_saved", 0),
                )[0]
                remaining -= allocated
            else:
                goal["allocated_monthly"]  = 0
                goal["achievement_months"] = float("inf")

            allocation.append(goal)

        logger.info(
            f"Goal optimization complete: "
            f"{len(allocation)} goals | "
            f"capacity=₹{available_monthly} | "
            f"remaining=₹{remaining:.2f}"
        )
        return allocation


# ─────────────────────────────────────────────────────────────
# ENHANCED STREAMLIT UI
# ─────────────────────────────────────────────────────────────

def enhanced_goal_tracker() -> None:
    """
    Advanced multi-goal tracker with inflation-aware math.
    Reads income/expenses from session_state set by app.py.
    """
    # ✅ Fixed — lazy imports: streamlit + pandas only when UI runs
    import streamlit as st
    import pandas as pd

    st.markdown("## 🎯 Enhanced Goal Tracker")

    # ── 1. Economic Assumptions ──────────────────────────────
    with st.expander("⚙️ Economic Assumptions", expanded=False):
        assumption_col1, assumption_col2 = st.columns(2)
        with assumption_col1:
            annual_inflation = st.slider(
                "Expected Annual Inflation (%)",
                min_value=0.0, max_value=15.0,
                value=5.0, step=0.1,
            ) / 100
        with assumption_col2:
            investment_return = st.slider(
                "Expected Investment Return (%)",
                min_value=0.0, max_value=20.0,
                value=8.0, step=0.1,
            ) / 100

    optimizer = GoalOptimizer(
        annual_inflation  = annual_inflation,
        investment_return = investment_return,
    )

    # ── 2. Add Goals ─────────────────────────────────────────
    st.subheader("➕ Add Financial Goals")

    if "goals" not in st.session_state:
        st.session_state.goals = []

    gc1, gc2, gc3, gc4, gc5 = st.columns([2, 1, 1, 1, 1])

    with gc1:
        name = st.text_input("Goal Name", placeholder="Emergency Fund")
    with gc2:
        target = st.number_input("Target Amount (₹)", min_value=0, value=100000)
    with gc3:
        months = st.number_input("Target Months", min_value=1, value=12)
    with gc4:
        goal_type = st.selectbox(
            "Type",
            ["emergency", "debt_high", "debt_moderate", "investment", "luxury"],
        )
    with gc5:
        urgency = st.slider("Urgency", 1, 10, 5)

    if st.button("➕ Add Goal", key="add_goal"):
        if name.strip():
            st.session_state.goals.append({
                "name"         : name.strip(),
                "target_amount": target,
                "months"       : months,
                "type"         : goal_type,
                "urgency"      : urgency,
                "current_saved": 0,
            })
            logger.info(f"Goal added: '{name}' ₹{target} in {months} months")
            st.success(f"✅ Goal '{name}' added!")
        else:
            st.warning("Please enter a goal name!")

    # ── 3. Display and Delete Goals ──────────────────────────
    if st.session_state.goals:
        st.subheader("📋 Your Goals")
        to_delete = None

        for i, goal in enumerate(st.session_state.goals):
            dc1, dc2, dc3, dc4, dc5 = st.columns([3, 2, 2, 2, 1])
            with dc1:
                st.write(f"**{goal['name']}** ({goal['type']})")
            with dc2:
                st.write(f"₹{goal['target_amount']:,}")
            with dc3:
                st.write(f"{goal['months']} months")
            with dc4:
                st.write(f"Urgency: {goal['urgency']}/10")
            with dc5:
                if st.button("🗑️", key=f"delete_{i}"):
                    to_delete = i

        if to_delete is not None:
            removed = st.session_state.goals.pop(to_delete)
            logger.info(f"Goal deleted: '{removed['name']}'")
            st.rerun()

    # ── 4. Savings Capacity ──────────────────────────────────
    st.subheader("💰 Your Savings Capacity")

    monthly_income   = st.session_state.get("income", 0)
    monthly_expenses = sum(st.session_state.get("expenses", {}).values())
    savings_capacity = monthly_income - monthly_expenses

    st.info(
        f"📊 From your profile — "
        f"Income: ₹{monthly_income:,} | "
        f"Expenses: ₹{monthly_expenses:,} | "
        f"Savings Capacity: ₹{savings_capacity:,}/month"
    )

    # ── 5. Negative Savings Recovery ─────────────────────────
    if savings_capacity < 0:
        st.error("⚠️ **Negative Savings Rate Detected**")
        with st.expander("🔍 Recovery Analysis & Path", expanded=True):
            deficit = abs(savings_capacity)
            st.markdown(f"""
**Current Situation:**
- Monthly Deficit : ₹{deficit:,}
- Annual Deficit  : ₹{deficit * 12:,}

**Recovery Options:**
1. Cut expenses by ₹{deficit + 2000:,}/month
2. Increase income by ₹{deficit * 1.2:,.0f}/month

**Priority Sequence:**
            """)
            for timeframe, action in [
                ("Month 1-3",   "Eliminate all discretionary spending"),
                ("Month 4-6",   "Reduce essential expenses by 20%"),
                ("Month 7-9",   "Add income through side hustles"),
                ("Month 10-12", "Build ₹10,000 emergency buffer"),
            ]:
                st.write(f"**{timeframe}:** {action}")

    # ── 6. Optimize ──────────────────────────────────────────
    elif st.button("🚀 Optimize Goal Allocation", type="primary"):
        if not st.session_state.goals:
            st.warning("Please add at least one goal first!")
        else:
            optimized        = optimizer.prioritize_goals(
                st.session_state.goals,
                savings_capacity,
            )
            total_allocated  = sum(g.get("allocated_monthly", 0) for g in optimized)
            remaining_buffer = savings_capacity - total_allocated

            st.subheader("📊 Optimized Allocation Plan")

            ac1, ac2, ac3 = st.columns(3)
            ac1.metric("Available Monthly",  f"₹{savings_capacity:,.0f}")
            ac2.metric("Allocated to Goals", f"₹{total_allocated:,.0f}")
            ac3.metric("Remaining Buffer",   f"₹{remaining_buffer:,.0f}")

            df = pd.DataFrame(optimized)
            df["Monthly Allocation"] = df["allocated_monthly"].apply(
                lambda x: f"₹{x:,.0f}"
            )
            # ✅ Fixed — single helper for both inf and 600-cap cases
            df["Achievement Time"] = df["achievement_months"].apply(
                lambda x: "Not funded" if _is_unfunded(x) else f"{int(x)} months"
            )
            st.dataframe(
                df[["name", "type", "Monthly Allocation", "Achievement Time"]],
                use_container_width=True,
            )

            # Timeline
            st.subheader("📅 Projected Achievement Timeline")
            timeline_data = [
                {
                    "Goal"         : g["name"],
                    "Start Date"   : datetime.now().date(),
                    "Target Date"  : (
                        datetime.now()
                        + timedelta(days=int(g["achievement_months"]) * 30)
                    ).date(),
                    "Months Needed": int(g["achievement_months"]),
                    "Monthly Save" : f"₹{g['allocated_monthly']:,.0f}",
                }
                for g in optimized
                if g["allocated_monthly"] > 0
                and not _is_unfunded(g["achievement_months"])
            ]

            if timeline_data:
                st.dataframe(
                    pd.DataFrame(timeline_data),
                    use_container_width=True,
                )
            else:
                st.info("No goals are funded with current savings capacity.")

    st.markdown("---")
    st.caption("🔄 Recalculates when income, expenses, or goals change.")


# ─────────────────────────────────────────────────────────────
# MATH VALIDATION
# ─────────────────────────────────────────────────────────────

def test_formulas() -> bool:
    """Validates all optimizer formulas. Safe to run outside Streamlit."""
    optimizer = GoalOptimizer()

    # Test 1 — Inflation adjustment
    adjusted = optimizer.inflation_adjusted_target(100000, 12)
    expected = 100000 * (1 + optimizer.monthly_inflation) ** 12
    assert abs(adjusted - expected) < 0.01, "Inflation formula error"

    # Test 2 — Real return
    real_manual = (
        (1 + optimizer.monthly_return) / (1 + optimizer.monthly_inflation) - 1
    )
    assert abs(optimizer.real_return - real_manual) < 0.0001, "Real return error"

    # Test 3 — Annuity formula round-trip
    # ✅ Fixed — guard against negative real_return (deflation scenario)
    fv  = 100000
    r   = optimizer.real_return
    pmt = optimizer.required_monthly_savings(fv, 12)
    if r > 0 and pmt > 0:
        fv_calc = pmt * ((1 + r) ** 12 - 1) / r
        assert abs(fv - fv_calc) < 0.01, "Annuity formula error"

    return True


# ─────────────────────────────────────────────────────────────
# STANDALONE TEST
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    try:
        test_formulas()
        print("✅ All mathematical formulas validated")
    except AssertionError as e:
        print(f"❌ Formula validation failed: {e}")

    # Simple function tests
    goal     = create_goal("New Phone", 15000, 3)
    progress = check_progress(goal, current_monthly=4000)
    print(f"\nGoal     : {goal}")
    print(f"Progress : {progress}")

    # Optimizer test
    optimizer = GoalOptimizer()
    goals = [
        {
            "name": "Emergency Fund", "target_amount": 30000,
            "months": 6,  "type": "emergency",  "urgency": 10,
            "current_saved": 5000,    # ← partial savings now threaded through
        },
        {
            "name": "New Laptop", "target_amount": 50000,
            "months": 12, "type": "investment", "urgency": 5,
            "current_saved": 0,
        },
        {
            "name": "Vacation", "target_amount": 20000,
            "months": 8,  "type": "luxury",     "urgency": 3,
            "current_saved": 0,
        },
    ]
    result = optimizer.prioritize_goals(goals, available_monthly=8000)
    print("\n=== Optimized Allocation ===")
    for g in result:
        label = "Not funded" if _is_unfunded(g["achievement_months"]) \
                else f"{int(g['achievement_months'])} months"
        print(f"  {g['name']}: ₹{g['allocated_monthly']:,.0f}/month → {label}")