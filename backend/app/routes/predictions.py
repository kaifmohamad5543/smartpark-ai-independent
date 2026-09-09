from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.prediction import (
    FeatureImportanceResponse,
    PredictionCreate,
    PredictionResponse
)
from app.services.prediction_service import (
    create_prediction,
    get_feature_importance,
    get_user_predictions
)
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/predictions",
    tags=["AI Predictions"]
)


@router.post(
    "",
    response_model=PredictionResponse,
    status_code=status.HTTP_201_CREATED
)
def predict_parking_demand(
    prediction_data: PredictionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return create_prediction(
            db=db,
            user_id=current_user.id,
            prediction_data=prediction_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@router.get(
    "",
    response_model=list[PredictionResponse]
)
def prediction_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_predictions(
        db=db,
        user_id=current_user.id
    )


@router.get(
    "/feature-importance",
    response_model=FeatureImportanceResponse
)
def feature_importance(
    current_user: User = Depends(get_current_user)
):
    try:
        features = get_feature_importance()

        return FeatureImportanceResponse(
            model_name="SmartPark XGBoost V2 Tuned",
            explanation_type="Global Model-Native Feature Importance",
            features=features
        )

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )
