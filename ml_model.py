import logging
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np
from pathlib import Path
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures

# ─── Logging ────────────────────────────────────────────────
logger = logging.getLogger(__name__)

# ─── Constants ──────────────────────────────────────────────
POLYNOMIAL_DEGREE    = 2
RIDGE_ALPHA          = 0.1
CI_T_VALUE           = 1.96
MAX_EXPENSE_RATIO    = 10.0
MAX_EXPENSE_RISK_CAP = 3.0
MIN_HISTORY_POINTS   = 3
MODEL_PATH           = Path("models/financial_model.pkl")


def calculate_financial_features(
    debt_amount: float,
    income: float,
    expenses: float,
    total_assets: Optional[float] = None,
) -> Dict[str, float]:
    """
    Calculate financial ratios with mathematical precision.

    Returns:
        dict with keys: debt_ratio, expense_ratio, savings_rate, cash_flow
    """
    # Input validation
    if debt_amount < 0:
        raise ValueError(f"debt_amount cannot be negative, got {debt_amount}")
    if expenses < 0:
        raise ValueError(f"expenses cannot be negative, got {expenses}")
    if total_assets is not None and total_assets < 0:
        raise ValueError(f"total_assets cannot be negative, got {total_assets}")

    if income == 0:
        debt_ratio   = debt_amount / (debt_amount + (total_assets or 0.001))
        expense_ratio = 1.0 if expenses > 0 else 0.0
        savings_rate  = 0.0
    else:
        denominator   = debt_amount + (total_assets or 0)
        debt_ratio    = debt_amount / denominator if denominator > 0 else 0.0
        expense_ratio = min(max(expenses / income, 0.0), MAX_EXPENSE_RATIO)
        savings_rate  = (income - expenses) / income

    logger.debug(
        f"Features calculated — debt_ratio={debt_ratio:.4f}, "
        f"expense_ratio={expense_ratio:.4f}, savings_rate={savings_rate:.4f}"
    )

    return {
        'debt_ratio'   : round(debt_ratio, 4),
        'expense_ratio': round(expense_ratio, 4),
        'savings_rate' : round(savings_rate, 4),
        'cash_flow'    : round(income - expenses, 4)
    }

def train_model(
    financial_history: List[float],
) -> Tuple[object, float]:
    """
    Train polynomial regression model with Ridge regularization.

    Returns:
        Tuple of (fitted_model, r2_score)
    """
    # Input validation
    if not financial_history:
        raise ValueError("financial_history cannot be empty")
    if len(financial_history) < MIN_HISTORY_POINTS:
        raise ValueError(
            f"Need at least {MIN_HISTORY_POINTS} data points, "
            f"got {len(financial_history)}"
        )
    if not all(isinstance(x, (int, float)) for x in financial_history):
        raise TypeError("All values in financial_history must be numeric")

    X = np.array(range(len(financial_history))).reshape(-1, 1)
    y = np.array(financial_history)

    model = make_pipeline(
        PolynomialFeatures(degree=POLYNOMIAL_DEGREE, include_bias=False),
        Ridge(alpha=RIDGE_ALPHA)
    )
    model.fit(X, y)

    r2 = model.score(X, y)
    if r2 < 0.7:
        logger.warning(f"Low R²={r2:.4f} — predictions may be unreliable")
    else:
        logger.info(f"Model trained successfully — R²={r2:.4f}")

    return model, r2


