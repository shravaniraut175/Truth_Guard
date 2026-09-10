# TruthGuard

## AI Framework for Hallucination Detection and Reduction in Large Language Models

TruthGuard is an adaptive AI framework designed to detect, estimate, and reduce hallucinations in Large Language Model (LLM) responses.

Instead of treating every question with the same expensive verification process, TruthGuard first analyzes the complexity of the question and dynamically selects the appropriate verification modules.

The framework combines evidence verification, black-box uncertainty quantification, LLM-as-a-Judge, and white-box uncertainty quantification to calculate a **Truth Score, Hallucination Probability, Confidence Score, and Risk Level**.

---

## Key Idea

Traditional LLM workflow:

```text
User Question
      ↓
LLM
      ↓
Answer
```

TruthGuard workflow:

```text
User Question
      ↓
Query Analyzer
      ↓
LOW / MEDIUM / HIGH
      ↓
Initial Response
      ↓
Adaptive Verification
      ↓
Score Fusion
      ↓
Risk Decision
      ↓
Accept / Review / Regenerate
      ↓
Final Verification
      ↓
Final Answer
```

The goal is to estimate the reliability of an LLM response rather than claiming to provide a perfect truth oracle.

---

## Features

- Adaptive LOW / MEDIUM / HIGH query routing
- Initial LLM response generation
- Claim extraction for complex responses
- Evidence verification using Gemini and Google Search grounding
- Black-Box Uncertainty Quantification
- LLM-as-a-Judge
- White-Box Uncertainty Quantification using a local Qwen model
- Weighted multi-signal score fusion
- Hallucination probability estimation
- Confidence estimation
- Risk-based response decisions
- Automatic response regeneration for high-risk responses
- Final verification after regeneration
- FastAPI backend
- Streamlit frontend
- Local execution support

---

## Adaptive Verification

TruthGuard does not run every module for every question.

### LOW

Used for straightforward questions.

```text
Initial Response
      ↓
Quick Evidence Check
      ↓
Lightweight LLM Judge
      ↓
Score Fusion
      ↓
Risk Decision
```

Skipped:

- Claim Extraction
- Black-Box UQ
- White-Box UQ

### MEDIUM

Used for questions requiring explanation, comparison, or moderate reasoning.

```text
Initial Response
      ↓
Claim Extraction
      ↓
Evidence Verification
      ↓
Black-Box UQ
      ↓
LLM Judge
      ↓
Score Fusion
      ↓
Risk Decision
```

White-Box UQ is skipped.

### HIGH

Used for complex technical, multi-step, or future-oriented questions.

```text
Initial Response
      ↓
Claim Extraction
      ↓
Evidence Verification
      ↓
Black-Box UQ
      ↓
LLM Judge
      ↓
White-Box UQ
      ↓
Score Fusion
      ↓
Risk Decision
      ↓
Regeneration if required
      ↓
Final Verification
```

The local Qwen model is loaded only for HIGH-complexity queries.

---

## Verification Modules

### 1. Query Analyzer

A deterministic Python rule-based analyzer classifies questions into:

```text
LOW
MEDIUM
HIGH
```

It also identifies broad domains such as:

```text
FACTUAL
TECHNICAL
CURRENT
OPINION
MULTI_STEP
```

Using deterministic routing keeps the adaptive controller fast and predictable.

---

### 2. Initial Response Generator

The initial answer is generated through OpenRouter.

The generator is instructed to:

- answer the user's question
- remain relevant
- avoid fabricated facts
- state uncertainty when appropriate
- avoid claiming external verification when it has not occurred

---

### 3. Claim Extraction

For MEDIUM and HIGH questions, the generated response is divided into individual claims.

Example:

```text
The Earth revolves around the Sun.
Water freezes at 0°C under standard atmospheric pressure.
```

becomes:

```text
Claim 1 → The Earth revolves around the Sun.
Claim 2 → Water freezes at 0°C under standard atmospheric pressure.
```

This allows evidence and other verification methods to operate at claim level.

---

### 4. Evidence Verification

Evidence verification uses Gemini with Google Search grounding.

For each relevant claim, TruthGuard obtains:

- verification score
- verdict
- explanation
- supporting sources
- model information

This provides external evidence rather than relying only on the original LLM.

---

### 5. Black-Box Uncertainty Quantification

Black-Box UQ generates multiple responses for the same question and measures their semantic consistency.

