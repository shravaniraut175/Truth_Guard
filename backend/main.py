# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel, Field

# from backend.core.generator import generate_response
# from backend.core.claim_extractor import extract_claims
# from backend.core.blackbox import blackbox_score
# from backend.core.evidence import verify_claim
# from backend.core.judge import judge_claim
# from backend.core.fusion import calculate_truth_score
# # from backend.core.whitebox import calculate_whitebox_score
# from backend.core.risk import make_risk_decision
# from backend.core.regenerator import regenerate_response
# from backend.core.final_verifier import final_verify
# from backend.core.pipeline import run_truthguard

# # ---------------------------------------------------------
# # FastAPI Application
# # ---------------------------------------------------------

# app = FastAPI(
#     title="TruthGuard API",
#     description="Backend API for the TruthGuard hallucination detection framework.",
#     version="0.1.0",
# )


# # ---------------------------------------------------------
# # Request Schema
# # ---------------------------------------------------------

# class GenerateRequest(BaseModel):

#     question: str = Field(
#         ...,
#         min_length=1,
#         max_length=5000,
#         description="User question"
#     )


# # ---------------------------------------------------------
# # Response Schema
# # ---------------------------------------------------------

# class GenerateResponse(BaseModel):

#     question: str
#     answer: str
#     model: str = "gemini-2.5-flash"


# class ClaimExtractionRequest(BaseModel):
#     response: str = Field(
#         ...,
#         min_length=1,
#         max_length=10000,
#         description="LLM-generated response"
#     )


# class ClaimExtractionResponse(BaseModel):
#     claims: list[dict]

# class BlackBoxRequest(BaseModel):
#     question: str = Field(
#         ...,
#         min_length=1,
#         max_length=5000
#     )


# class BlackBoxResponse(BaseModel):
#     method: str
#     num_responses: int
#     consistency_score: float
#     responses: list[str]

# class EvidenceRequest(BaseModel):
#     claim: str = Field(
#         ...,
#         min_length=1,
#         max_length=5000
#     )


# class EvidenceResponse(BaseModel):
#     claim: str
#     score: int
#     verdict: str
#     explanation: str
#     sources: list[dict]

# class JudgeRequest(BaseModel):
#     claim: str = Field(
#         ...,
#         min_length=1,
#         max_length=5000
#     )

#     response: str = Field(
#         ...,
#         min_length=1,
#         max_length=10000
#     )


# class JudgeResponse(BaseModel):
#     claim: str
#     score: int
#     verdict: str
#     explanation: str

# class FusionRequest(BaseModel):
#     evidence_score: float = Field(..., ge=0, le=100)
#     blackbox_score: float = Field(..., ge=0, le=100)
#     judge_score: float = Field(..., ge=0, le=100)
#     whitebox_score: float = Field(..., ge=0, le=100)

# class FusionResponse(BaseModel):
#     truth_score: float
#     hallucination_probability: float
#     confidence_score: float
#     risk_level: str
#     component_scores: dict

# class WhiteBoxRequest(BaseModel):
#     text: str = Field(
#         ...,
#         min_length=1,
#         max_length=10000,
#         description="Text to analyze using White-Box UQ"
#     )


# class WhiteBoxResponse(BaseModel):
#     method: str
#     model: str
#     whitebox_score: float
#     minimum_token_confidence: float
#     token_count: int

# class RiskRequest(BaseModel):
#     truth_score: float = Field(..., ge=0, le=100)
#     hallucination_probability: float = Field(..., ge=0, le=100)
#     confidence_score: float = Field(..., ge=0, le=100)

# class RegenerationRequest(BaseModel):
#     question: str = Field(..., min_length=1, max_length=5000)
#     original_response: str = Field(..., min_length=1, max_length=10000)
#     verification_context: str = Field(
#         ...,
#         min_length=1,
#         max_length=20000
#     )


# class FinalVerificationRequest(BaseModel):
#     question: str = Field(..., min_length=1, max_length=5000)
#     response: str = Field(..., min_length=1, max_length=10000)

# class PipelineRequest(BaseModel):
#     question: str = Field(
#         ...,
#         min_length=1,
#         max_length=5000
#     )

# # ---------------------------------------------------------
# # Health Check
# # ---------------------------------------------------------

# @app.get("/health")
# def health_check():

#     return {
#         "status": "ok",
#         "service": "TruthGuard API"
#     }


# # ---------------------------------------------------------
# # Generate Response
# # ---------------------------------------------------------

# @app.post(
#     "/generate",
#     response_model=GenerateResponse
# )
# def generate(request: GenerateRequest):

#     try:

#         answer = generate_response(
#             request.question
#         )

#         return GenerateResponse(
#             question=request.question,
#             answer=answer
#         )

#     except ValueError as exc:

#         raise HTTPException(
#             status_code=400,
#             detail=str(exc)
#         )

#     except Exception as exc:

#         raise HTTPException(
#             status_code=500,
#             detail=str(exc)
#         )

    
# @app.post(
#     "/extract-claims",
#     response_model=ClaimExtractionResponse
# )
# def extract_response_claims(
#     request: ClaimExtractionRequest
# ):
#     try:
#         result = extract_claims(request.response)

