"""
financial_engine.py
===================
Calculates core financial metrics for the user to provide a real-time snapshot of their financial health.
"""
import datetime

def calculate_survival_days(savings: float, expenses: float) -> int:
    """Calculates how many days the user can survive on current savings."""
    if expenses <= 0:
        return 9999  # effectively infinite if no expenses
    daily_expenses = expenses / 30.0
    return int(savings / daily_expenses) if daily_expenses > 0 else 0

def calculate_savings_rate(income: float, expenses: float) -> float:
    """Calculates the percentage of income being saved."""
    if income <= 0:
        return 0.0
    rate = ((income - expenses) / income) * 100.0
    return round(max(0.0, min(rate, 100.0)), 2)

def calculate_debt_free_date(total_debt: float, income: float, expenses: float) -> str:
    """Estimates the month and year the user will be debt-free."""
    if total_debt <= 0:
        return datetime.datetime.now().strftime("%B %Y")
    
    monthly_surplus = income - expenses
    if monthly_surplus <= 0:
        return "Never (monthly deficit)"
    
    months_to_payoff = int(total_debt / monthly_surplus) + (1 if total_debt % monthly_surplus > 0 else 0)
    
    now = datetime.datetime.now()
    total_months = now.month + months_to_payoff
    year = now.year + ((total_months - 1) // 12)
    month = ((total_months - 1) % 12) + 1
    
    payoff_date = datetime.date(year, month, 1)
    return payoff_date.strftime("%B %Y")

def calculate_financial_health_score(savings_rate: float, total_debt: float, income: float, survival_days: int) -> int:
    """Calculates a comprehensive 0-100 financial health score."""
    score = 50  # Base score
    
    # 1. Savings rate contribution (-10 to +25)
    if savings_rate >= 20:
        score += 25
    elif savings_rate >= 10:
        score += 15
    elif savings_rate > 0:
        score += 5
    else:
        score -= 10
        
    # 2. Debt burden contribution (-20 to +15)
    if income > 0:
        debt_to_income = total_debt / income
        if debt_to_income == 0:
            score += 15
        elif debt_to_income < 0.3:
            score += 5
        elif debt_to_income > 1.0:
            score -= 20
        elif debt_to_income > 0.5:
            score -= 10
            
    # 3. Emergency fund contribution (-15 to +10)
    if survival_days >= 180:
        score += 10
    elif survival_days >= 90:
        score += 5
    elif survival_days < 30:
        score -= 15
        
    return max(0, min(100, int(score)))

def get_financial_snapshot(income: float, expenses: float, savings: float, total_debt: float) -> dict:
    """Aggregates all calculations into a single financial snapshot."""
    survival_days = calculate_survival_days(savings, expenses)
    savings_rate = calculate_savings_rate(income, expenses)
    debt_free_date = calculate_debt_free_date(total_debt, income, expenses)
    health_score = calculate_financial_health_score(savings_rate, total_debt, income, survival_days)
    
    return {
        "survival_days": survival_days,
        "savings_rate": savings_rate,
        "debt_free_date": debt_free_date,
        "financial_health_score": health_score
    }