The current implementation uses:

```text
OpenRouter
+
Sentence Transformers
+
all-MiniLM-L6-v2
```

The resulting semantic consistency is converted into a 0–100 consistency score.

**Important:** Black-Box UQ runs once for the complete question/response. It is not repeatedly executed for every extracted claim.

---

### 6. LLM-as-a-Judge

An LLM evaluates the generated response/claims and produces an additional reliability score.

This provides an independent verification signal alongside evidence and consistency.

The current implementation uses OpenRouter.

---

### 7. White-Box Uncertainty Quantification

White-Box UQ is enabled only for HIGH-complexity questions.

The current local model is:

```text
Qwen/Qwen3-0.6B
```

The module examines token-level model confidence and calculates a White-Box score.

Because the model is loaded locally, it is intentionally not loaded for LOW or MEDIUM questions.

---

## Score Fusion

TruthGuard combines the available verification signals using the following experimental weights:

| Verification Signal | Weight |
|---|---:|
| Evidence | 35% |
| Black-Box UQ | 25% |
| LLM Judge | 25% |
| White-Box UQ | 15% |

Conceptually:

```text
Truth Score =
    Evidence × 0.35
  + Black-Box × 0.25
  + Judge × 0.25
  + White-Box × 0.15
```

When a module is not applicable, the available weights are normalized.

For MEDIUM and HIGH responses, claim-level Evidence/Judge/White-Box scores are averaged before the overall fusion. The single Black-Box score is then included once.

---

## Risk Calculation

TruthGuard calculates:

```text
Hallucination Probability = 100 - Truth Score
```

Current risk thresholds:

| Hallucination Probability | Risk |
|---:|---|
| < 20% | LOW |
| 20% – 60% | MEDIUM |
| > 60% | HIGH |

The system then produces one of three decisions:

```text
ACCEPT
REVIEW
REGENERATE
```

A high-risk response can be regenerated and subsequently verified again.

---

## Regeneration and Final Verification

When the risk decision is `REGENERATE`:

```text
High-Risk Response
       ↓
Gemini Regeneration
       ↓
Safer Response
       ↓
Final Verification
       ↓
Final Answer
```

The purpose is to reduce detected hallucination risk instead of simply reporting that a response may be unreliable.

---

## Technology Stack

### Frontend

- Streamlit

### Backend

- Python
- FastAPI
- Uvicorn

### LLM Providers / Models

- OpenRouter
- Google Gemini
- Qwen3-0.6B

### Machine Learning

- PyTorch
- Hugging Face Transformers
- Sentence Transformers

### Evidence

- Google Search grounding
- Gemini

### Development

- Git
- GitHub
- VS Code

---

## Project Structure

```text
TruthGuard/
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   │
│   └── core/
│       ├── __init__.py
│       ├── generator.py
│       ├── query_analyzer.py
│       ├── claim_extractor.py
│       ├── blackbox.py
│       ├── evidence.py
│       ├── judge.py
│       ├── whitebox.py
│       ├── fusion.py
│       ├── risk.py
│       ├── regenerator.py
│       ├── final_verifier.py
│       ├── pipeline.py
│       ├── router.py
│       └── openrouter_client.py
│
├── frontend/
│   └── app.py
│
├── evaluation/
│
├── tests/
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd TruthGuard
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root.

Example:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openrouter/free

GOOGLE_API_KEY=your_gemini_api_key

EVIDENCE_MODEL=gemini-2.5-flash
EVIDENCE_FALLBACK_MODELS=gemini-2.5-flash-lite,gemini-3.5-flash-lite,gemini-3.5-flash
```

Add any additional variables required by your local configuration.

### Security

Never commit API keys to GitHub.

Your `.gitignore` should include:

```gitignore
.env
venv/
.venv/
__pycache__/
*.pyc
```

---

## Running the Backend

From the project root:

```powershell
uvicorn backend.main:app --reload
```

The backend will normally be available at:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Running the Frontend

Open another terminal.

Activate the same virtual environment and run:

```powershell
streamlit run frontend/app.py
```

Streamlit will provide the local application URL.

The frontend communicates with the FastAPI backend to run TruthGuard verification.

---

## Example Questions

### LOW

```text
Who invented the telephone?
```

Expected route:

