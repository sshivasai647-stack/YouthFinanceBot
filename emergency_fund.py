# emergency_fund.py
# Purpose: Helps youth understand and build an emergency fund

import logging
from typing import Union

logger = logging.getLogger(__name__)


def calculate_emergency_fund(
    monthly_expenses: float,
    months          : int = 6,
) -> dict:
    """
    Calculates minimum and recommended emergency fund targets.
    Standard rule: 3 months minimum, 6 months recommended.

    Args:
        monthly_expenses : Total monthly spending (₹)
        months           : Recommended months of coverage (default 6)

    Returns:
        dict with minimum_fund, recommended_fund, months_covered
    """
    if monthly_expenses < 0:
        raise ValueError(f"monthly_expenses cannot be negative, got {monthly_expenses}")

    minimum_fund     = monthly_expenses * 3
    recommended_fund = monthly_expenses * months

    logger.info(
        f"Emergency fund calculated: "
        f"min=₹{minimum_fund} | recommended=₹{recommended_fund}"
    )

    return {
        "minimum_fund"    : minimum_fund,
        "recommended_fund": recommended_fund,
        "months_covered"  : months,
    }


def _months_to_save(remaining: float, monthly: float) -> Union[int, str]:
    """Returns months needed or 'N/A' if monthly contribution is zero."""
    if monthly <= 0:
        return "N/A"
    return round(remaining / monthly)


def get_building_plan(
    target_amount  : float,
    current_savings: float,
    monthly_income : float,
) -> dict:
    """
    Creates 3 realistic speed-based plans to build emergency fund.

    Args:
        target_amount   : Recommended emergency fund amount (₹)
        current_savings : How much user has saved already (₹)
        monthly_income  : User's monthly income (₹)

    Returns:
        dict with status, remaining amount, and list of plan options
    """
    remaining = max(target_amount - current_savings, 0)

    # ✅ Fixed — consistent return shape for complete and incomplete cases
    if remaining == 0:
        logger.info("Emergency fund already complete")
        return {
            "status"   : "complete",
            "remaining": 0,
            "plans"    : [],
        }

    fast   = monthly_income * 0.20
    medium = monthly_income * 0.10
    slow   = monthly_income * 0.05

    plans = [
        {
            "name"       : "Aggressive",
            "emoji"      : "🚀",
            "monthly"    : round(fast),
            "months"     : _months_to_save(remaining, fast),
            "description": "Save 20% of income. Fastest way but needs discipline!",
        },
        {
            "name"       : "Balanced",
            "emoji"      : "⚖️",
            "monthly"    : round(medium),
            "months"     : _months_to_save(remaining, medium),
            "description": "Save 10% of income. Comfortable and realistic!",
        },
        {
            "name"       : "Slow & Steady",
            "emoji"      : "🐢",
            "monthly"    : round(slow),
            "months"     : _months_to_save(remaining, slow),
            "description": "Save 5% of income. Very easy, takes longer but still works!",
        },
    ]

    logger.info(
        f"Building plan created: "
        f"target=₹{target_amount} | "
        f"saved=₹{current_savings} | "
        f"remaining=₹{remaining} | "
        f"income=₹{monthly_income}"
    )

    return {
        "status"         : "incomplete",
        "remaining"      : remaining,
        "current_savings": current_savings,
        "plans"          : plans,
    }


def get_emergency_tip(savings_rate: float) -> str:
    """
    Returns actionable tip based on current savings rate (0-100 scale).
    """
    if savings_rate >= 20:
        return (
            "You're saving well! Dedicate at least 3 months of expenses "
            "as emergency fund before investing anywhere else."
        )
    elif savings_rate >= 10:
        return (
            "Good savings habit! Try to build your emergency fund first "
            "before spending on wants."
        )
    else:
        return (
            "Start small! Even saving ₹100/week builds an emergency fund "
            "over time. Start today!"
        )


# ─── Standalone Test ─────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    monthly_expenses = 5000
    monthly_income   = 10000
    current_savings  = 2000

    fund = calculate_emergency_fund(monthly_expenses)
    plan = get_building_plan(
        fund["recommended_fund"],
        current_savings,
        monthly_income,
    )

    print("=== Emergency Fund Calculator ===")
    print(f"Minimum Fund Needed:     ₹{fund['minimum_fund']}")
    print(f"Recommended Fund Needed: ₹{fund['recommended_fund']}")
    print(f"You Currently Have:      ₹{current_savings}")
    print(f"Remaining to Build:      ₹{plan['remaining']}")

    print("\n=== Your Building Plans ===")
    for p in plan["plans"]:
        months_str = (
            f"{p['months']} months" if p["months"] != "N/A"
            else "Not possible (zero income)"
        )
        print(f"\n{p['emoji']} {p['name']} Plan")
        print(f"   Save ₹{p['monthly']}/month")
        print(f"   Reach goal in {months_str}")
        print(f"   {p['description']}")

    # Edge case test
    print("\n=== Edge Case: Zero Income ===")
    zero_plan = get_building_plan(30000, 0, 0)
    for p in zero_plan["plans"]:
        print(f"{p['name']}: ₹{p['monthly']}/mo → {p['months']}")

    # Edge case test: already complete
    print("\n=== Edge Case: Already Complete ===")
    done = get_building_plan(30000, 35000, 10000)
    print(f"Status: {done['status']}")