#         return ClaimExtractionResponse(
#             claims=[
#                 claim.model_dump()
#                 for claim in result.claims
#             ]
#         )

#     except ValueError as exc:
#         raise HTTPException(
#             status_code=400,
#             detail=str(exc)
#         )

#     except Exception as exc:
#         raise HTTPException(
#             status_code=500,
#             detail=str(exc)
#         )

# @app.post(
#     "/blackbox",
#     response_model=BlackBoxResponse
# )
# def run_blackbox(
#     request: BlackBoxRequest
# ):

#     try:
#         result = blackbox_score(
#             request.question
#         )

#         return BlackBoxResponse(**result)

#     except ValueError as exc:
#         raise HTTPException(
#             status_code=400,
#             detail=str(exc)
#         )

#     except Exception as exc:
#         raise HTTPException(
#             status_code=500,
#             detail=str(exc)
#         )

# @app.post(
#     "/verify-claim",
#     response_model=EvidenceResponse
# )
# def verify_claim_endpoint(
#     request: EvidenceRequest
# ):

#     try:
#         result = verify_claim(
#             request.claim
#         )

#         return EvidenceResponse(**result)

#     except ValueError as exc:
#         raise HTTPException(
#             status_code=400,
#             detail=str(exc)
#         )

#     except Exception as exc:
#         raise HTTPException(
#             status_code=500,
#             detail=str(exc)
#         )

# @app.post(
#     "/judge",
#     response_model=JudgeResponse
# )
# def judge_endpoint(
#     request: JudgeRequest
# ):

#     try:

#         result = judge_claim(
#             claim=request.claim,
#             response=request.response
#         )

#         return JudgeResponse(**result)

#     except ValueError as exc:

#         raise HTTPException(
#             status_code=400,
#             detail=str(exc)
#         )

#     except Exception as exc:

#         raise HTTPException(
#             status_code=500,
#             detail=str(exc)
#         )


# @app.post("/fuse-scores")
# def fuse_scores_endpoint(request: FusionRequest):
#     try:
#         return calculate_truth_score(
#             evidence_score=request.evidence_score,
#             blackbox_score=request.blackbox_score,
#             judge_score=request.judge_score,
#             whitebox_score=request.whitebox_score,
#         )

#     except ValueError as exc:
#         raise HTTPException(
#             status_code=400,
#             detail=str(exc)
#         )

#     except Exception as exc:
#         raise HTTPException(
#             status_code=500,
#             detail=str(exc)
#         )

    
# @app.post("/whitebox")
# def whitebox_endpoint(request: WhiteBoxRequest):

#     try:

#         from backend.core.whitebox import (
#             calculate_whitebox_score
#         )

#         result = calculate_whitebox_score(
#             request.text
#         )

#         return result

#     except ValueError as exc:

#         raise HTTPException(
#             status_code=400,
#             detail=str(exc)
#         )

#     except Exception as exc:

#         raise HTTPException(
#             status_code=500,
#             detail=str(exc)
#         )

# @app.post("/risk-decision")
# def risk_decision_endpoint(request: RiskRequest):
#     try:
#         return make_risk_decision(
#             truth_score=request.truth_score,
#             hallucination_probability=request.hallucination_probability,
#             confidence_score=request.confidence_score,
#         )

#     except ValueError as exc:
#         raise HTTPException(
#             status_code=400,
#             detail=str(exc)
#         )

#     except Exception as exc:
#         raise HTTPException(
#             status_code=500,
#             detail=str(exc)
#         )

# @app.post("/regenerate")
# def regenerate_endpoint(request: RegenerationRequest):
#     try:
#         regenerated = regenerate_response(
#             question=request.question,
#             original_response=request.original_response,
#             verification_context=request.verification_context,
#         )

#         return {
#             "original_response": request.original_response,
#             "regenerated_response": regenerated,
#             "method": "TruthGuard Response Regeneration",
#         }

#     except ValueError as exc:
#         raise HTTPException(
#             status_code=400,
#             detail=str(exc)
#         )

#     except Exception as exc:
#         raise HTTPException(
#             status_code=500,
#             detail=str(exc)
#         )

# @app.post("/final-verify")
# def final_verify_endpoint(request: FinalVerificationRequest):
#     try:
#         return final_verify(
#             question=request.question,
#             response=request.response,
#         )

#     except ValueError as exc:
#         raise HTTPException(
#             status_code=400,
#             detail=str(exc)
#         )

#     except Exception as exc:
#         raise HTTPException(
#             status_code=500,
#             detail=str(exc)
#         )

# @app.post("/truthguard")
# def truthguard_endpoint(request: PipelineRequest):

#     try:
#         return run_truthguard(request.question)

#     except ValueError as exc:
#         raise HTTPException(
#             status_code=400,
#             detail=str(exc)
#         )

#     except Exception as exc:
#         raise HTTPException(
#             status_code=500,
#             detail=str(exc)
#         )


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.core.pipeline import run_truthguard


app = FastAPI(
    title="TruthGuard API",
    description="Adaptive LLM Hallucination Detection and Reduction Framework",
    version="1.0.0",
)


class VerifyRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {
        "message": "TruthGuard API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/verify")
def verify(request: VerifyRequest):

    try:

        result = run_truthguard(
            request.question
        )

        return result

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )