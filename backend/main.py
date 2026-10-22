# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel

# from backend.core.pipeline import run_truthguard


# app = FastAPI(
#     title="TruthGuard API",
#     description="Adaptive LLM Hallucination Detection and Reduction Framework",
#     version="1.0.0",
# )


# class VerifyRequest(BaseModel):
#     question: str


# @app.get("/")
# def root():
#     return {
#         "message": "TruthGuard API is running"
#     }


# @app.get("/health")
# def health():
#     return {
#         "status": "healthy"
#     }


# @app.post("/verify")
# def verify(request: VerifyRequest):

#     try:

#         result = run_truthguard(
#             request.question
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


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.core.pipeline import run_truthguard


app = FastAPI(
    title="TruthGuard API",
    description="Adaptive LLM Hallucination Detection and Reduction Framework",
    version="1.0.0",
)


class VerifyRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Question to generate and verify")


@app.get("/")
def root():
    return {"message": "TruthGuard API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/verify")
def verify(request: VerifyRequest):
    try:
        return run_truthguard(request.question)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        # Avoid exposing internal stack traces to API clients.
        raise HTTPException(
            status_code=500,
            detail=f"TruthGuard verification failed: {exc}",
        ) from exc
