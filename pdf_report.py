# pdf_report.py
import logging
import os
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.flowables import HRFlowable
from analyzer import get_saving_tip

logger = logging.getLogger(__name__)

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
    Generates a complete PDF financial report using ReportLab.
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

    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=72)

    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.darkgreen,
        alignment=1,  # Center
        spaceAfter=30
    )

    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.black,
        spaceAfter=10,
        borderColor=colors.darkgreen,
        borderWidth=1,
        borderPadding=5
    )

    normal_style = styles['Normal']
    bold_style = styles['Heading4']

    # Build the story (content flow)
    story = []

    # Title
    story.append(Paragraph("Youth Financial Guardian", title_style))
    story.append(Paragraph(texts["title"], styles['Heading2']))
    story.append(Spacer(1, 12))

    # Profile Section
    story.append(HRFlowable(width="100%", thickness=1, color=colors.darkgreen))
    story.append(Paragraph(texts["profile"], section_style))

    profile_data = [
        ["Name:", str(name)],
        ["Age:", f"{age} years"],
        ["Monthly Income:", f"Rs.{income:,.0f}"],
    ]

    profile_table = Table(profile_data, colWidths=[2*inch, 4*inch])
    profile_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(profile_table)
    story.append(Spacer(1, 12))

    # Financial Health Section
    story.append(Paragraph(texts["health_score"], section_style))

    health_data = [
        [texts["status"] + ":", crisis.get('level', 'Unknown')],
        ["Total Income:", f"Rs.{result['total_income']:,.0f}"],
        ["Total Expenses:", f"Rs.{result['total_expenses']:,.0f}"],
        ["Monthly Savings:", f"Rs.{result['savings']:,.0f}"],
        ["Savings Rate:", f"{result['savings_rate']}%"],
        ["Financial Health:", result['financial_health']],
    ]

    health_table = Table(health_data, colWidths=[2*inch, 4*inch])
    health_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(health_table)

    # Crisis alerts
    if crisis.get("alerts"):
        story.append(Spacer(1, 6))
        for alert in crisis["alerts"]:
            story.append(Paragraph(f"• {alert}", normal_style))

    story.append(Spacer(1, 12))

    # Expense Breakdown Section
    story.append(Paragraph(texts["path_summary"], section_style))

    if expenses:
        expense_data = [["Category", "Amount", "Percentage"]]
        total_expenses = result["total_expenses"]
        for category, amount in expenses.items():
            percentage = round((amount / total_expenses) * 100, 1) if total_expenses > 0 else 0
            expense_data.append([category, f"Rs.{amount:,.0f}", f"{percentage}%"])

        expense_table = Table(expense_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
        expense_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(expense_table)
    else:
        story.append(Paragraph("No expenses recorded.", normal_style))

    story.append(Spacer(1, 12))

    # Charts Section (if provided)
    if chart_paths is not None:
        story.append(Paragraph(texts["charts"], section_style))
        if chart_paths:
            for chart_path in chart_paths:
                if os.path.exists(chart_path):
                    from reportlab.platypus import Image
                    img = Image(chart_path, width=6*inch, height=4*inch)
                    story.append(img)
                    story.append(Spacer(1, 12))
        else:
            story.append(Paragraph("No charts available.", styles['Italic']))
        story.append(Spacer(1, 12))

    # Government Schemes Section
    story.append(Paragraph(texts["schemes"], section_style))

    if schemes:
        for scheme in schemes:
            story.append(Paragraph(f"<b>{scheme['name']}</b>", bold_style))
            story.append(Paragraph(f"Benefit: {scheme['benefit']}", normal_style))
            story.append(Spacer(1, 6))
    else:
        story.append(Paragraph("No schemes matched your profile.", normal_style))

    story.append(Spacer(1, 12))

    # Action Plan Section
    story.append(Paragraph(texts["action_plan"], section_style))

    if action_plan:
        for step in action_plan:
            story.append(Paragraph(f"<b>{step['title']}</b>", bold_style))
            story.append(Paragraph(step['description'], normal_style))
            story.append(Spacer(1, 6))
    else:
        story.append(Paragraph("No action steps available.", normal_style))

    story.append(Spacer(1, 12))

    # Personalized Tip
    tip = get_saving_tip(result["savings_rate"])
    story.append(Paragraph(f"<i>Tip: {tip}</i>", styles['Italic']))

    # Footer
    story.append(Spacer(1, 24))
    footer_text = f"{texts['generated']} {datetime.now().strftime('%d %B %Y')} | Made with love for young India"
    story.append(Paragraph(footer_text, styles['Italic']))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


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