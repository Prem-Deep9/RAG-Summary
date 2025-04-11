"""
Patient router module for handling patient summary endpoints.

This module provides API routes for retrieving AI-generated patient summaries,
including authentication and authorization handling.
"""

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.data.patient_submissions import get_ai_tags
from app.dependencies.core import DBSessionDep
from app.dependencies.security import TokenValidator
from app.schemas.frameworks import SummaryResponse
from app.services.summary import get_patient_summary

security = HTTPBearer()

router = APIRouter(
    prefix="/patient/summary",
    tags=["patient summary"],
    responses={
        404: {"description": "Not found"},
        401: {"description": "Invalid or expired token"},
        403: {"description": "Forbidden - insufficient permissions"},
    },
)


async def get_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Validate and extract payload from JWT token."""
    try:
        return await TokenValidator().validate_token(credentials.credentials)
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Token has expired") from exc
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Authentication failed: {str(e)}"
        ) from e


@router.get("/{patient_id}", response_model=SummaryResponse)
async def get_summary(
    patient_id: str,
    db_session: DBSessionDep,
    token_payload: dict = Depends(get_token_payload),
):
    """
    Fetch the AI generated summary of a specific patient.
    Requires valid JWT token in Authorization header.

    Args:
        patient_id: The unique identifier of the patient
        db_session: Database session dependency
        token_payload: Validated JWT token payload

    Returns:
        SummaryResponse: The AI-generated patient summary

    Raises:
        HTTPException:
            - 401 if authentication fails
            - 404 if patient not found
    """
    summary = await get_patient_summary(db_session, patient_id)
    if not summary:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")

    ai_tags = await get_ai_tags(db_session, patient_id)

    return {"summary": summary, "ai_tags": ai_tags}
