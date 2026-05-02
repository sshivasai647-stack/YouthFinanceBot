# pdf_report.py
import logging
import os
from datetime import datetime

from fpdf import FPDF
from analyzer import get_saving_tip

logger = logging.getLogger(__name__)

# ─── Helpers ─────────────────────────────────────────────────

def _safe_text(text: str) -> str:
    """
    Strips any character Helvetica/latin-1 cannot encode.
    Handles ₹, emoji, Devanagari, and all non-latin characters.
    """
    if not isinstance(text, str):
        text = str(text)
    return text.encode("latin-1", errors="ignore").decode("latin-1").strip()


# ─── Multi-language Headers ───────────────────────────────────
LANG_MAP = {
    "en": {
        "title"       : "Your Personal Financial Report",
        "profile"     : "Your Profile",
        "health_score": "Financial Health Score",
        "path_summary": "Path Summary & Expense Breakdown",
        "action_plan" : "Action Plan & Next Steps",
        "schemes"     : "Government Schemes Eligible For You",
        "charts"      : "Financial Projections",
        "status"      : "Status",
        "generated"   : "Generated on",
    }
}


class FinancialReport(FPDF):

    def header(self):
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(34, 139, 34)
        self.cell(
            0, 15, "Youth Financial Guardian",
            align="C", new_x="LMARGIN", new_y="NEXT",
        )
        self.set_font("Helvetica", "", 11)
        self.set_text_color(100, 100, 100)
        self.cell(
            0, 8,
            getattr(self, "report_title", "Your Personal Financial Report"),
            align="C", new_x="LMARGIN", new_y="NEXT",
        )
        self.ln(3)
        self.set_draw_color(34, 139, 34)
        self.set_line_width(0.8)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        gen_text = getattr(self, "footer_text", "Generated on")
        self.cell(
            0, 10,
            f"{gen_text} {datetime.now().strftime('%d %B %Y')}"
            f" | Made with love for young India",
            align="C",
        )


def generate_report(
    name        : str,
    age         : int,
    income      : float,
    expenses    : dict,
    result      : dict,
    crisis      : dict,
    schemes     : list,
    action_plan : list,
    lang        : str  = "en",
    chart_paths : list = None,
) -> bytes:
    """
    Generates a complete PDF financial report.
    Returns PDF as bytes for Streamlit download.

    Args:
        action_plan : List of dicts with 'title' and 'description' keys.
        chart_paths : None  → chart section hidden entirely
                      []    → section shown, "No charts available" message
                      [..]) → image paths to embed
    """
    texts = LANG_MAP.get(lang, LANG_MAP["en"])
    if lang not in LANG_MAP:
        logger.warning(f"Language '{lang}' not in LANG_MAP — falling back to 'en'")

    pdf = FinancialReport()
    pdf.report_title = texts["title"]
    pdf.footer_text  = texts["generated"]
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── Profile ───────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, texts["profile"], new_x="LMARGIN", new_y="NEXT")
    pdf.set_line_width(0.3)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Name:           {_safe_text(name)}",  new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Age:            {age} years",         new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Monthly Income: Rs.{income:,}",       new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # ── Financial Health ──────────────────────────────────────
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, texts["health_score"], new_x="LMARGIN", new_y="NEXT")
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"{texts['status']}:       {_safe_text(crisis['level'])}",           new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Total Income:   Rs.{result['total_income']:,}",                    new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Total Expenses: Rs.{result['total_expenses']:,}",                  new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Monthly Savings:Rs.{result['savings']:,}",                         new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Savings Rate:   {result['savings_rate']}%",                        new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Financial Health: {_safe_text(result['financial_health'])}",       new_x="LMARGIN", new_y="NEXT")

    for alert in crisis.get("alerts", []):
        pdf.multi_cell(180, 8, f"  - {_safe_text(alert)}")
    pdf.ln(4)

    # ── Expense Breakdown ─────────────────────────────────────
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, texts["path_summary"], new_x="LMARGIN", new_y="NEXT")
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    pdf.set_font("Helvetica", "", 12)
    if expenses:
        for category, amount in expenses.items():
            percentage = (
                round((amount / result["total_expenses"]) * 100, 1)
                if result["total_expenses"] > 0 else 0
            )
            pdf.cell(
                0, 8,
                f"  {_safe_text(category)}: Rs.{amount:,} ({percentage}%)",
                new_x="LMARGIN", new_y="NEXT",
            )
    else:
        pdf.cell(0, 8, "  No expenses recorded.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # ── Charts ────────────────────────────────────────────────
    if chart_paths is not None:
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, texts["charts"], new_x="LMARGIN", new_y="NEXT")
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)
        if chart_paths:
            for chart in chart_paths:
                if os.path.exists(chart):
                    pdf.image(chart, x=10, w=190)
                    pdf.ln(5)
        else:
            pdf.set_font("Helvetica", "I", 11)
            pdf.cell(
                0, 8, "  No charts available.",
                new_x="LMARGIN", new_y="NEXT",
            )
        pdf.ln(4)

    # ── Government Schemes ────────────────────────────────────
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, texts["schemes"], new_x="LMARGIN", new_y="NEXT")
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    if schemes:
        for scheme in schemes:
            pdf.set_font("Helvetica", "B", 12)
            pdf.multi_cell(180, 8, f"  {_safe_text(scheme['name'])}")
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(180, 7, f"    Benefit: {_safe_text(scheme['benefit'])}")
            pdf.ln(2)
    else:
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 8, "  No schemes matched your profile.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # ── Action Plan ───────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, texts["action_plan"], new_x="LMARGIN", new_y="NEXT")
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    if action_plan:
        for step in action_plan:
            pdf.set_font("Helvetica", "B", 12)
            pdf.multi_cell(180, 8, f"  {_safe_text(step['title'])}")
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(180, 7, f"    {_safe_text(step['description'])}")
            pdf.ln(2)
    else:
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 8, "  No action steps available.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # ── Personalised Tip ──────────────────────────────────────
    tip = get_saving_tip(result["savings_rate"])
    pdf.set_font("Helvetica", "I", 12)
    pdf.multi_cell(180, 8, f"Tip: {_safe_text(tip)}")

    return bytes(pdf.output())


# ─── Standalone Test ──────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    test_expenses    = {"Food": 3000, "Transport": 1500, "Entertainment": 500}
    test_result      = {
        "total_income"   : 10000,
        "total_expenses" : 5000,
        "savings"        : 5000,
        "savings_rate"   : 50,
        "financial_health": "Good",
    }
    test_crisis      = {
        "level" : "Low Risk",
        "alerts": ["You are doing great!"],
    }
    test_schemes     = [
        {"name": "PM Mudra Yojana", "benefit": "Loan up to Rs.10 Lakhs"}
    ]
    test_action_plan = [
        {
            "title"      : "Start an Emergency Fund",
            "description": "Save at least 3 months of expenses in a liquid account.",
        },
        {
            "title"      : "Freelancing on Fiverr",
            "description": "Use your skills to earn Rs.5,000-20,000/month extra.",
        },
    ]

    pdf_bytes = generate_report(
        "Shivasai", 20, 10000,
        test_expenses, test_result,
        test_crisis,   test_schemes,
        test_action_plan,
        lang        = "en",
        chart_paths = [],
    )

    with open("test_report.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("✅ test_report.pdf generated successfully")