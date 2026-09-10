import requests
from html import escape
import streamlit as st
from textwrap import dedent
from textwrap import dedent
# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="TruthGuard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
    /* ---------- GLOBAL & HEADER OVERRIDES ---------- */
    [data-testid="stHeader"], footer, #MainMenu {
        visibility: hidden;
        height: 0;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* ---------- BACKGROUND ---------- */
    .stApp {
        background:
            radial-gradient(circle at 15% 10%, rgba(99, 102, 241, 0.08), transparent 28%),
            radial-gradient(circle at 85% 15%, rgba(14, 165, 233, 0.07), transparent 25%),
            #0b0d12;
    }

    /* ---------- HEADER ---------- */
    .brand {
        display: flex;
        align-items: center;
        gap: 13px;
        margin-bottom: 8px;
    }

    .brand-icon {
        width: 46px;
        height: 46px;
        border-radius: 14px;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.25);
    }

    .brand-name {
        font-size: 28px;
        font-weight: 750;
        letter-spacing: -0.7px;
        color: #f8fafc;
    }

    .brand-badge {
        font-size: 11px;
        padding: 4px 9px;
        border-radius: 20px;
        background: rgba(99, 102, 241, 0.12);
        color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.25);
        font-weight: 600;
    }

    .hero {
        margin-top: 2rem;
        margin-bottom: 2rem;
    }

    .hero-title {
        font-size: 42px;
        line-height: 1.15;
        font-weight: 760;
        letter-spacing: -1.5px;
        color: #f8fafc;
        margin-bottom: 12px;
    }

    .hero-title span {
        background: linear-gradient(90deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-description {
        max-width: 720px;
        color: #94a3b8;
        font-size: 16px;
        line-height: 1.7;
    }

    /* ---------- TEXTAREA FIX ---------- */
    .stTextArea textarea {
        background-color: #11141c !important;
        color: #f1f5f9 !important;
        border: 1px solid #303646 !important;
        border-radius: 12px !important;
        font-size: 15px !important;
    }

    .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 1px #6366f1 !important;
    }

    /* ---------- BUTTON ---------- */
    .stButton > button {
        width: 100%;
        height: 48px;
        border-radius: 11px;
        border: none;
        background: linear-gradient(90deg, #6366f1, #7c3aed);
        color: white;
        font-size: 14px;
        font-weight: 700;
        transition: all 0.2s ease;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.18);
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 12px 30px rgba(99, 102, 241, 0.28);
        border: none;
    }

    /* ---------- LABELS & CARDS ---------- */
    .section-title {
        font-size: 18px;
        font-weight: 700;
        color: #f8fafc;
        margin-top: 28px;
        margin-bottom: 14px;
    }

    .section-subtitle {
        color: #64748b;
        font-size: 13px;
        margin-bottom: 18px;
    }

    .answer-card {
        background: #11141c;
        border: 1px solid #252a36;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 20px;
    }

    .answer-label {
        color: #818cf8;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 10px;
    }

    .answer-text {
        color: #e2e8f0;
        font-size: 15px;
        line-height: 1.75;
    }

    .score-card {
        background: #11141c;
        border: 1px solid #252a36;
        border-radius: 15px;
        padding: 19px;
        min-height: 115px;
    }

    .score-name {
        color: #64748b;
        font-size: 12px;
        margin-bottom: 8px;
    }

    .score-value {
        color: #f8fafc;
        font-size: 28px;
        font-weight: 750;
    }

    .score-description {
        color: #64748b;
        font-size: 11px;
        margin-top: 5px;
    }

    .status-safe {
        background: rgba(34, 197, 94, 0.07);
        border: 1px solid rgba(34, 197, 94, 0.20);
        color: #86efac;
        border-radius: 12px;
        padding: 14px 17px;
        font-size: 13px;
        font-weight: 650;
        margin-top: 18px;
    }

    .pipeline {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 10px;
    }

    .pipeline-item {
        background: #151923;
        border: 1px solid #282e3b;
        color: #94a3b8;
        border-radius: 9px;
        padding: 8px 11px;
        font-size: 11px;
    }

    .pipeline-arrow {
        color: #475569;
        font-size: 12px;
    }

    .empty-state {
        border: 1px dashed #303646;
        background: rgba(15, 18, 25, 0.65);
        border-radius: 18px;
        padding: 42px 30px;
        text-align: center;
        margin-top: 15px;
    }

    .empty-icon { font-size: 38px; margin-bottom: 10px; }
    .empty-title { color: #e2e8f0; font-size: 17px; font-weight: 650; }
    .empty-description { color: #64748b; font-size: 13px; margin-top: 6px; }

    .footer {
        text-align: center;
        color: #475569;
        font-size: 11px;
        margin-top: 55px;
        padding-top: 20px;
        border-top: 1px solid #1c2029;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# HEADER & HERO
# ============================================================

st.markdown(
    """
    <div class="brand">
        <div class="brand-icon">🛡️</div>
        <div class="brand-name">TruthGuard</div>
        <div class="brand-badge">AI VERIFICATION</div>
    </div>
    <div class="hero">
        <div class="hero-title">
            Know when your AI answer<br>
            <span>can be trusted.</span>
        </div>
        <div class="hero-description">
            TruthGuard analyzes LLM-generated responses using multiple verification
            techniques to estimate factual reliability and hallucination risk.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# INPUT SECTION
# ============================================================

st.markdown('<p style="font-size:14px; font-weight:650; color:#e2e8f0; margin-bottom:8px;">Ask a question</p>', unsafe_allow_html=True)

question = st.text_area(
    "Question",
    placeholder="Example: Who invented the telephone?",
    height=125,
    label_visibility="collapsed",
)

st.markdown(
    '<p style="font-size:12px; color:#64748b; margin-top:-10px; margin-bottom:15px;">'
    'TruthGuard will analyze the response after generation.</p>',
    unsafe_allow_html=True,
)

verify_clicked = st.button("🔍 Verify Response", type="primary")

# ============================================================
# RESULTS
# ============================================================

if verify_clicked:

    if not question.strip():

        st.warning(
            "Please enter a question before starting verification."
        )

    else:

        API_URL = "http://127.0.0.1:8000/verify"

        st.markdown(
            '<div class="section-title">Analysis</div>',
            unsafe_allow_html=True
        )

        with st.spinner(
            "TruthGuard is analyzing and verifying the response..."
        ):

            try:

                response = requests.post(
                    API_URL,
                    json={
                        "question": question.strip()
                    },
                    timeout=300,
                )

                if response.status_code == 200:

                    result = response.json()

                    # ====================================================
                    # EXTRACT RESULTS
                    # ====================================================

                    query_analysis = result.get(
                        "query_analysis",
                        {}
                    )

                    verification_plan = result.get(
                        "verification_plan",
                        {}
                    )

                    modules_used = result.get(
                        "modules_used",
                        []
                    )

                    scores = result.get(
                        "overall_scores",
                        {}
                    )

                    risk = result.get(
                        "risk_decision",
                        {}
                    )

                    original_response = result.get(
                        "original_response",
                        ""
                    )

                    final_response = result.get(
                        "final_response",
                        original_response
                    )

                    # ====================================================
                    # QUERY ANALYSIS
                    # ====================================================

                    st.markdown(
                        '<div class="section-title">Query Analysis</div>',
                        unsafe_allow_html=True
                    )

                    st.html(dedent(f"""
                        <div class="answer-card">

                            <div class="answer-label">
                                ADAPTIVE ROUTING
                            </div>

                            <div style="
                                display:flex;
                                gap:12px;
                                flex-wrap:wrap;
                                margin-top:10px;
                            ">

                                <div class="pipeline-item">
                                    🧠 Complexity:
                                    <b>{query_analysis.get("level", "N/A")}</b>
                                </div>

                                <div class="pipeline-item">
                                    📂 Domain:
                                    <b>{query_analysis.get("domain", "N/A")}</b>
                                </div>

                            </div>

                            <div style="
                                color:#64748b;
                                font-size:13px;
                                margin-top:14px;
                            ">
                                {escape(query_analysis.get("reason", ""))}
                            </div>

                        </div>
                        """))

                    # ====================================================
                    # VERIFICATION PIPELINE
                    # ====================================================

                    st.markdown(
                        '<div class="section-title">Verification Pipeline</div>',
                        unsafe_allow_html=True
                    )

                    module_labels = {
                        "Initial Response": "🤖 Initial Response",
                        "Quick Evidence Check": "🔎 Quick Evidence",
                        "Claim Extraction": "📋 Claim Extraction",
                        "Evidence Verification": "🔎 Evidence",
                        "Black-Box UQ": "🧠 Black-Box UQ",
                        "Lightweight LLM Judge": "⚖️ LLM Judge",
                        "LLM Judge": "⚖️ LLM Judge",
                        "White-Box UQ": "⚙️ White-Box UQ",
                    }

                    pipeline_html = """
                    <div class="pipeline">
                    """

                    for index, module in enumerate(modules_used):

                        label = module_labels.get(
                            module,
                            module
                        )

                        pipeline_html += f"""
                        <div class="pipeline-item">
                            ✓ {label}
                        </div>
                        """

                        if index < len(modules_used) - 1:

                            pipeline_html += """
                            <div class="pipeline-arrow">→</div>
                            """

                    pipeline_html += "</div>"

                    st.html(pipeline_html)

                    # ====================================================
                    # SHOW SKIPPED MODULES
                    # ====================================================

                    skipped_modules = []

                    if not verification_plan.get(
                        "claim_extraction",
                        False
                    ):
                        skipped_modules.append(
                            "Claim Extraction"
                        )

                    if not verification_plan.get(
                        "blackbox",
                        False
                    ):
                        skipped_modules.append(
                            "Black-Box UQ"
                        )

                    if not verification_plan.get(
                        "whitebox",
                        False
                    ):
                        skipped_modules.append(
                            "White-Box UQ"
                        )

                    if skipped_modules:

                        st.html(dedent(f"""
                            <div style="
                                color:#64748b;
                                font-size:12px;
                                margin-top:10px;
                            ">
                                Skipped for this query:
                                {", ".join(skipped_modules)}
                            </div>
                            """))

                    # ====================================================
                    # INITIAL RESPONSE
                    # ====================================================

                    st.markdown(
                        '<div class="section-title">Initial Response</div>',
                        unsafe_allow_html=True
                    )

                    st.html(dedent(f"""
                        <div class="answer-card">

                            <div class="answer-label">
                                GENERATED RESPONSE
                            </div>

                            <div class="answer-text">
                                {escape(original_response)}
                            </div>

                        </div>
                        """))

                    # ====================================================
                    # CLAIM VERIFICATION
                    # ====================================================

                    claims = result.get(
                        "claims",
                        []
                    )

                    if claims:

                        st.markdown(
                            '<div class="section-title">Claim Verification</div>',
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            '<div class="section-subtitle">'
                            'Each extracted claim is evaluated using the '
                            'selected verification modules.'
                            '</div>',
                            unsafe_allow_html=True
                        )

                        for index, claim_data in enumerate(
                            claims,
                            start=1
                        ):

                            claim = claim_data.get(
                                "claim",
                                {}
                            )

                            evidence = claim_data.get(
                                "evidence",
                                {}
                            )

                            blackbox = claim_data.get(
                                "blackbox",
                                {}
                            )

                            judge = claim_data.get(
                                "judge",
                                {}
                            )

                            whitebox = claim_data.get(
                                "whitebox",
                                {}
                            )

                            fusion = claim_data.get(
                                "fusion",
                                {}
                            )

                            st.html(dedent(f"""
                                <div class="answer-card">

                                    <div class="answer-label">
                                        CLAIM {index}
                                    </div>

                                    <div class="answer-text">
                                        {escape(claim.get("text", ""))}
                                    </div>

                                </div>
                                """))

                            # --------------------------------------------
                            # Component scores
                            # --------------------------------------------

                            score_columns = []

                            if evidence:
                                score_columns.append(
                                    (
                                        "Evidence",
                                        evidence.get(
                                            "score",
                                            "N/A"
                                        )
                                    )
                                )

                            if blackbox:
                                score_columns.append(
                                    (
                                        "Black-Box",
                                        blackbox.get(
                                            "consistency_score",
                                            "N/A"
                                        )
                                    )
                                )

                            if judge:
                                score_columns.append(
                                    (
                                        "Judge",
                                        judge.get(
                                            "score",
                                            "N/A"
                                        )
                                    )
                                )

                            if whitebox:
                                score_columns.append(
                                    (
                                        "White-Box",
                                        whitebox.get(
                                            "whitebox_score",
                                            "N/A"
                                        )
                                    )
                                )

                            if fusion:
                                score_columns.append(
                                    (
                                        "Truth",
                                        fusion.get(
                                            "truth_score",
                                            "N/A"
                                        )
                                    )
                                )

                            if score_columns:

                                cols = st.columns(
                                    len(score_columns)
                                )

                                for col, (
                                    name,
                                    value
                                ) in zip(
                                    cols,
                                    score_columns
                                ):

                                    with col:

                                        st.html(dedent(f"""
                                            <div class="score-card">

                                                <div class="score-name">
                                                    {name.upper()}
                                                </div>

                                                <div class="score-value">
                                                    {value}
                                                </div>

                                            </div>
                                            """))

                            # --------------------------------------------
                            # Evidence details
                            # --------------------------------------------

                            if evidence:

                                verdict = evidence.get(
                                    "verdict",
                                    "N/A"
                                )

                                explanation = evidence.get(
                                    "explanation",
                                    ""
                                )

                                st.html(dedent(f"""
                                    <div style="
                                        background:#11141c;
                                        border:1px solid #252a36;
                                        border-radius:12px;
                                        padding:15px;
                                        margin-top:12px;
                                        color:#94a3b8;
                                        font-size:13px;
                                    ">

                                    <b style="color:#e2e8f0;">
                                        Evidence Verdict:
                                    </b>
                                    {verdict}

                                    <br><br>

                                    {explanation}

                                    </div>
                                    """))

                    # ====================================================
                    # OVERALL SCORES
                    # ====================================================

                    st.markdown(
                        '<div class="section-title">Reliability Analysis</div>',
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        '<div class="section-subtitle">'
                        'TruthGuard combines the available verification '
                        'signals according to the adaptive verification plan.'
                        '</div>',
                        unsafe_allow_html=True
                    )

                    truth_score = scores.get(
                        "truth_score",
                        0
                    )

                    confidence_score = scores.get(
                        "confidence_score",
                        0
                    )

                    hallucination_probability = scores.get(
                        "hallucination_probability",
                        0
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.html(dedent(f"""
                            <div class="score-card">

                                <div class="score-name">
                                    TRUTH SCORE
                                </div>

                                <div class="score-value">
                                    {truth_score}%
                                </div>

                                <div class="score-description">
                                    Overall reliability
                                </div>

                            </div>
                            """))

                    with col2:

                        st.html(dedent(f"""
                            <div class="score-card">

                                <div class="score-name">
                                    CONFIDENCE
                                </div>

                                <div class="score-value">
                                    {confidence_score}%
                                </div>

                                <div class="score-description">
                                    Assessment confidence
                                </div>

                            </div>
                            """))

                    with col3:

                        st.html(dedent(f"""
                            <div class="score-card">

                                <div class="score-name">
                                    HALLUCINATION RISK
                                </div>

                                <div class="score-value">
                                    {hallucination_probability}%
                                </div>

                                <div class="score-description">
                                    Estimated risk
                                </div>

                            </div>
                            """))

                    # ====================================================
                    # RISK DECISION
                    # ====================================================

                    st.markdown(
                        '<div class="section-title">Risk Decision</div>',
                        unsafe_allow_html=True
                    )

                    decision = risk.get(
                        "decision",
                        "UNKNOWN"
                    )

                    reason = risk.get(
                        "reason",
                        ""
                    )

                    if decision == "ACCEPT":

                        st.html(dedent(f"""
                            <div class="status-safe">

                                ✓ RESPONSE ACCEPTED

                                <div style="
                                    color:#94a3b8;
                                    font-weight:400;
                                    margin-top:6px;
                                ">
                                    {reason}
                                </div>

                            </div>
                            """))

                    elif decision == "REVIEW":

                        st.html(dedent(f"""
                            <div style="
                                background:rgba(234,179,8,0.07);
                                border:1px solid rgba(234,179,8,0.20);
                                color:#fde68a;
                                border-radius:12px;
                                padding:14px 17px;
                                font-size:13px;
                                font-weight:650;
                                margin-top:18px;
                            ">

                                ⚠ RESPONSE NEEDS REVIEW

                                <div style="
                                    color:#94a3b8;
                                    font-weight:400;
                                    margin-top:6px;
                                ">
                                    {reason}
                                </div>

                            </div>
                            """))

                    elif decision == "REGENERATE":

                        st.html(dedent(f"""
                            <div style="
                                background:rgba(239,68,68,0.07);
                                border:1px solid rgba(239,68,68,0.20);
                                color:#fca5a5;
                                border-radius:12px;
                                padding:14px 17px;
                                font-size:13px;
                                font-weight:650;
                                margin-top:18px;
                            ">

                                🔄 RESPONSE REQUIRES REGENERATION

                                <div style="
                                    color:#94a3b8;
                                    font-weight:400;
                                    margin-top:6px;
                                ">
                                    {reason}
                                </div>

                            </div>
                            """))

                    # ====================================================
                    # REGENERATION
                    # ====================================================

                    regeneration = result.get(
                        "regeneration"
                    )

                    if regeneration:

                        st.markdown(
                            '<div class="section-title">'
                            'Response Regeneration'
                            '</div>',
                            unsafe_allow_html=True
                        )

                        st.html(dedent(f"""
                            <div class="answer-card">

                                <div class="answer-label">
                                    REGENERATED RESPONSE
                                </div>

                                <div class="answer-text">
                                    {regeneration.get(
                                        "regenerated_response",
                                        ""
                                    )}
                                </div>

                            </div>
                            """))

                    # ====================================================
                    # FINAL VERIFICATION
                    # ====================================================

                    final_verification = result.get(
                        "final_verification"
                    )

                    if final_verification:

                        st.markdown(
                            '<div class="section-title">'
                            'Final Verification'
                            '</div>',
                            unsafe_allow_html=True
                        )

                        final_score = final_verification.get(
                            "score",
                            "N/A"
                        )

                        final_verdict = final_verification.get(
                            "verdict",
                            "N/A"
                        )

                        final_explanation = final_verification.get(
                            "explanation",
                            ""
                        )

                        col1, col2 = st.columns(2)

                        with col1:

                            st.html(dedent(f"""
                                <div class="score-card">

                                    <div class="score-name">
                                        FINAL VERIFICATION SCORE
                                    </div>

                                    <div class="score-value">
                                        {final_score}
                                    </div>

                                </div>
                                """))

                        with col2:

                            st.html(dedent(f"""
                                <div class="score-card">

                                    <div class="score-name">
                                        FINAL VERDICT
                                    </div>

                                    <div class="score-value"
                                         style="font-size:20px;">
                                        {final_verdict}
                                    </div>

                                </div>
                                """))

                        st.html(dedent(f"""
                            <div class="answer-card"
                                 style="margin-top:15px;">

                                <div class="answer-text">
                                    {final_explanation}
                                </div>

                            </div>
                            """))

                    # ====================================================
                    # FINAL ANSWER
                    # ====================================================

                    st.markdown(
                        '<div class="section-title">Final Answer</div>',
                        unsafe_allow_html=True
                    )

                    st.html(dedent(f"""
                        <div class="answer-card">

                            <div class="answer-label">
                                TRUTHGUARD VERIFIED ANSWER
                            </div>

                            <div class="answer-text">
                                {escape(final_response)}
                            </div>

                        </div>
                        """))

                else:

                    try:

                        error_data = response.json()

                        error_message = error_data.get(
                            "detail",
                            "Unknown backend error"
                        )

                    except ValueError:

                        error_message = (
                            response.text
                            or "Unknown backend error"
                        )

                    st.error(
                        f"Backend error: {error_message}"
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Cannot connect to TruthGuard backend. "
                    "Make sure FastAPI is running on port 8000."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "The request timed out. "
                    "Please check the backend and try again."
                )

            except Exception as exc:

                st.error(
                    f"Unexpected error: {exc}"
                )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        TruthGuard · AI Hallucination Detection Framework
        <br>
        Adaptive verification for reliable LLM responses
    </div>
    """,
    unsafe_allow_html=True,
)