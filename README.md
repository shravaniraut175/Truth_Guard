# TruthGuard
### AI Framework for Hallucination Detection and Reduction in Large Language Models

TruthGuard is an AI-based verification framework designed to detect potential hallucinations in Large Language Model (LLM) responses. It does not simply generate an answer—it evaluates the generated response using multiple verification techniques, combines their results, determines the risk level, and can regenerate the answer when the detected risk is high.

---

## 1. Overview

Large Language Models can generate responses that appear convincing but contain incorrect, unsupported, outdated, or fabricated information. TruthGuard addresses this problem through a multi-stage verification pipeline.

The framework:
1. Accepts a user query.
2. Analyzes the query complexity.
3. Generates an initial response.
4. Selects an appropriate verification strategy.
5. Extracts factual claims when required.
6. Searches the web for supporting evidence.
7. Evaluates claims using an LLM-based judge.
8. Performs black-box uncertainty verification.
9. Performs white-box verification for high-complexity queries when enabled.
10. Combines verification scores into an overall truth score.
11. Calculates hallucination probability and confidence.
12. Determines the risk level.
13. Regenerates the response when the risk is high.
14. Performs final verification of the regenerated response.

---

## 2. Key Features

### Adaptive Verification
TruthGuard does not apply the same verification process to every query. Queries are classified into:
- **LOW**
- **MEDIUM**
- **HIGH**

Verification modules are dynamically selected according to the complexity level.

### Claim Extraction
For medium and high complexity queries, TruthGuard extracts individual claims from the generated response. Claims are classified as:
- Factual
- Numerical
- Temporal
- Causal
- Comparative
- Opinion

### Web-Based Evidence Verification
TruthGuard retrieves relevant information from the web using DuckDuckGo search and evaluates the retrieved evidence using OpenRouter. Each claim receives:
- Evidence score
- Verdict
- Explanation
- Supporting sources

### LLM-as-a-Judge
An independent LLM-based judge evaluates whether a claim is consistent with the generated response and available evidence. Possible verdicts include:
- `SUPPORTED`
- `PARTIALLY_SUPPORTED`
- `NOT_SUPPORTED`
- `UNCERTAIN`

### Black-Box Uncertainty Verification
Black-box verification evaluates consistency across model responses to identify potentially unreliable or unstable answers.

### White-Box Uncertainty Verification
For high-complexity verification routes, TruthGuard can use white-box uncertainty analysis based on model-level information.

### Score Fusion
Scores from available verification modules are combined into a normalized truth score.

| Verification Module | Weight |
| :--- | :--- |
| Evidence | 35% |
| Black-Box | 25% |
| LLM Judge | 25% |
| White-Box | 15% |

Weights are automatically normalized when a verification module is not used.

### Risk Detection
TruthGuard calculates:
- Truth Score
- Hallucination Probability
- Confidence Score
- Risk Level

| Hallucination Probability | Risk Level |
| :--- | :--- |
| < 20% | LOW |
| 20–60% | MEDIUM |
| > 60% | HIGH |

### Response Regeneration
If the risk is high, TruthGuard sends the original response and verification findings to the regeneration module. The system generates an improved response using the detected verification issues.

### Final Verification
The regenerated response is passed through a final verification stage to check whether the response has improved.

---

## 3. Verification Strategy

### LOW Complexity
```text
User Query
 ↓
Initial Response
 ↓
Quick Evidence Verification
 ↓
LLM Judge
 ↓
Score Fusion
 ↓
Risk Decision
```

### MEDIUM Complexity
```text
User Query
 ↓
Initial Response
 ↓
Claim Extraction
 ↓
Claim-Level Evidence Verification
 ↓
Black-Box Verification
 ↓
LLM Judge
 ↓
Score Fusion
 ↓
Risk Decision
```

### HIGH Complexity
```text
User Query
 ↓
Initial Response
 ↓
Claim Extraction
 ↓
Evidence Verification
 ↓
Black-Box Verification
 ↓
LLM Judge
 ↓
White-Box Verification
 ↓
Score Fusion
 ↓
Risk Decision
 ↓
Regeneration if Required
 ↓
Final Verification
```

---

## 4. Technology Stack

- **Backend:** Python, FastAPI, Uvicorn
- **AI / LLM:** Google Gemini, OpenRouter, Hugging Face Transformers, PyTorch
- **Web Evidence:** DuckDuckGo Search, `ddgs`
- **Validation:** Pydantic
- **Frontend:** Streamlit
- **Deployment:** Render, Streamlit deployment

---

## 5. Project Structure

```text
Truth_Guard/
├── backend/
│   ├── api/
│   │   └── main.py
│   │
│   └── core/
│       ├── generator.py
│       ├── claim_extractor.py
│       ├── evidence.py
│       ├── judge.py
│       ├── blackbox.py
│       ├── whitebox.py
│       ├── fusion.py
│       ├── risk.py
│       ├── router.py
│       ├── query_analyzer.py
│       ├── regenerator.py
│       ├── final_verifier.py
│       ├── openrouter_client.py
│       └── pipeline.py
│
├── frontend/
│   └── app.py
│
├── tests/
│   └── ...
│
├── .env
├── requirements.txt
└── README.md
```

---

## 6. Core Modules

- **`generator.py`**: Generates the initial answer to the user's question. Gemini is used as the primary response-generation model.
- **`query_analyzer.py`**: Analyzes the incoming question and determines its complexity level. The result is used by the router to select the appropriate verification pipeline.
- **`router.py`**: Creates the verification plan based on the query complexity. It determines which modules should be executed for the current query.
- **`claim_extractor.py`**: Extracts verifiable claims from the generated response using structured output validation through Pydantic.
- **`evidence.py`**: Performs web-based evidence verification via DuckDuckGo Search and OpenRouter.
- **`judge.py`**: Uses an LLM-as-a-Judge approach to evaluate the factual consistency of claims returning structured JSON data.
- **`blackbox.py`**: Performs black-box uncertainty/consistency analysis without requiring internal model probabilities.
- **`whitebox.py`**: Provides white-box uncertainty analysis for verification routes where this module is enabled.
- **`fusion.py`**: Combines available verification scores into a normalized truth score, hallucination probability, confidence score, and risk level.
- **`risk.py`**: Converts verification results into a risk decision, determining whether the response should be regenerated.
- **`regenerator.py`**: Generates a corrected response when the verification pipeline identifies a high-risk response.
- **`final_verifier.py`**: Performs verification on the regenerated response, providing an additional validation stage after correction.
- **`pipeline.py`**: Acts as the central controller orchestrating the entire TruthGuard workflow.

---

## 7. Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=YOUR_API_KEY
GEMINI_MODEL=gemini-3.5-flash-lite
CLAIM_MODEL=gemini-3.5-flash-lite
EVIDENCE_MODEL=gemini-3.5-flash-lite
EVIDENCE_FALLBACK_MODELS=gemini-3.1-flash-lite,gemini-3.5-flash
JUDGE_MODEL=gemini-3.5-flash-lite
OPENROUTER_API_KEY=YOUR_OPENROUTER_KEY
OPENROUTER_MODEL=openrouter/free
```

---

## 8. Installation

### Step 1 — Clone the Repository
```bash
git clone https://github.com/shravaniraut175/TruthGuard-ai.git
cd TruthGuard-ai
```

### Step 2 — Create a Virtual Environment
Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
pip install ddgs
```

---

## 9. Running the Backend

Start the FastAPI server:
```bash
uvicorn backend.api.main:app --reload
```
- **API Endpoint:** `http://localhost:8000`
- **FastAPI Documentation (Swagger UI):** `http://localhost:8000/docs`

---

## 10. Running the Frontend

Start the Streamlit application:
```bash
streamlit run frontend/app.py
```
The Streamlit interface provides a user-facing dashboard for entering questions and inspecting TruthGuard verification findings.

---

## 11. Testing

Individual modules can be tested prior to testing the complete pipeline.

- **Test Evidence Verification:** Verify claims using search and evaluate scores.
- **Test Claim Extraction:** Pass responses to identify individual assertions and their types.
- **Test Judge:** Provide a claim, generated response, and evidence result to output structured JSON.
- **Test Complete Pipeline:** Submit a query via frontend/API to run the end-to-end multi-stage flow.

---

## 12. Example Verification

### Example 1
- **Input:** `Mumbai is the capital of India.`
- **Expected Behavior:** System retrieves evidence indicating the claim is contradicted/unsupported, yielding a low evidence score and a high hallucination risk.

### Example 2
- **Input:** `New Delhi is the capital of India.`
- **Expected Behavior:** High evidence score, verdict `SUPPORTED`, low hallucination risk.

---

## 13. Output Schema

The complete TruthGuard pipeline returns structured JSON:

```json
{
  "question": "string",
  "query_analysis": {},
  "verification_plan": [],
  "modules_used": [],
  "original_response": "string",
  "claims": [],
  "overall_scores": {
    "truth_score": 91.5,
    "hallucination_probability": 8.5,
    "confidence_score": 88.2,
    "risk_level": "LOW"
  },
  "component_results": {},
  "risk_decision": {},
  "regeneration": {},
  "final_verification": {},
  "final_response": "string"
}
```

---

## 14. Error Handling

TruthGuard includes robust handling for:
- Empty queries and missing API keys
- Failed LLM requests and empty model responses
- Invalid JSON outputs and score boundaries
- Web search errors & missing evidence
- Upstream API rate limits & provider outages

---

## 15. API Rate Limits

TruthGuard relies on external AI providers where rate limits may apply:
- `429 RESOURCE_EXHAUSTED` indicates provider quota exhaustion.
- OpenRouter free-tier endpoints can return rate limits when daily caps are reached.

---

## 16. Security

- API keys must never be hard-coded into repository files.
- Store secrets solely in `.env` and keep `.env` inside `.gitignore`.
- Immediately revoke and rotate any accidentally exposed keys.

---

## 17. Limitations

- Verification quality depends heavily on the quality and authority of retrieved search results.
- Search snippets may lack full context.
- LLM judges can occasionally commit reasoning or classification errors.
- Upstream rate limits can interrupt deep multi-step verification flows.
- White-box uncertainty metrics require access to underlying model logits and weights.

---

## 18. Future Enhancements

- RAG-based persistent evidence retrieval and document stores
- Source credibility and domain authority weighting
- Cross-source contradiction analysis
- Enhanced temporal and chronological verification
- Token-level and claim-level citation mapping
- Multilingual hallucination detection
- Adaptive routing across extended LLM providers (Anthropic, Cohere, local vLLM)

---

## 19. Project Objective

```text
Evidence + Black-Box Consistency + LLM Judge + White-Box Uncertainty
                            ↓
                      Score Fusion
                            ↓
                    Risk Assessment
                            ↓
                 Response Regeneration
```
This ensures TruthGuard delivers not just raw text, but an actionable, quantifiable assessment of its trustworthiness.

---

## 20. Conclusion

TruthGuard provides a modular, end-to-end framework for hallucination detection and mitigation in Large Language Models. By uniting adaptive routing, atomic claim extraction, live web evidence retrieval, model-as-a-judge evaluation, dual uncertainty analysis, weighted score fusion, risk policies, and grounded regeneration, it makes LLM outputs transparent, measurable, and reliable.