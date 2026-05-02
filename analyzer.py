# analyzer.py
# Purpose: Analyzes user spending and returns financial summary

import logging
from typing import Dict

logger = logging.getLogger(__name__)


def analyze_spending(
    income  : float,
    expenses: Dict[str, float],
    debt    : float = 0,
) -> Dict:
    """
    Analyzes user spending and returns complete financial summary.

    Args:
        income   : Monthly income (₹)
        expenses : Category-wise expense dict (₹)
        debt     : Monthly debt/EMI payments (₹), default 0

    Returns:
        dict with savings, savings_rate, financial_health, etc.
    """
    if income < 0:
        raise ValueError(f"income cannot be negative, got {income}")
    if debt < 0:
        raise ValueError(f"debt cannot be negative, got {debt}")

    # ✅ Fixed — debt included in total expenses
    total_expenses = sum(expenses.values()) + debt
    savings        = income - total_expenses
    savings_rate   = (savings / income) * 100 if income > 0 else 0.0

    # Financial health thresholds
    if savings_rate >= 30:
        health = "🟢 Excellent"
    elif savings_rate >= 20:
        health = "🟡 Good"
    elif savings_rate >= 10:
        health = "🟠 Average"
    else:
        health = "🔴 Poor"

    # Highest expense from base categories only (not debt)
    if expenses:
        highest_category = max(expenses, key=expenses.get)
        highest_amount   = expenses[highest_category]
    else:
        highest_category = "N/A"
        highest_amount   = 0

    logger.info(
        f"Analysis complete — income=₹{income} | "
        f"expenses=₹{total_expenses} | debt=₹{debt} | "
        f"savings=₹{savings} | rate={savings_rate:.1f}% | "
        f"health={health}"
    )

    return {
        "total_income"             : income,
        "total_expenses"           : total_expenses,
        "savings"                  : savings,
        "savings_rate"             : round(savings_rate, 2),
        "financial_health"         : health,
        "highest_expense_category" : highest_category,
        "highest_expense_amount"   : highest_amount,
    }


def get_saving_tip(savings_rate: float) -> str:
    """
    Returns personalized saving tip based on savings rate (0-100 scale).
    """
    if savings_rate >= 30:
        return "💪 Amazing! You're saving really well. Consider investing your extra savings!"
    elif savings_rate >= 20:
        return "👍 Good job! Try to push your savings to 30% by cutting entertainment costs."
    elif savings_rate >= 10:
        return "⚠️ You're saving but it's not enough. Try the 50-30-20 rule!"
    else:
        return "🚨 You need to save more! Start by cutting your biggest expense category."


# ─── Standalone Test ─────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    test_income   = 10000
    test_expenses = {
        "Food"         : 3000,
        "Transport"    : 500,
        "Education"    : 1000,
        "Entertainment": 500,
        "Others"       : 500,
    }
    test_debt = 500

    # Test 1: With debt
    result = analyze_spending(test_income, test_expenses, test_debt)
    print("=== Financial Analysis (with debt) ===")
    for key, value in result.items():
        print(f"  {key}: {value}")

    # Test 2: Without debt (backward compat check)
    result2 = analyze_spending(test_income, test_expenses)
    print("\n=== Financial Analysis (no debt) ===")
    print(f"  savings     : ₹{result2['savings']}")
    print(f"  savings_rate: {result2['savings_rate']}%")

    # Test 3: Zero income edge case
    result3 = analyze_spending(0, test_expenses, 0)
    print("\n=== Edge Case: Zero Income ===")
    print(f"  savings_rate : {result3['savings_rate']}%")
    print(f"  health       : {result3['financial_health']}")

    tip = get_saving_tip(result["savings_rate"])
    print(f"\n=== Saving Tip ===\n  {tip}")