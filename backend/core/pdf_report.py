from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from xml.sax.saxutils import escape


NAVY = colors.HexColor("#101827")
SLATE = colors.HexColor("#1B2939")
CYAN = colors.HexColor("#7DD3FC")
PURPLE = colors.HexColor("#818CF8")
MUTED = colors.HexColor("#64748B")
PALE = colors.HexColor("#F1F5F9")
BORDER = colors.HexColor("#CBD5E1")
GREEN = colors.HexColor("#15803D")
AMBER = colors.HexColor("#B45309")
RED = colors.HexColor("#B91C1C")


def _safe(value: Any) -> str:
    if value is None:
        return "Not available"
    if isinstance(value, (dict, list, tuple)):
        return escape(str(value))
    return escape(str(value)).replace("\n", "<br/>")


def _value(value: Any) -> str:
    if value is None:
        return "Not available"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def _add_page_number(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(BORDER)
    canvas.line(18 * mm, 15 * mm, width - 18 * mm, 15 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 10 * mm, "TRUTHGUARD | AI Response Verification Report")
    canvas.drawRightString(width - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def create_analysis_pdf(result: dict) -> bytes:
    """Build a downloadable PDF containing the complete available TruthGuard analysis."""
    result = result if isinstance(result, dict) else {}
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=21 * mm,
        title="TruthGuard Analysis Report",
        author="TruthGuard",
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="TGTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=24, leading=29, textColor=NAVY, alignment=TA_LEFT,
        spaceAfter=5 * mm,
    ))
    styles.add(ParagraphStyle(
        name="TGSub", parent=styles["Normal"], fontSize=9,
        leading=13, textColor=MUTED, spaceAfter=5 * mm,
    ))
    styles.add(ParagraphStyle(
        name="TGSection", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=14, leading=18, textColor=NAVY, spaceBefore=5 * mm,
        spaceAfter=2.5 * mm, keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="TGBody", parent=styles["BodyText"], fontSize=9,
        leading=13, textColor=colors.HexColor("#1F2937"), spaceAfter=2.5 * mm,
        wordWrap="CJK",
    ))
    styles.add(ParagraphStyle(
        name="TGSmall", parent=styles["BodyText"], fontSize=8,
        leading=11, textColor=MUTED, spaceAfter=1.5 * mm,
    ))
    styles.add(ParagraphStyle(
        name="TGClaim", parent=styles["BodyText"], fontName="Helvetica-Bold",
        fontSize=10, leading=14, textColor=NAVY, spaceAfter=2 * mm,
    ))

    story = []
    question = result.get("question", "Not available")
    original = result.get("original_response", "Not available")
    final_response = result.get("final_response") or original
    regeneration = result.get("regeneration") or {}
    final_verification = result.get("final_verification")
    fusion = result.get("fusion") or result.get("overall_scores") or {}
    risk = result.get("risk") or result.get("risk_decision") or {}
    if not isinstance(fusion, dict):
        fusion = {}

    if not isinstance(risk, dict):
        risk = {}
    claims = result.get("claims") or []
    evidence_average = result.get("evidence_average")
    judge_average = result.get("judge_average")

    story.append(Paragraph("TruthGuard", styles["TGTitle"]))
    story.append(Paragraph("AI Response Verification — Complete Analysis Report", styles["Heading2"]))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}<br/>"
        "This report contains the results returned by the current verification pipeline.",
        styles["TGSub"],
    ))

    story.append(Paragraph("1. Question", styles["TGSection"]))
    story.append(Paragraph(_safe(question), styles["TGBody"]))

    story.append(Paragraph("2. TruthGuard Response", styles["TGSection"]))
    story.append(Paragraph(_safe(final_response), styles["TGBody"]))
    if final_verification:
        story.append(Paragraph(
            "A final-verification result was returned by the backend.",
            styles["TGSmall"],
        ))
    else:
        story.append(Paragraph(
            "Note: a separately verified/corrected answer was not returned unless stated by the backend. "
            "This report does not independently guarantee factual accuracy.",
            styles["TGSmall"],
        ))

    story.append(Paragraph("3. Verification Overview", styles["TGSection"]))
    overview = [
        ["Metric", "Result"],
        ["Truth score", _value(fusion.get("truth_score"))],
        ["Confidence score", _value(fusion.get("confidence_score"))],
        ["Hallucination probability", _value(fusion.get("hallucination_probability"))],
        ["Risk level", _value(fusion.get("risk_level", risk.get("risk_level")))],
        ["Risk decision", _value(risk.get("decision"))],
        ["Risk explanation", _value(risk.get("reason"))],
        ["Average evidence score", _value(evidence_average)],
        ["Average judge score", _value(judge_average)],
    ]
    table = Table(overview, colWidths=[54 * mm, 112 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 1), (0, -1), PALE),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#1F2937")),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEADING", (0, 0), (-1, -1), 11),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)

    story.append(Paragraph("4. Claim-by-Claim Review", styles["TGSection"]))
    if not claims:
        story.append(Paragraph("No claim-level results were returned.", styles["TGBody"]))
    else:
        for index, item in enumerate(claims, start=1):
            if not isinstance(item, dict):
                continue
            claim = item.get("claim") or {}
            if not isinstance(claim, dict):
                claim = {"text": str(claim)}
            claim_id = claim.get("id", index)
            claim_text = claim.get("text", item.get("text", "Claim text unavailable"))
            claim_type = claim.get("type", item.get("type", "Not classified"))
            story.append(Paragraph(
                f"Claim {escape(str(claim_id))} — {escape(str(claim_type))}",
                styles["TGClaim"],
            ))
            story.append(Paragraph(_safe(claim_text), styles["TGBody"]))

            for key, title in (("evidence", "Evidence verification"), ("judge", "LLM-as-a-Judge")):
                detail = item.get(key)
                story.append(Paragraph(title, styles["Heading4"]))
                if isinstance(detail, dict):
                    story.append(Paragraph(
                        f"<b>Score:</b> {_safe(detail.get('score'))} &nbsp;&nbsp; "
                        f"<b>Verdict:</b> {_safe(detail.get('verdict'))}",
                        styles["TGBody"],
                    ))
                    if detail.get("explanation"):
                        story.append(Paragraph(
                            f"<b>Explanation:</b> {_safe(detail.get('explanation'))}",
                            styles["TGBody"],
                        ))
                    sources = detail.get("sources") or []
                    if sources:
                        story.append(Paragraph("<b>Sources:</b>", styles["TGSmall"]))
                        for source_index, source in enumerate(sources, start=1):
                            if isinstance(source, dict):
                                title_text = source.get("title") or f"Source {source_index}"
                                url = source.get("url", "")
                                snippet = source.get("snippet", "")
                                link = (
                                    f'<link href="{escape(str(url), quote=True)}" color="#0369A1">'
                                    f'{escape(str(title_text))}</link>'
                                    if url else escape(str(title_text))
                                )
                                source_line = f"{source_index}. {link}"
                                if snippet:
                                    source_line += f"<br/><font color='#64748B'>{_safe(snippet)}</font>"
                                story.append(Paragraph(source_line, styles["TGSmall"]))
                            else:
                                story.append(Paragraph(_safe(source), styles["TGSmall"]))
                elif detail is None:
                    story.append(Paragraph("No result returned for this stage.", styles["TGSmall"]))
                else:
                    story.append(Paragraph(_safe(detail), styles["TGBody"]))

            if item.get("whitebox") is not None:
                story.append(Paragraph("White-box uncertainty", styles["Heading4"]))
                story.append(Paragraph(_safe(item["whitebox"]), styles["TGBody"]))
            if item.get("fusion") is not None:
                story.append(Paragraph("Claim score fusion", styles["Heading4"]))
                story.append(Paragraph(_safe(item["fusion"]), styles["TGBody"]))
            story.append(Spacer(1, 2 * mm))

    story.append(Paragraph("5. Score Fusion Details", styles["TGSection"]))
    if fusion.get("component_scores") is not None:
        story.append(Paragraph(
            f"<b>Component scores:</b> {_safe(fusion.get('component_scores'))}",
            styles["TGBody"],
        ))
    if fusion.get("weights") is not None:
        story.append(Paragraph(
            f"<b>Fusion weights:</b> {_safe(fusion.get('weights'))}",
            styles["TGBody"],
        ))
    if fusion.get("component_scores") is None and fusion.get("weights") is None:
        story.append(Paragraph("No component-score breakdown or fusion weights were returned.", styles["TGBody"]))

    story.append(Paragraph("6. Original vs. Final Response", styles["TGSection"]))
    story.append(Paragraph("<b>Original response</b>", styles["TGBody"]))
    story.append(Paragraph(_safe(original), styles["TGBody"]))
    story.append(Paragraph("<b>Final available response</b>", styles["TGBody"]))
    story.append(Paragraph(_safe(final_response), styles["TGBody"]))
    if isinstance(regeneration, dict) and regeneration.get("regenerated_response"):
        story.append(Paragraph("<b>Regenerated response</b>", styles["TGBody"]))
        story.append(Paragraph(_safe(regeneration["regenerated_response"]), styles["TGBody"]))

    if final_verification:
        story.append(Paragraph("7. Final Response Verification", styles["TGSection"]))
        story.append(Paragraph(_safe(final_verification), styles["TGBody"]))

    components = result.get("component_results")
    if components:
        story.append(Paragraph("8. Additional Component Results", styles["TGSection"]))
        story.append(Paragraph(_safe(components), styles["TGBody"]))

    errors = result.get("errors") or []
    if errors:
        story.append(Paragraph("Warnings / Errors", styles["TGSection"]))
        for err in errors:
            story.append(Paragraph(f"• {_safe(err)}", styles["TGBody"]))

    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph(
        "Interpretation note: TruthGuard scores and model judgments are estimates based on the "
        "evidence and model outputs available at runtime. Review source material for important decisions.",
        styles["TGSmall"],
    ))

    doc.build(story, onFirstPage=_add_page_number, onLaterPages=_add_page_number)
    return buffer.getvalue()
