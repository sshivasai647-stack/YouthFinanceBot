"""
statement_analyzer.py
======================
Bank statement analyzer for Youth Financial Guardian Chatbot.

This module parses transaction statements, categorizes spending, and returns
a clear summary of expense patterns and top categories.
"""

import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Transaction:
    date: Optional[str]
    description: str
    amount: float
    category: str
    direction: str  # 'debit' or 'credit'


CATEGORY_KEYWORDS = {
    "Food": ["food", "restaurant", "dining", "swiggy", "zomato", "cafe", "canteen", "meal"],
    "Transport": ["uber", "ola", "bus", "train", "metro", "taxi", "fuel", "petrol", "auto", "cab"],
    "Shopping": ["amazon", "flipkart", "myntra", "shop", "mall", "shopping", "paytm mall", "ajio"],
    "Entertainment": ["movie", "netflix", "primevideo", "spotify", "games", "gaming", "spotify", "bookmyshow"],
    "Education": ["school", "college", "tuition", "course", "exam", "books", "library", "academy"],
    "Utilities": ["electricity", "internet", "wifi", "water", "bill", "dth", "recharge"],
    "Health": ["pharmacy", "hospital", "clinic", "doctor", "medical", "health", "lab"],
    "Recharge": ["mobile recharge", "recharge", "dth", "prepaid"],
    "Rent": ["rent", "room rent", "house rent"],
    "Salary": ["salary", "credit", "payroll", "ctc"],
}

DEFAULT_CATEGORY = "Others"


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def _parse_amount(text: str) -> Optional[float]:
    cleaned = text.replace(',', '').replace('₹', '').replace('inr', '')
    cleaned = cleaned.strip()
    match = re.search(r"(-?\d+[\d\.]*)(?=\D*$)", cleaned)
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def _detect_direction(amount_str: str, description: str) -> str:
    if '-' in amount_str or 'debit' in description or 'spent' in description or 'withdrawal' in description:
        return 'debit'
    return 'credit'


def _categorize_description(description: str) -> str:
    normalized = _normalize_text(description)
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in normalized:
                return category
    return DEFAULT_CATEGORY


def parse_statement_lines(lines: List[str]) -> List[Transaction]:
    transactions: List[Transaction] = []
    for raw in lines:
        text = raw.strip()
        if not text:
            continue

        # Attempt to split on common separators
        parts = re.split(r"\s{2,}|,|\||;|\t", text)
        parts = [p.strip() for p in parts if p.strip()]

        date_candidate, amount_candidate, description = None, None, None
        if len(parts) >= 3:
            if re.match(r"\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4}", parts[0]):
                date_candidate = parts[0]
                amount_candidate = parts[-1]
                description = " ".join(parts[1:-1])
            elif re.match(r"\d+[\d,.]*", parts[-1]):
                amount_candidate = parts[-1]
                description = " ".join(parts[:-1])
            else:
                description = " ".join(parts)
        else:
            description = text
            amount_candidate = re.search(r"-?\d+[\d,.]*", text)
            amount_candidate = amount_candidate.group(0) if amount_candidate else None

        amount = _parse_amount(amount_candidate or "") if amount_candidate else 0.0
        direction = _detect_direction(amount_candidate or "", description or "")

        if direction == 'debit' and amount > 0:
            amount = -amount

        category = _categorize_description(description or text)

        transactions.append(Transaction(
            date=date_candidate,
            description=description or text,
            amount=round(amount, 2),
            category=category,
            direction=direction,
        ))
    return transactions


def summarize_transactions(transactions: List[Transaction], income: Optional[float] = None) -> Dict[str, object]:
    summary: Dict[str, object] = {
        'total_spent': 0.0,
        'total_received': 0.0,
        'category_totals': {},
        'top_categories': [],
        'transaction_count': len(transactions),
        'income': income,
        'savings_estimate': None,
    }

    category_totals: Dict[str, float] = {}
    for txn in transactions:
        if txn.amount < 0:
            category_totals[txn.category] = category_totals.get(txn.category, 0.0) + abs(txn.amount)
            summary['total_spent'] += abs(txn.amount)
        else:
            summary['total_received'] += txn.amount

    summary['category_totals'] = {k: round(v, 2) for k, v in category_totals.items()}
    summary['top_categories'] = sorted(
        [{'category': k, 'amount': v} for k, v in category_totals.items()],
        key=lambda item: item['amount'],
        reverse=True
    )[:5]

    if income is not None:
        savings = income - summary['total_spent']
        summary['savings_estimate'] = round(savings, 2)

    return summary


def analyze_statement(statement_text: str, income: Optional[float] = None) -> Dict[str, object]:
    lines = [line for line in statement_text.splitlines() if line.strip()]
    transactions = parse_statement_lines(lines)
    summary = summarize_transactions(transactions, income=income)

    message = "Here is your statement summary."
    if summary['total_spent'] == 0:
        message = "I could not detect spending transactions clearly. Please provide a clean statement or add more detail."
    elif summary['top_categories']:
        top = summary['top_categories'][0]
        message = (
            f"Your highest spending category is {top['category']} at ₹{top['amount']:.2f}. "
            "I can also help you make a budget from this."
        )

    return {
        'transactions': [
            {
                'date': txn.date,
                'description': txn.description,
                'amount': txn.amount,
                'category': txn.category,
                'direction': txn.direction,
            }
            for txn in transactions
        ],
        'summary': summary,
        'message': message,
        'recommendations': _build_recommendations(summary),
    }


def _build_recommendations(summary: Dict[str, object]) -> List[str]:
    recs: List[str] = []
    if summary['total_spent'] > 0:
        recs.append("Review your top 3 spending categories and cut one small recurring item.")
    if summary['income'] is not None and summary['savings_estimate'] is not None:
        if summary['savings_estimate'] < 0:
            recs.append("Your expenses exceed your income - reduce spending or increase earnings.")
        else:
            recs.append("Try to save at least 20% of your income each month.")
    if summary['top_categories']:
        recs.append("Use a separate wallet or envelope for food and transport money.")
    return recs


def run_statement_analyzer(statement_text: str, income: Optional[float] = None) -> Dict[str, object]:
    return analyze_statement(statement_text, income=income)


if __name__ == "__main__":
    example_statement = """
2024-04-01|Google Pay|Food delivery|₹-350.00
2024-04-01|Salary credit|Income|₹15000.00
2024-04-02|Metro recharge|Transport|₹-300.00
2024-04-05|Swiggy|Dinner|₹-450.00
2024-04-10|Electricity bill|Utilities|₹-1200.00
2024-04-12|Bookstore|Education|₹-600.00
"""

    result = run_statement_analyzer(example_statement, income=15000)
    print("SUMMARY:")
    print(result['message'])
    print(f"Total spent: ₹{result['summary']['total_spent']}")
    print(f"Top category: {result['summary']['top_categories'][0]['category']} = ₹{result['summary']['top_categories'][0]['amount']}")
    print("RECOMMENDATIONS:")
    for rec in result['recommendations']:
        print(f"- {rec}")
