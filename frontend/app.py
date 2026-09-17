import requests
import streamlit as st
from html import escape

st.set_page_config(
    page_title="TruthGuard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_URL = "http://127.0.0.1:8000/verify"


def esc(value):
    return escape(str(value or ""))


def pct(value):
    try:
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return "N/A"


def verdict_info(value):
    v = str(value or "UNKNOWN").upper()
    if v == "SUPPORTED":
        return "✓ Supported", "good"
    if v in {"PARTIALLY_SUPPORTED", "PARTIALLY SUPPORTED"}:
        return "⚠ Partially Supported", "warn"
    if v in {"NOT_SUPPORTED", "NOT SUPPORTED"}:
        return "✕ Not Supported", "bad"
    if v == "UNCERTAIN":
        return "? Uncertain", "warn"
    return v.replace("_", " ").title(), "neutral"


def render_markdown(text):
    # Important: generated answers are rendered as Markdown, not HTML.
    st.markdown(str(text or ""), unsafe_allow_html=False)


st.markdown(
    """
    <style>
    [data-testid="stHeader"], footer, #MainMenu {visibility:hidden;height:0;}
    .block-container{max-width:1180px;padding-top:2rem;padding-bottom:3rem;}
    .stApp{
        background:
        radial-gradient(circle at 15% 10%,rgba(99,102,241,.08),transparent 28%),
        radial-gradient(circle at 85% 15%,rgba(14,165,233,.07),transparent 25%),
        #0b0d12;
    }
    .brand{display:flex;align-items:center;gap:13px;margin-bottom:8px;}
    .brand-icon{
        width:46px;height:46px;border-radius:14px;
        background:linear-gradient(135deg,#6366f1,#8b5cf6);
        display:flex;align-items:center;justify-content:center;font-size:24px;
    }
    .brand-name{font-size:28px;font-weight:750;color:#f8fafc;}
    .brand-badge,.pill{
        display:inline-block;border-radius:20px;padding:5px 10px;
        font-size:11px;font-weight:650;
    }
    .brand-badge,.pill.active{
        background:rgba(99,102,241,.10);
        color:#a5b4fc;border:1px solid rgba(99,102,241,.28);
    }
    .pill{
        background:#151923;color:#94a3b8;border:1px solid #282e3b;
        margin:3px 4px 3px 0;
    }
    .hero{margin:2rem 0;}
    .hero-title{font-size:42px;line-height:1.15;font-weight:760;color:#f8fafc;}
    .hero-title span{
        background:linear-gradient(90deg,#818cf8,#c084fc);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    }
    .hero-description{max-width:760px;color:#94a3b8;font-size:16px;line-height:1.7;margin-top:12px;}
    .stTextArea textarea{
        background:#11141c!important;color:#f1f5f9!important;
        border:1px solid #303646!important;border-radius:12px!important;
        font-size:15px!important;
    }
    .stButton>button{
        width:100%;height:48px;border-radius:11px;border:none;
        background:linear-gradient(90deg,#6366f1,#7c3aed);
        color:#fff;font-size:14px;font-weight:700;
    }
    .section-title{font-size:18px;font-weight:700;color:#f8fafc;margin:30px 0 12px;}
    .section-subtitle{color:#64748b;font-size:13px;margin-bottom:14px;}
    .card,.metric,.overview{
        background:#11141c;border:1px solid #252a36;border-radius:16px;padding:20px;
        margin-bottom:14px;
    }
    .overview{background:linear-gradient(135deg,#11141c,#151827);padding:24px;}
    .metric{min-height:112px;}
    .metric-label{
        color:#64748b;font-size:11px;font-weight:750;
        letter-spacing:.7px;text-transform:uppercase;
    }
    .metric-value{color:#f8fafc;font-size:29px;font-weight:760;margin-top:7px;}
    .metric-help{color:#64748b;font-size:11px;margin-top:5px;}
    .answer-label{
        color:#818cf8;font-size:11px;font-weight:750;
        letter-spacing:.8px;text-transform:uppercase;margin-bottom:12px;
    }
    .answer-box{
        background:#0d1017;border:1px solid #252a36;
        border-radius:13px;padding:18px;margin-bottom:14px;
    }
    .status{border-radius:13px;padding:14px 17px;margin:8px 0 16px;font-size:13px;font-weight:700;}
    .status.good{background:rgba(34,197,94,.07);border:1px solid rgba(34,197,94,.22);color:#86efac;}
    .status.warn{background:rgba(234,179,8,.07);border:1px solid rgba(234,179,8,.22);color:#fde68a;}
    .status.bad{background:rgba(239,68,68,.07);border:1px solid rgba(239,68,68,.22);color:#fca5a5;}
    .status.neutral{background:rgba(148,163,184,.07);border:1px solid rgba(148,163,184,.18);color:#cbd5e1;}
    .reason{color:#94a3b8;font-weight:400;margin-top:6px;line-height:1.55;}
    .breakdown{display:flex;align-items:center;gap:12px;margin:14px 0;}
    .breakdown-name{width:120px;color:#cbd5e1;font-size:12px;}
    .bar{flex:1;height:8px;background:#1c2130;border-radius:10px;overflow:hidden;}
    .fill{height:100%;background:linear-gradient(90deg,#6366f1,#a78bfa);}
    .weight{width:45px;text-align:right;color:#818cf8;font-size:11px;font-weight:700;}
    .score-mini{
        background:#0d1017;border:1px solid #252a36;border-radius:11px;padding:12px;
    }
    div[data-testid="stExpander"]{
        background:#11141c;border:1px solid #252a36;border-radius:13px;
        margin-bottom:10px;
    }
    .footer{text-align:center;color:#475569;font-size:11px;margin-top:55px;padding-top:20px;border-top:1px solid #1c2029;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="brand">
        <div class="brand-icon">🛡️</div>
        <div class="brand-name">TruthGuard</div>
        <div class="brand-badge">AI VERIFICATION</div>
    </div>
    <div class="hero">
        <div class="hero-title">Know when your AI answer<br><span>can be trusted.</span></div>
        <div class="hero-description">
            TruthGuard analyzes LLM-generated responses using adaptive verification
            techniques to estimate reliability and hallucination risk.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<p style="font-size:14px;font-weight:650;color:#e2e8f0;">Ask a question</p>',
    unsafe_allow_html=True,
)

question = st.text_area(
    "Question",
    placeholder="Example: Who invented the telephone?",
    height=125,
    label_visibility="collapsed",
)

st.markdown(
    '<p style="font-size:12px;color:#64748b;margin-top:-10px;">'
    'TruthGuard automatically chooses LOW, MEDIUM, or HIGH verification.</p>',
    unsafe_allow_html=True,
)

verify_clicked = st.button("🔍 Verify Response", type="primary")

# ============================================================
# RESULT
# ============================================================

if verify_clicked:
    if not question.strip():
        st.warning("Please enter a question before starting verification.")
    else:
        with st.spinner("Generating and verifying the response..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"question": question.strip()},
                    timeout=300,
                )

                if response.status_code != 200:
                    try:
                        detail = response.json().get("detail", "Unknown backend error")
                    except ValueError:
                        detail = response.text or "Unknown backend error"
                    st.error(f"Backend error: {detail}")
                    st.stop()

                result = response.json()

                analysis = result.get("query_analysis", {})
                plan = result.get("verification_plan", {})
                modules = result.get("modules_used", [])
                scores = result.get("overall_scores", {})
                risk = result.get("risk_decision", {})
                original = result.get("original_response", "")
                final = result.get("final_response", original)
                claims = result.get("claims", [])
                components = result.get("component_results", {})
                regeneration = result.get("regeneration")
                final_verification = result.get("final_verification")

                complexity = str(analysis.get("level", "N/A")).upper()
                decision = str(risk.get("decision", "UNKNOWN")).upper()
                decision_label = {
                    "ACCEPT": "✓ RESPONSE ACCEPTED",
                    "REVIEW": "⚠ RESPONSE NEEDS REVIEW",
                    "REGENERATE": "🔄 RESPONSE REQUIRES REGENERATION",
                }.get(decision, decision)

                status_type = (
                    "good" if decision == "ACCEPT"
                    else "warn" if decision == "REVIEW"
                    else "bad"
                )

                # --------------------------------------------------------
                # 1. OVERVIEW
                # --------------------------------------------------------

                st.markdown(
                    '<div class="section-title">Verification Result</div>',
                    unsafe_allow_html=True,
                )

                st.html(
                    f"""
                    <div class="overview">
                        <div class="answer-label">FINAL ASSESSMENT</div>
                        <div style="display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap;">
                            <div>
                                <div style="color:#f8fafc;font-size:24px;font-weight:760;">
                                    {esc(decision_label)}
                                </div>
                                <div class="reason">
                                    {esc(risk.get("reason", ""))}
                                </div>
                            </div>
                            <div class="pill active">
                                Complexity: {esc(complexity)}
                            </div>
                        </div>
                    </div>
                    """
                )

                # --------------------------------------------------------
                # 2. MAIN SCORES
                # --------------------------------------------------------

                st.markdown(
                    '<div class="section-title">Reliability Summary</div>',
                    unsafe_allow_html=True,
                )

                c1, c2, c3 = st.columns(3)

                metrics = [
                    ("Truth Score", scores.get("truth_score", 0), "Overall reliability"),
                    ("Confidence", scores.get("confidence_score", 0), "Agreement between signals"),
                    ("Hallucination Risk", scores.get("hallucination_probability", 0), "Estimated unreliable-content risk"),
                ]

                for col, (name, value, help_text) in zip((c1, c2, c3), metrics):
                    with col:
                        st.html(
                            f"""
                            <div class="metric">
                                <div class="metric-label">{esc(name)}</div>
                                <div class="metric-value">{pct(value)}</div>
                                <div class="metric-help">{esc(help_text)}</div>
                            </div>
                            """
                        )

                # --------------------------------------------------------
                # 3. QUERY ANALYSIS
                # --------------------------------------------------------

                st.markdown(
                    '<div class="section-title">1. Query Analysis</div>',
                    unsafe_allow_html=True,
                )

                st.html(
                    f"""
                    <div class="card">
                        <span class="pill active">🧠 Complexity: {esc(complexity)}</span>
                        <span class="pill">📂 Domain: {esc(analysis.get("domain", "N/A"))}</span>
                        <div class="reason">{esc(analysis.get("reason", ""))}</div>
                    </div>
                    """
                )

                # --------------------------------------------------------
                # 4. PIPELINE
                # --------------------------------------------------------

                st.markdown(
                    '<div class="section-title">2. Verification Pipeline</div>',
                    unsafe_allow_html=True,
                )

                labels = {
                    "Initial Response": "🤖 Initial Response",
                    "Claim Extraction": "📋 Claim Extraction",
                    "Quick Evidence Check": "🔎 Quick Evidence",
                    "Evidence Verification": "🔎 Evidence Verification",
                    "Black-Box UQ": "🧠 Black-Box UQ",
                    "Lightweight LLM Judge": "⚖️ LLM Judge",
                    "LLM Judge": "⚖️ LLM Judge",
                    "White-Box UQ": "⚙️ White-Box UQ",
                }

                html = '<div class="card">'
                for module in modules:
                    html += f'<span class="pill active">✓ {esc(labels.get(module, module))}</span>'
                html += "</div>"
                st.html(html)

                skipped = []
                if not plan.get("claim_extraction", False):
                    skipped.append("Claim Extraction")
                if not plan.get("blackbox", False):
                    skipped.append("Black-Box UQ")
                if not plan.get("whitebox", False):
                    skipped.append("White-Box UQ")

                if skipped:
                    st.markdown(
                        f'<div style="color:#64748b;font-size:12px;">'
                        f'Skipped by adaptive routing: {esc(", ".join(skipped))}</div>',
                        unsafe_allow_html=True,
                    )

                # --------------------------------------------------------
                # 5. INITIAL ANSWER
                # --------------------------------------------------------

                st.markdown(
                    '<div class="section-title">3. Initial LLM Response</div>',
                    unsafe_allow_html=True,
                )

                st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                st.markdown('<div class="answer-label">GENERATED RESPONSE</div>', unsafe_allow_html=True)
                render_markdown(original)
                st.markdown("</div>", unsafe_allow_html=True)

                # --------------------------------------------------------
                # 6. CLAIMS
                # --------------------------------------------------------

                if claims:
                    st.markdown(
                        '<div class="section-title">4. Claim Verification</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        "Each extracted claim is shown separately. Expand a claim to inspect its evidence and verification scores."
                    )

                    for i, item in enumerate(claims, 1):
                        claim = item.get("claim", {})
                        evidence = item.get("evidence", {})
                        judge = item.get("judge", {})
                        whitebox = item.get("whitebox", {})
                        fusion = item.get("fusion", {})

                        with st.expander(
                            f"Claim {i}  •  Truth Score: {pct(fusion.get('truth_score'))}",
                            expanded=(i == 1),
                        ):
                            st.markdown(
                                f'<div class="answer-label">CLAIM {i}</div>',
                                unsafe_allow_html=True,
                            )
                            render_markdown(claim.get("text", ""))

                            score_items = []
                            if evidence:
                                score_items.append(("Evidence", evidence.get("score")))
                            if judge:
                                score_items.append(("LLM Judge", judge.get("score")))
                            if whitebox:
                                score_items.append(("White-Box", whitebox.get("whitebox_score")))
                            score_items.append(("Claim Truth", fusion.get("truth_score")))

                            cols = st.columns(len(score_items))
                            for col, (name, value) in zip(cols, score_items):
                                with col:
                                    st.html(
                                        f"""
                                        <div class="score-mini">
                                            <div class="metric-label">{esc(name)}</div>
                                            <div class="metric-value" style="font-size:20px;">
                                                {pct(value)}
                                            </div>
                                        </div>
                                        """
                                    )

                            if evidence:
                                label, kind = verdict_info(evidence.get("verdict"))
                                st.html(
                                    f"""
                                    <div class="status {kind}">
                                        {esc(label)}
                                        <div class="reason">
                                            {esc(evidence.get("explanation", ""))}
                                        </div>
                                    </div>
                                    """
                                )

                                sources = evidence.get("sources", [])
                                if sources:
                                    st.markdown("**Evidence Sources**")
                                    for source in sources:
                                        if isinstance(source, dict):
                                            title = source.get("title", source.get("name", "Source"))
                                            url = source.get("url", source.get("link", ""))
                                            if url:
                                                st.markdown(f"- [{title}]({url})")
                                            else:
                                                st.markdown(f"- {title}")
                                        else:
                                            st.markdown(f"- {source}")

                            if judge:
                                with st.expander("LLM Judge Details"):
                                    st.markdown(f"**Score:** {pct(judge.get('score'))}")
                                    if judge.get("verdict"):
                                        st.markdown(f"**Verdict:** {judge.get('verdict')}")
                                    if judge.get("explanation"):
                                        render_markdown(judge.get("explanation"))

                            if whitebox:
                                with st.expander("White-Box UQ Details"):
                                    st.markdown(
                                        f"**White-Box Score:** {pct(whitebox.get('whitebox_score'))}"
                                    )
                                    if whitebox.get("average_token_probability") is not None:
                                        st.markdown(
                                            f"**Average Token Probability:** {whitebox.get('average_token_probability')}"
                                        )
                                    if whitebox.get("minimum_token_probability") is not None:
                                        st.markdown(
                                            f"**Minimum Token Probability:** {whitebox.get('minimum_token_probability')}"
                                        )

                # --------------------------------------------------------
                # 7. SCORE FUSION
                # --------------------------------------------------------

                st.markdown(
                    '<div class="section-title">5. Score Fusion</div>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    "The overall score combines the verification signals that were applicable to this query."
                )

                component_scores = scores.get("component_scores", {})
                weights = scores.get("weights", {})

                names = [
                    ("evidence", "Evidence"),
                    ("blackbox", "Black-Box UQ"),
                    ("judge", "LLM Judge"),
                    ("whitebox", "White-Box UQ"),
                ]

                html = '<div class="card">'
                for key, name in names:
                    value = component_scores.get(key)
                    if value is None:
                        continue

                    try:
                        value_num = max(0, min(100, float(value)))
                    except (TypeError, ValueError):
                        value_num = 0

                    try:
                        weight_num = float(weights.get(key, 0)) * 100
                    except (TypeError, ValueError):
                        weight_num = 0

                    html += f"""
                    <div class="breakdown">
                        <div class="breakdown-name">{esc(name)}</div>
                        <div class="bar">
                            <div class="fill" style="width:{value_num:.1f}%;"></div>
                        </div>
                        <div style="width:55px;text-align:right;color:#f8fafc;font-size:12px;">
                            {value_num:.1f}
                        </div>
                        <div class="weight">{weight_num:.0f}%</div>
                    </div>
                    """
                html += "</div>"
                st.html(html)

                # --------------------------------------------------------
                # 8. RISK
                # --------------------------------------------------------

                st.markdown(
                    '<div class="section-title">6. Risk Decision</div>',
                    unsafe_allow_html=True,
                )

                st.html(
                    f"""
                    <div class="status {status_type}">
                        {esc(decision_label)}
                        <div class="reason">{esc(risk.get("reason", ""))}</div>
                    </div>
                    """
                )

                # --------------------------------------------------------
                # 9. REGENERATION
                # --------------------------------------------------------

                if regeneration:
                    st.markdown(
                        '<div class="section-title">7. Response Regeneration</div>',
                        unsafe_allow_html=True,
                    )

                    st.info(
                        "The response was considered high risk, so TruthGuard generated a revised response."
                    )

                    r1, r2 = st.columns(2)

                    with r1:
                        st.markdown("**Original Response**")
                        render_markdown(
                            regeneration.get("original_response", original)
                        )

                    with r2:
                        st.markdown("**Regenerated Response**")
                        render_markdown(
                            regeneration.get("regenerated_response", "")
                        )

                # --------------------------------------------------------
                # 10. FINAL VERIFICATION
                # --------------------------------------------------------

                if final_verification:
                    st.markdown(
                        '<div class="section-title">8. Final Verification</div>',
                        unsafe_allow_html=True,
                    )

                    f1, f2 = st.columns(2)

                    with f1:
                        st.html(
                            f"""
                            <div class="metric">
                                <div class="metric-label">Final Verification Score</div>
                                <div class="metric-value">
                                    {pct(final_verification.get("score"))}
                                </div>
                            </div>
                            """
                        )

                    with f2:
                        label, kind = verdict_info(final_verification.get("verdict"))
                        st.html(
                            f"""
                            <div class="status {kind}">
                                {esc(label)}
                                <div class="reason">Final verification verdict</div>
                            </div>
                            """
                        )

                    if final_verification.get("explanation"):
                        render_markdown(final_verification.get("explanation"))

                # --------------------------------------------------------
                # 11. FINAL ANSWER
                # --------------------------------------------------------

                st.markdown(
                    '<div class="section-title">Final Answer</div>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    "### 🛡️ TruthGuard Verified Answer"
                )

                st.markdown(
                    '<div class="answer-box">',
                    unsafe_allow_html=True,
                )
                render_markdown(final)
                st.markdown("</div>", unsafe_allow_html=True)

            except requests.exceptions.ConnectionError:
                st.error(
                    "Cannot connect to the TruthGuard backend. "
                    "Start FastAPI with `uvicorn backend.main:app --reload`."
                )
            except requests.exceptions.Timeout:
                st.error(
                    "The verification request timed out. Check the backend terminal."
                )
            except Exception as exc:
                st.error(f"Unexpected error: {exc}")

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