def save_model(model, path: Path = MODEL_PATH) -> None:
    """Save trained model to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    logger.info(f"Model saved to {path}")


def load_model(path: Path = MODEL_PATH):
    """Load trained model from disk."""
    if not path.exists():
        raise FileNotFoundError(f"No saved model found at {path}")
    logger.info(f"Model loaded from {path}")
    return joblib.load(path)


def predict_future_with_ci(
    model,
    current_months: int,
    months_ahead: int = 3,
    history: Optional[List[float]] = None,
) -> List[Dict]:
    """
    Predict future savings with 95% confidence intervals.
    Uses matrix leverage calculation correct for polynomial features.
    """
    if history is None or len(history) < 2:
        raise ValueError("Need at least 2 historical points for confidence intervals")

    X_train = np.array(range(len(history))).reshape(-1, 1)
    y_train = np.array(history)
    n       = len(history)

    y_pred     = model.predict(X_train)
    mse        = np.mean((y_train - y_pred) ** 2)

    poly   = model.named_steps['polynomialfeatures']
    ridge  = model.named_steps['ridge']

    X_design   = poly.transform(X_train)
    I          = np.eye(X_design.shape[1])
    cov_matrix = np.linalg.pinv(X_design.T @ X_design + ridge.alpha * I)

    predictions = []
    for i in range(1, months_ahead + 1):
        future_month = np.array([[current_months + i]])
        predicted    = model.predict(future_month)[0]
        x_new_poly   = poly.transform(future_month)

        # ✅ Correct leverage for polynomial space
        leverage  = (x_new_poly @ cov_matrix @ x_new_poly.T).item()
        std_error = np.sqrt(mse * (1 + leverage))

        ci_lower = max(predicted - CI_T_VALUE * std_error, 0)
        ci_upper = predicted + CI_T_VALUE * std_error

        predictions.append({
            "month"      : f"Month {current_months + i}",
            "predicted"  : round(max(predicted, 0), 2),
            "ci_95_lower": round(ci_lower, 2),
            "ci_95_upper": round(ci_upper, 2),
            "ci_width"   : round(ci_upper - ci_lower, 2),
        })

    return predictions


def calculate_risk_score(
    financial_features: Dict[str, float],
) -> float:
    """
    Calculate weighted financial risk score.
    Score ∈ [0,1] where 0=low risk, 1=high risk.
    """
    debt_ratio    = financial_features['debt_ratio']
    expense_ratio = min(financial_features['expense_ratio'], MAX_EXPENSE_RISK_CAP)
    savings_rate  = max(min(financial_features['savings_rate'], 1.0), -1.0)

    risk_score = (
        0.5 * debt_ratio +
        0.3 * min(expense_ratio, 1.0) +
        0.2 * (1.0 - max(savings_rate, 0.0))
    )

    return max(0.0, min(1.0, round(risk_score, 4)))

def get_trend(financial_history: List[float]) -> str:
    """
    Analyze savings trend and return a friendly message.
    
    Args:
        financial_history: List of past savings amounts
        
    Returns:
        A natural language description of the trend
    """
    if not financial_history or len(financial_history) < 2:
        return "📊 Not enough data to determine trend yet. Keep tracking your savings!"
    
    # Calculate simple trend using first and last values
    first = financial_history[0]
    last  = financial_history[-1]
    
    if first == 0:
        if last > 0:
            return "📈 Great start! You're building savings momentum!"
        return "📊 Your savings journey is just beginning. Keep going!"
    
    change_percent = ((last - first) / first) * 100
    
    if change_percent > 20:
        return f"🚀 Excellent! Your savings are growing strongly ({change_percent:.1f}% increase)"
    elif change_percent > 5:
        return f"📈 Good progress! Your savings are trending upward ({change_percent:.1f}% increase)"
    elif change_percent > -5:
        return "📊 Your savings are stable. Small adjustments can boost growth!"
    elif change_percent > -20:
        return f"📉 Savings dipped slightly ({abs(change_percent):.1f}% decrease). Let's get back on track!"
    else:
        return f"⚠️ Savings dropped significantly ({abs(change_percent):.1f}% decrease). Time for a financial reset!"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    features = calculate_financial_features(
        debt_amount=25000,
        income=60000,
        expenses=45000,
        total_assets=100000,
    )
    print(f"Features   : {features}")
    print(f"Risk Score : {calculate_risk_score(features):.1%}")

    savings_history = [500, 800, 1200, 1500, 1800, 2000]
    model, r2 = train_model(savings_history)
    print(f"R² Score   : {r2:.4f}")

    predictions = predict_future_with_ci(
        model,
        current_months=len(savings_history),
        months_ahead=3,
        history=savings_history,
    )
    for pred in predictions:
        print(
            f"{pred['month']}: ₹{pred['predicted']:.2f} "
            f"(95% CI: ₹{pred['ci_95_lower']:.2f} - ₹{pred['ci_95_upper']:.2f})"
        )