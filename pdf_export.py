from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


def generate_pdf(
        filename,
        selected_user,
        summary,
        personality,
        sentiment,
        starter_df=None,
        response_df=None
):

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph("<b><font size=22>ChatPulse Analysis Report</font></b>",
                  styles["Title"])
    )

    elements.append(Spacer(1, 0.3 * inch))

    elements.append(
        Paragraph(f"<b>User:</b> {selected_user}", styles["Heading2"])
    )

    elements.append(Spacer(1, 0.2 * inch))

    # ---------------- Summary ----------------

    elements.append(
        Paragraph("<b>Summary Statistics</b>", styles["Heading2"])
    )

    table = Table([
        ["Metric", "Value"],
        ["Messages", summary[0]],
        ["Words", summary[1]],
        ["Media", summary[2]],
        ["Links", summary[3]]
    ])

    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    ]))

    elements.append(table)

    elements.append(Spacer(1, 0.3 * inch))

    # ---------------- Personality ----------------

    elements.append(
        Paragraph("<b>Personality Analysis</b>",
                  styles["Heading2"])
    )

    for trait in personality:
        elements.append(
            Paragraph("• " + trait, styles["Normal"])
        )

    elements.append(Spacer(1, 0.3 * inch))

    # ---------------- Sentiment ----------------

    elements.append(
        Paragraph("<b>Sentiment Analysis</b>",
                  styles["Heading2"])
    )

    elements.append(
        Paragraph(
            f"Positive : {sentiment['positive']}%",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Neutral : {sentiment['neutral']}%",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Negative : {sentiment['negative']}%",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 0.3 * inch))

    # ---------------- Overall Only ----------------

    if starter_df is not None:

        elements.append(
            Paragraph("<b>Conversation Starters</b>",
                      styles["Heading2"])
        )

        for _, row in starter_df.iterrows():

            elements.append(
                Paragraph(
                    f"{row['User']} : {row['Conversations Started']}",
                    styles["Normal"]
                )
            )

    if response_df is not None:

        elements.append(Spacer(1, 0.3 * inch))

        elements.append(
            Paragraph("<b>Response Time Leaderboard</b>",
                      styles["Heading2"])
        )

        for _, row in response_df.iterrows():

            elements.append(
                Paragraph(
                    f"{row['User']} : {row['Average Response Time (mins)']} mins",
                    styles["Normal"]
                )
            )

    doc.build(elements)

    return filename