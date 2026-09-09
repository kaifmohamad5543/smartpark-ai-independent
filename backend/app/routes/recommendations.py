from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse
)
from app.services.recommendation_service import (
    generate_recommendations
)
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/recommendations",
    tags=["Parking Recommendations"]
)


@router.post(
    "",
    response_model=RecommendationResponse
)
def recommend_parking(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recommendations = generate_recommendations(
        db=db,
        request=request
    )

    return RecommendationResponse(
        destination_latitude=(
            request.destination_latitude
        ),
        destination_longitude=(
            request.destination_longitude
        ),
        preference_mode=request.preference_mode,
        recommendations=recommendations
    )
