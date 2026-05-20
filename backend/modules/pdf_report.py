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

logger = logging.getLogger(__name__)

def draw_footer(canvas, doc):
    canvas.saveState()
    footer_text = "iCall Helpline: 9152987821 | AASRA: 9820466726 | You are not alone."
    canvas.setFont('Helvetica-Oblique', 10)
    canvas.setFillColor(colors.red)
    canvas.drawCentredString(letter[0] / 2.0, 0.5 * inch, footer_text)
    
    generated_text = f"Generated on {datetime.now().strftime('%d %B %Y')} | Youth Financial Guardian"
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.gray)
    canvas.drawCentredString(letter[0] / 2.0, 0.3 * inch, generated_text)
    canvas.restoreState()

def generate_report(data: dict) -> bytes:
    """
    Generates a complete PDF financial report using ReportLab.
    Returns PDF as bytes.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=72, leftMargin=72,
        topMargin=72, bottomMargin=72
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.darkgreen,
        alignment=1,
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
    
    warning_style = ParagraphStyle(
        'WarningStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.red,
        spaceAfter=6
    )

    normal_style = styles['Normal']
    bold_style = styles['Heading4']

    story = []

    # Title
    story.append(Paragraph("Youth Financial Guardian", title_style))
    story.append(Paragraph("Your Personal Financial Report", styles['Heading2']))
    story.append(Spacer(1, 12))

    # Financial Snapshot
    story.append(HRFlowable(width="100%", thickness=1, color=colors.darkgreen))
    story.append(Paragraph("Financial Snapshot", section_style))

    income = data.get('income', 0)
    expenses = data.get('expenses', 0)
    health_score = data.get('health_score', 'Unknown')
    survival_days = data.get('survival_days', 'N/A')

    snapshot_data = [
        ["Monthly Income:", f"Rs. {income:,.0f}"],
        ["Monthly Expenses:", f"Rs. {expenses:,.0f}"],
        ["Health Score:", str(health_score)],
        ["Survival Days:", str(survival_days)],
    ]
    
    debt_free_date = data.get('debt_free_date')
    if debt_free_date:
        snapshot_data.append(["Debt-Free Date:", str(debt_free_date)])

    snapshot_table = Table(snapshot_data, colWidths=[2*inch, 4*inch])
    snapshot_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(snapshot_table)
    story.append(Spacer(1, 12))

    # Blacklist Warnings
    warnings = data.get('blacklist_warnings', [])
    if warnings:
        story.append(Paragraph("Blacklist & Risk Warnings", section_style))
        for warning in warnings:
            app_name = warning.get('app', 'Unknown App')
            risk = warning.get('risk', 'Unknown Risk')
            action = warning.get('action', 'Stay alert.')
            
            story.append(Paragraph(f"<b>App: {app_name}</b>", warning_style))
            story.append(Paragraph(f"Risk: {risk}", normal_style))
            story.append(Paragraph(f"Action: {action}", normal_style))
            story.append(Spacer(1, 6))
        story.append(Spacer(1, 12))

    # Government Schemes
    schemes = data.get('schemes', [])
    if schemes:
        story.append(Paragraph("You May Qualify For (Govt Schemes)", section_style))
        for scheme in schemes:
            story.append(Paragraph(f"<b>{scheme.get('name', '')}</b>", bold_style))
            story.append(Paragraph(f"Benefit: {scheme.get('benefit', '')}", normal_style))
            if 'apply_link' in scheme:
                story.append(Paragraph(f"Apply: <a href='{scheme['apply_link']}' color='blue'>{scheme['apply_link']}</a>", normal_style))
            story.append(Spacer(1, 6))
        story.append(Spacer(1, 12))

    # Build PDF with footers
    doc.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)
    buffer.seek(0)
    return buffer.getvalue()
