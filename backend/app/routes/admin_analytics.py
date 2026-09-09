from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.admin_analytics import (
    AdminAnalyticsOverview,
    ParkingLocationPerformance,
    ReservationTrendItem,
    AIDemandAnalyticsResponse
)
from app.services.admin_analytics_service import (
    get_admin_analytics_overview,
    get_parking_location_performance,
    get_reservation_trends,
    get_ai_demand_analytics
)
from app.utils.dependencies import require_admin


router = APIRouter(
    prefix="/api/admin/analytics",
    tags=["Admin Analytics"]
)


@router.get(
    "/overview",
    response_model=AdminAnalyticsOverview
)
def analytics_overview(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return get_admin_analytics_overview(
        db=db
    )


@router.get(
    "/locations",
    response_model=list[ParkingLocationPerformance]
)
def location_performance(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return get_parking_location_performance(
        db=db
    )


@router.get(
    "/reservation-trends",
    response_model=list[ReservationTrendItem]
)
def reservation_trends(
    days: int = 7,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    if days < 1:
        days = 1

    if days > 90:
        days = 90

    return get_reservation_trends(
        db=db,
        days=days
    )


@router.get(
    "/ai-demand",
    response_model=AIDemandAnalyticsResponse
)
def ai_demand_analytics(
    limit: int = 20,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    limit = max(
        1,
        min(limit, 100)
    )

    return get_ai_demand_analytics(
        db=db,
        limit=limit
    )


from app.schemas.model_performance import (
    ModelPerformanceResponse
)
from app.services.model_performance_service import (
    get_model_performance
)


@router.get(
    "/model-performance",
    response_model=ModelPerformanceResponse
)
def model_performance(
    admin_user: User = Depends(require_admin)
):
    return get_model_performance()