```text
Initial Response
→ Quick Evidence Check
→ Lightweight LLM Judge
→ Score Fusion
→ Risk Decision
```

### MEDIUM

```text
What are the advantages and disadvantages of electric vehicles?
```

Expected route:

```text
Initial Response
→ Claim Extraction
→ Evidence
→ Black-Box
→ Judge
→ Score Fusion
→ Risk Decision
```

### HIGH

```text
How will quantum computing impact global cybersecurity over the next decade?
```

Expected route:

```text
Initial Response
→ Claim Extraction
→ Evidence
→ Black-Box
→ Judge
→ White-Box
→ Score Fusion
→ Risk Decision
→ Regeneration if required
→ Final Verification
```

---

## API

### Health

```http
GET /health
```

Response:

```json
{
  "status": "healthy"
}
```

### Verify

```http
POST /verify
```

Request:

```json
{
  "question": "Who invented the telephone?"
}
```

The response contains:

- query analysis
- verification plan
- modules used
- original response
- claims
- component scores
- Truth Score
- Hallucination Probability
- Confidence Score
- risk decision
- regeneration result
- final verification
- final response

---

## Example Result

A successful LOW-complexity verification can produce results such as:

```text
Truth Score: 97.08
Hallucination Probability: 2.92
Confidence Score: 95
Risk Level: LOW
Decision: ACCEPT
```

These values are examples from testing and should not be treated as fixed outputs.

---

## Current Limitations

### API Rate Limits

Some TruthGuard components use external LLM APIs and are subject to provider rate limits and quotas.

For example, OpenRouter free models have request limits. If the daily limit is exhausted, OpenRouter-dependent modules may return HTTP 429 errors.

This does not indicate that the TruthGuard pipeline itself is broken.

### Local Qwen Model

White-Box UQ uses a local Qwen model and requires sufficient RAM and processing resources.

For this reason, the current complete prototype is intended to run locally rather than on a low-memory deployment environment.

### Research Scope

TruthGuard estimates reliability and hallucination risk. It does not mathematically guarantee that an answer is true.

---

## Research Evaluation

The next major stage of the project is experimental evaluation.

TruthGuard should be evaluated against a baseline LLM using labelled questions/responses.

Recommended metrics include:

- Accuracy
- Precision
- Recall
- F1-score
- Hallucination detection rate
- Hallucination reduction rate
- False positives
- False negatives
- Average latency
- API calls
- RAM usage

A key comparison is:

```text
Baseline LLM
     VS
TruthGuard
```

The evaluation should determine whether adaptive multi-signal verification reduces hallucination while maintaining acceptable latency and resource usage.

---

## Research Contribution

The main contribution of TruthGuard is an **adaptive multi-signal hallucination verification framework**.

Instead of applying one hallucination-detection technique to every response, TruthGuard dynamically selects verification methods according to question complexity.

The framework combines:

```text
Evidence
   +
Black-Box Consistency
   +
LLM Judgment
   +
White-Box Confidence
   ↓
Unified Reliability Assessment
   ↓
Risk-Based Decision
   ↓
Response Regeneration
   ↓
Final Verification
```

This provides a modular architecture that can be extended with additional verification models and scoring techniques in future work.

---

## Future Improvements

Potential future work includes:

- Better query-complexity classification
- Calibrated confidence scores
- Larger evaluation datasets
- Improved claim extraction
- Batched LLM judging to reduce API calls
- More advanced evidence retrieval
- Additional open-source local models
- Better regeneration strategies
- Automated benchmarking
- More robust uncertainty calibration
- Resource-aware model selection

---

## Project Status

```text
Core Architecture              ✅
Adaptive Routing                ✅
Initial Response Generation     ✅
Claim Extraction                ✅
Evidence Verification           ✅
Black-Box UQ                    ✅
LLM-as-a-Judge                  ✅
White-Box UQ                    ✅
Score Fusion                    ✅
Risk Decision                   ✅
Response Regeneration           ✅
Final Verification              ✅
FastAPI Backend                 ✅
Streamlit Frontend              ✅
Local End-to-End Prototype      ✅
Dataset Evaluation              🔄
Deployment                      ⏸️
```

---

## Disclaimer

TruthGuard is a research and educational prototype for estimating LLM response reliability and hallucination risk. Its scores represent verification signals and should not be interpreted as absolute proof of factual correctness.

---

## License

Add the appropriate project license before publishing the repository.
