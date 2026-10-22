import sys
from pathlib import Path
from html import escape

import streamlit as st

# Keep imports working when launched from the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.core.pipeline_ui import run_truthguard


# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="TruthGuard | AI Trust & Verification",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# STYLING — hero from screenshot 1, answer/results from screenshot 2
# ============================================================
st.markdown(
    """
    <style>
    :root {
        --bg: #080a10;
        --panel: #111827;
        --panel-2: #1b2939;
        --border: #303047;
        --text: #f4f5fb;
        --muted: #9aa6bd;
        --purple: #a78bfa;
        --blue: #60a5fa;
        --cyan: #67e8f9;
        --green: #22c55e;
        --amber: #fbbf24;
        --red: #f87171;
    }

    html, body, [class*="css"] {
        font-family: Inter, ui-sans-serif, system-ui, -apple-system,
                     BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(ellipse at 8% 0%, rgba(124, 58, 237, .16), transparent 32%),
            radial-gradient(ellipse at 95% 4%, rgba(6, 182, 212, .13), transparent 30%),
            var(--bg);
        color: var(--text);
    }

    [data-testid="stHeader"] { background: transparent; }
    #MainMenu, footer { visibility: hidden; }

    .block-container {
        max-width: 1240px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 14px;
        margin: 0 0 26px 0;
        padding: 2px 0;
    }

    .brand-icon {
        width: 58px;
        height: 58px;
        min-width: 58px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 18px;
        background: linear-gradient(135deg, #8b5cf6, #06b6d4);
        color: white;
        font-size: 28px;
        box-shadow: 0 8px 28px rgba(99, 102, 241, .2);
    }

    .brand-title {
        color: #f8fafc;
        font-size: 30px;
        line-height: 1.2;
        font-weight: 780;
        letter-spacing: -.6px;
    }

    .brand-subtitle {
        color: var(--muted);
        font-size: 14px;
        margin-top: 5px;
    }

    .hero {
        background: linear-gradient(115deg, rgba(24, 22, 43, .98), rgba(17, 27, 42, .97));
        border: 1px solid #39334f;
        border-radius: 30px;
        padding: 38px 42px 36px;
        margin-bottom: 24px;
        box-shadow: 0 22px 70px rgba(0, 0, 0, .16);
    }

    .hero-tag {
        display: inline-block;
        padding: 9px 14px;
        border: 1px solid #55417f;
        border-radius: 999px;
        background: rgba(109, 40, 217, .12);
        color: #d4c5ff;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1px;
        margin-bottom: 22px;
    }

    .hero-heading {
        color: #f7f7ff;
        font-size: clamp(34px, 4vw, 58px);
        font-weight: 820;
        line-height: 1.13;
        letter-spacing: -1.5px;
        margin: 0 0 20px 0;
    }

    .hero-gradient {
        background: linear-gradient(90deg, #c4b5fd 0%, #93c5fd 47%, #67e8f9 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }

    .hero-copy {
        color: #a8b1c7;
        font-size: 16px;
        line-height: 1.8;
        max-width: 940px;
    }

    .section-kicker {
        color: #94a3b8;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: .25px;
        margin-bottom: 13px;
    }

    .question-panel {
        background: rgba(5, 5, 8, .82);
        border: 1px solid #303030;
        border-radius: 15px;
        padding: 18px;
        margin: 0 0 16px 0;
    }

    div[data-testid="stTextArea"] textarea {
        background: #111827 !important;
        color: #f1f5f9 !important;
        border: 1px solid #29364b !important;
        border-radius: 13px !important;
        font-size: 15px !important;
        min-height: 110px;
    }

    div[data-testid="stTextArea"] textarea:focus {
        border-color: #6478a5 !important;
        box-shadow: 0 0 0 1px #6478a5 !important;
    }

    .stFormSubmitButton > button {
        min-height: 48px;
        border-radius: 12px;
        border: 1px solid #52688a;
        background: linear-gradient(90deg, #263d5a, #1d3550);
        color: #f8fafc;
        font-size: 14px;
        font-weight: 750;
    }

    .stFormSubmitButton > button:hover {
        border-color: #67e8f9;
        color: #67e8f9;
    }

    .answer-panel {
        background: #101827;
        border: 1px solid #293b53;
        border-radius: 20px;
        padding: 27px 26px 24px;
        margin: 16px 0 18px;
    }

    .answer-heading {
        color: #f1f5f9;
        font-size: 20px;
        font-weight: 800;
        margin: 0 0 16px 0;
    }

    .answer-text {
        color: #e2e8f0;
        font-size: 15px;
        line-height: 1.8;
    }

    .score-card {
        background: #1b2939;
        border-radius: 16px;
        padding: 15px;
        min-height: 84px;
        margin-bottom: 4px;
    }

    .score-label {
        color: #9aa8bb;
        font-size: 12px;
        margin-bottom: 12px;
    }

    .score-value {
        color: #7dd3fc;
        font-size: 25px;
        line-height: 1.15;
        font-weight: 800;
    }

    .score-value.risk { color: #fbbf24; }

    .fine-print {
        color: #94a3b8;
        font-size: 12px;
        line-height: 1.55;
        margin-top: 12px;
    }

    .section-title {
        color: #f1f5f9;
        font-size: 23px;
        font-weight: 780;
        margin: 28px 0 4px;
    }

    .section-subtitle {
        color: #94a3b8;
        font-size: 13px;
        margin-bottom: 16px;
    }

    .feature-card {
        background: rgba(0, 0, 0, .65);
        border: 1px solid #292929;
        border-radius: 16px;
        padding: 17px;
        min-height: 140px;
        margin-bottom: 12px;
    }

    .feature-icon {
        font-size: 24px;
        margin-bottom: 11px;
        line-height: 1;
    }

    .feature-icon.cyan { color: #14b8a6; }
    .feature-icon.purple { color: #818cf8; }

    .feature-title {
        color: #f1f5f9;
        font-size: 16px;
        font-weight: 780;
        margin-bottom: 7px;
    }

    .feature-copy {
        color: #d1d5db;
        font-size: 13px;
        line-height: 1.6;
    }

    .status {
        display: inline-block;
        padding: 6px 11px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 800;
        margin: 0 0 15px;
    }

    .status.good { color: #4ade80; background: #052e20; border: 1px solid #166534; }
    .status.warn { color: #fbbf24; background: #422006; border: 1px solid #854d0e; }
    .status.bad { color: #fca5a5; background: #450a0a; border: 1px solid #7f1d1d; }
    .status.neutral { color: #cbd5e1; background: #1e293b; border: 1px solid #334155; }

    div[data-testid="stExpander"] {
        background: #0b0d12;
        border: 1px solid #292f3d;
        border-radius: 13px;
        margin-bottom: 9px;
    }

    div[data-testid="stMetric"] {
        background: #1b2939;
        border: 1px solid #29374a;
        border-radius: 13px;
        padding: 13px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 7px;
        background: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background: #111827;
        border: 1px solid #29374a;
        border-radius: 10px;
        color: #aab4c5;
        padding: 9px 13px;
    }

    .stTabs [aria-selected="true"] {
        color: #e0e7ff !important;
        border-color: #6366f1 !important;
    }

    a { color: #7dd3fc !important; }

    .footer {
        color: #64748b;
        text-align: center;
        font-size: 11px;
        margin-top: 42px;
        padding-top: 20px;
        border-top: 1px solid #242938;
    }

    @media (max-width: 700px) {
        .hero { padding: 26px 22px; border-radius: 22px; }
        .hero-heading { letter-spacing: -.7px; }
        .brand-title { font-size: 25px; }
        .answer-panel { padding: 21px 17px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================
def as_dict(value):
    return value if isinstance(value, dict) else {}


def display_value(value, digits=2):
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def status_for_decision(decision):
    decision = str(decision or "UNKNOWN").upper()
    if decision in {"ACCEPT", "APPROVE", "SUPPORTED"}:
        return "good", "✓ RESPONSE ACCEPTED"
    if decision in {"REVIEW", "CAUTION", "PARTIALLY_SUPPORTED"}:
        return "warn", "⚠ REVIEW RECOMMENDED"
    if decision in {"REGENERATE", "REJECT", "HIGH_RISK", "HIGH RISK"}:
        return "bad", "⚠ RESPONSE NEEDS ATTENTION"
    return "neutral", "ASSESSMENT AVAILABLE"


def render_sources(data):
    data = as_dict(data)
    sources = data.get("sources") or []
    if not sources:
        return
    st.markdown("**Evidence sources**")
    for i, source in enumerate(sources, start=1):
        if isinstance(source, dict):
            title = source.get("title") or f"Source {i}"
            url = source.get("url")
            if url:
                st.markdown(f"- [{title}]({url})")
            else:
                st.write(f"- {title}")
        else:
            st.write(f"- {source}")


def render_verification(title, data):
    data = as_dict(data)
    st.markdown(f"#### {title}")
    if not data:
        st.caption("No result was returned for this stage.")
        return
    left, right = st.columns(2)
    with left:
        st.write("**Score**")
        st.write(display_value(data.get("score")))
    with right:
        st.write("**Verdict**")
        st.write(str(data.get("verdict", "Not available")).replace("_", " ").title())
    if data.get("explanation"):
        st.write("**Explanation**")
        st.write(data["explanation"])
    render_sources(data)


def score_card(label, value, risk=False):
    cls = "score-value risk" if risk else "score-value"
    st.markdown(
        f'<div class="score-card"><div class="score-label">{escape(label)}</div>'
        f'<div class="{cls}">{escape(display_value(value))}</div></div>',
        unsafe_allow_html=True,
    )


# ============================================================
# HEADER + HERO — FIRST SCREENSHOT
# ============================================================
st.markdown(
    """
    <div class="brand">
        <div class="brand-icon">🛡</div>
        <div>
            <div class="brand-title">TruthGuard</div>
            <div class="brand-subtitle">AI Trust &amp; Verification Engine</div>
        </div>
    </div>

    <div class="hero">
        <div class="hero-tag">LLM RELIABILITY • EVIDENCE • RISK ANALYSIS</div>
        <div class="hero-heading">
            Don’t just get an answer.<br>
            <span class="hero-gradient">Know how much to trust it.</span>
        </div>
        <div class="hero-copy">
            TruthGuard evaluates AI-generated answers using claim analysis, evidence checks,
            model judging and risk scoring.<br>
            Get the response first, then explore the reasoning behind the assessment.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# QUESTION INPUT
# ============================================================
# st.markdown('<div class="question-panel">', unsafe_allow_html=True)
with st.form("truthguard_question_form", clear_on_submit=False):
    st.markdown('<div class="section-kicker">ASK TRUTHGUARD</div>', unsafe_allow_html=True)
    question = st.text_area(
        "Question",
        placeholder="Ask a question you want to verify...",
        height=110,
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button(
        "Verify response",
        type="primary",
        use_container_width=True,
    )
st.markdown("</div>", unsafe_allow_html=True)

if submitted:
    if not question.strip():
        st.warning("Please enter a question first.")
    else:
        try:
            with st.spinner("TruthGuard is generating the answer and checking its claims..."):
                st.session_state["truthguard_result"] = run_truthguard(question.strip())
                st.session_state["truthguard_question"] = question.strip()
        except Exception as exc:
            st.error("TruthGuard could not complete the verification pipeline.")
            st.exception(exc)


# ============================================================
# RESULT — ANSWER FIRST, THEN COMPLETE ANALYSIS
# Expected result keys align with backend/core/pipeline_ui.py:
# question, original_response, claims, evidence_average, judge_average,
# fusion, risk, and optional final_response / final_verification.
# ============================================================
result = st.session_state.get("truthguard_result")

if result:
    result = as_dict(result)
    original_response = result.get("original_response") or ""
    regeneration = as_dict(result.get("regeneration"))
    final_verification = as_dict(result.get("final_verification"))

    # Prefer a backend-produced final/regenerated answer if one exists.
    final_response = (
        result.get("final_response")
        or regeneration.get("regenerated_response")
        or original_response
    )

    fusion = as_dict(result.get("fusion") or result.get("overall_scores"))
    risk = as_dict(result.get("risk") or result.get("risk_decision"))
    claims = result.get("claims") or []
    question_text = result.get("question") or st.session_state.get("truthguard_question", "")

    decision = risk.get("decision", "UNKNOWN")
    status_class, status_text = status_for_decision(decision)

    if final_verification:
        answer_note = "A final verification result is available below in the analysis."
    elif regeneration.get("regenerated_response"):
        answer_note = "This is the regenerated response returned by the backend."
    else:
        answer_note = (
            "This is the response returned by the current pipeline. "
            "Review the evidence and risk assessment below before relying on it."
        )

    # Main answer panel appears before every analysis section.
    st.markdown(
        f"""
        <div class="answer-panel">
            <div class="section-kicker">YOUR VERIFIED ANSWER</div>
            <div class="status {status_class}">{status_text}</div>
            <div class="answer-heading">TruthGuard response</div>
            <div class="fine-print">{escape(answer_note)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(final_response or "No response was returned by the backend.")

    if question_text:
        with st.expander("View question", expanded=False):
            st.write(question_text)

    if final_response:
        st.download_button(
            "Download answer",
            data=str(final_response),
            file_name="truthguard_answer.txt",
            mime="text/plain",
        )

    # Score cards immediately after the answer, matching screenshot 2.
    st.markdown('<div class="section-kicker" style="margin-top:24px;">VERIFICATION OVERVIEW</div>',
                unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        score_card("Truth score", fusion.get("truth_score"))
    with col2:
        score_card("Confidence", fusion.get("confidence_score"))
    with col3:
        score_card("Risk level", fusion.get("risk_level", risk.get("risk_level")), risk=True)

    st.markdown(
        '<div class="fine-print">Scores reflect the values returned by your backend. '
        'They are estimates, not a guarantee that every statement is correct.</div>',
        unsafe_allow_html=True,
    )

    # Feature cards — same wording as the desired reference design.
    st.markdown('<div class="section-title">Complete analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Explore the evidence and reasoning behind the assessment.</div>',
                unsafe_allow_html=True)

    f1, f2 = st.columns(2)
    with f1:
        st.markdown(
            '<div class="feature-card"><div class="feature-icon cyan">⌕</div>'
            '<div class="feature-title">Evidence &amp; sources</div>'
            '<div class="feature-copy">Show supporting evidence and clickable source links for each claim.</div></div>',
            unsafe_allow_html=True,
        )
    with f2:
        st.markdown(
            '<div class="feature-card"><div class="feature-icon purple">⑂</div>'
            '<div class="feature-title">Verification pipeline</div>'
            '<div class="feature-copy">Show the stages completed, with scores and explanations.</div></div>',
            unsafe_allow_html=True,
        )
    f3, f4 = st.columns(2)
    with f3:
        st.markdown(
            '<div class="feature-card"><div class="feature-icon cyan">☷</div>'
            '<div class="feature-title">Claim-by-claim review</div>'
            '<div class="feature-copy">Expand each claim to inspect its verdict, evidence and judge reasoning.</div></div>',
            unsafe_allow_html=True,
        )
    with f4:
        st.markdown(
            '<div class="feature-card"><div class="feature-icon purple">▤</div>'
            '<div class="feature-title">Original vs. verified</div>'
            '<div class="feature-copy">Keep the original AI response available for comparison below the verified answer.</div></div>',
            unsafe_allow_html=True,
        )

    tab_claims, tab_evidence, tab_scores, tab_pipeline, tab_compare = st.tabs(
        ["Claim-by-claim review", "Evidence & sources", "Score analysis",
         "Verification pipeline", "Original vs. verified"]
    )

    with tab_claims:
        st.subheader("Claim-by-claim review")
        if claims:
            for index, item in enumerate(claims, start=1):
                item = as_dict(item)
                claim_obj = as_dict(item.get("claim"))
                claim_id = claim_obj.get("id", item.get("id", index))
                claim_text = claim_obj.get("text", item.get("text", "Claim text unavailable"))
                claim_type = claim_obj.get("type", item.get("type", "Not classified"))
                with st.expander(
                    f"Claim {claim_id} · {str(claim_type).replace('_', ' ').title()}",
                    expanded=(index == 1),
                ):
                    st.write(claim_text)
                    render_verification("Evidence verification", item.get("evidence"))
                    render_verification("LLM-as-a-Judge", item.get("judge"))
                    if item.get("whitebox") is not None:
                        st.markdown("#### White-box uncertainty")
                        st.json(item["whitebox"])
                    if item.get("fusion") is not None:
                        st.markdown("#### Claim score fusion")
                        st.json(item["fusion"])
        else:
            st.info("No claim-level results were returned by the current backend.")

    with tab_evidence:
        st.subheader("Evidence & sources")
        found_evidence = False
        components = as_dict(result.get("component_results"))
        for name, value in components.items():
            if isinstance(value, dict) and any(
                key in name.lower() for key in ("evidence", "judge", "blackbox")
            ):
                found_evidence = True
                with st.expander(name.replace("_", " ").title(), expanded=True):
                    render_verification(name.replace("_", " ").title(), value)

        for index, item in enumerate(claims, start=1):
            item = as_dict(item)
            claim_obj = as_dict(item.get("claim"))
            claim_id = claim_obj.get("id", item.get("id", index))
            if item.get("evidence") or item.get("judge"):
                found_evidence = True
                with st.expander(f"Claim {claim_id} — evidence and judge"):
                    render_verification("Evidence verification", item.get("evidence"))
                    render_verification("LLM-as-a-Judge", item.get("judge"))

        if final_verification:
            found_evidence = True
            render_verification("Final response verification", final_verification)
        if not found_evidence:
            st.info("No detailed evidence objects were returned by the current wrapper.")

    with tab_scores:
        st.subheader("Score analysis")
        metric_cols = st.columns(4)
        score_items = [
            ("Truth score", fusion.get("truth_score")),
            ("Confidence", fusion.get("confidence_score")),
            ("Hallucination probability", fusion.get("hallucination_probability")),
            ("Risk level", fusion.get("risk_level", risk.get("risk_level"))),
        ]
        for col, (label, value) in zip(metric_cols, score_items):
            with col:
                st.metric(label, display_value(value))

        averages = [
            ("Average evidence score", result.get("evidence_average")),
            ("Average judge score", result.get("judge_average")),
        ]
        avg_cols = st.columns(2)
        for col, (label, value) in zip(avg_cols, averages):
            with col:
                st.metric(label, display_value(value))

        left, right = st.columns(2)
        with left:
            st.markdown("#### Component scores")
            if fusion.get("component_scores") is not None:
                st.json(fusion["component_scores"])
            else:
                st.info("No component score breakdown was returned.")
        with right:
            st.markdown("#### Fusion weights")
            if fusion.get("weights") is not None:
                st.json(fusion["weights"])
            else:
                st.info("No fusion weights were returned.")

    with tab_pipeline:
        st.subheader("Verification pipeline")
        stages = [
            ("Response generation", original_response),
            ("Claim extraction", claims),
            ("Evidence verification", any(as_dict(c).get("evidence") for c in claims)),
            ("LLM-as-a-Judge", any(as_dict(c).get("judge") for c in claims)),
            ("Score fusion", fusion),
            ("Risk decision", risk),
        ]
        for stage, output in stages:
            stage_col, state_col = st.columns([4, 1])
            with stage_col:
                st.write(stage)
            with state_col:
                st.write("Available" if output else "Not returned")

        st.markdown("#### Final risk decision")
        if risk:
            st.write("**Decision:**", risk.get("decision", "Not available"))
            st.write("**Risk level:**", risk.get("risk_level", fusion.get("risk_level", "Not available")))
            st.write("**Reason:**", risk.get("reason", "No explanation was returned."))
        else:
            st.info("No risk decision was returned.")

        errors = result.get("errors") or []
        if errors:
            with st.expander(f"Warnings ({len(errors)})"):
                for error in errors:
                    st.warning(str(error))

        with st.expander("Raw backend result (debug)"):
            st.json(result)

    with tab_compare:
        st.subheader("Original vs. verified")
        left, right = st.columns(2)
        with left:
            st.markdown("#### Original AI response")
            st.write(original_response or "No original response was returned.")
        with right:
            st.markdown("#### Final available response")
            st.write(final_response or "No final response was returned.")

        if regeneration:
            st.markdown("#### Regeneration details")
            st.write(regeneration.get("regenerated_response", "No regenerated response returned."))
        if final_verification:
            st.markdown("#### Final verification")
            render_verification("Final response check", final_verification)

    st.markdown(
        '<div class="footer">TRUTHGUARD · AI TRUST &amp; VERIFICATION ENGINE'
        '<br><br>Review evidence for important decisions. Verification scores are estimates.</div>',
        unsafe_allow_html=True,
    )

else:
    # Empty state mirrors the result card from screenshot 2 before first query.
    st.markdown(
        """
        <div class="answer-panel">
            <div class="section-kicker">YOUR VERIFIED ANSWER</div>
            <div class="answer-heading">The final answer appears here first.</div>
            <div class="answer-text">
                After you submit a question, TruthGuard will show the available final
                response first, followed by the complete verification analysis.
            </div>
            <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:18px;">
                <div class="score-card"><div class="score-label">Truth score</div><div class="score-value">—</div></div>
                <div class="score-card"><div class="score-label">Confidence</div><div class="score-value">—</div></div>
                <div class="score-card"><div class="score-label">Risk level</div><div class="score-value risk">—</div></div>
            </div>
            <div class="fine-print">Scores will appear here after the backend completes verification.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    f1, f2 = st.columns(2)
    with f1:
        st.markdown(
            '<div class="feature-card"><div class="feature-icon cyan">⌕</div>'
            '<div class="feature-title">Evidence &amp; sources</div>'
            '<div class="feature-copy">Show supporting evidence and clickable source links for each claim.</div></div>',
            unsafe_allow_html=True,
        )
    with f2:
        st.markdown(
            '<div class="feature-card"><div class="feature-icon purple">⑂</div>'
            '<div class="feature-title">Verification pipeline</div>'
            '<div class="feature-copy">Show the stages completed, with scores and explanations.</div></div>',
            unsafe_allow_html=True,
        )
    f3, f4 = st.columns(2)
    with f3:
        st.markdown(
            '<div class="feature-card"><div class="feature-icon cyan">☷</div>'
            '<div class="feature-title">Claim-by-claim review</div>'
            '<div class="feature-copy">Expand each claim to inspect its verdict, evidence and judge reasoning.</div></div>',
            unsafe_allow_html=True,
        )
    with f4:
        st.markdown(
            '<div class="feature-card"><div class="feature-icon purple">▤</div>'
            '<div class="feature-title">Original vs. verified</div>'
            '<div class="feature-copy">Keep the original AI response available for comparison below the verified answer.</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="footer">TRUTHGUARD · AI TRUST &amp; VERIFICATION ENGINE</div>',
        unsafe_allow_html=True,
    )
