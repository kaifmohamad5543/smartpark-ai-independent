from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.external_parking_bay import (
    ExternalParkingBay,
)
from app.schemas.open_data import (
    ExternalParkingBayResponse,
    ExternalParkingBayStatsResponse,
)


router = APIRouter(
    prefix="/api/open-data",
    tags=["London Open Data"],
)


@router.get(
    "/parking-bays/stats",
    response_model=ExternalParkingBayStatsResponse,
)
def parking_bay_statistics(
    db: Session = Depends(get_db),
):
    total_records = db.scalar(
        select(func.count())
        .select_from(ExternalParkingBay)
    ) or 0

    declared_spaces = db.scalar(
        select(
            func.coalesce(
                func.sum(
                    ExternalParkingBay.parking_spaces
                ),
                0,
            )
        )
    ) or 0

    distinct_roads = db.scalar(
        select(
            func.count(
                func.distinct(
                    ExternalParkingBay.road_name
                )
            )
        )
    ) or 0

    paid_for = db.scalar(
        select(func.count())
        .select_from(ExternalParkingBay)
        .where(
            ExternalParkingBay.restriction_type
            == "paid-for"
        )
    ) or 0

    ev_charging = db.scalar(
        select(func.count())
        .select_from(ExternalParkingBay)
        .where(
            ExternalParkingBay.restriction_type
            == "electric vehicle recharging"
        )
    ) or 0

    disabled = db.scalar(
        select(func.count())
        .select_from(ExternalParkingBay)
        .where(
            ExternalParkingBay.restriction_type.ilike(
                "disabled%"
            )
        )
    ) or 0

    return {
        "total_records": total_records,
        "declared_parking_spaces":
            int(declared_spaces),
        "distinct_roads": distinct_roads,
        "paid_for_records": paid_for,
        "ev_charging_records": ev_charging,
        "disabled_bay_records": disabled,
        "source_dataset":
            "Camden Parking Bays",
        "source_organisation":
            "London Borough of Camden",
        "data_type":
            "Genuine public parking infrastructure data",
    }


@router.get(
    "/parking-bays",
    response_model=list[
        ExternalParkingBayResponse
    ],
)
def list_external_parking_bays(
    road_name: str | None = Query(
        default=None,
        max_length=150,
    ),
    postcode: str | None = Query(
        default=None,
        max_length=20,
    ),
    restriction_type: str | None = Query(
        default=None,
        max_length=150,
    ),
    min_lat: float | None = Query(
        default=None,
        ge=-90,
        le=90,
    ),
    max_lat: float | None = Query(
        default=None,
        ge=-90,
        le=90,
    ),
    min_lon: float | None = Query(
        default=None,
        ge=-180,
        le=180,
    ),
    max_lon: float | None = Query(
        default=None,
        ge=-180,
        le=180,
    ),
    limit: int = Query(
        default=200,
        ge=1,
        le=500,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    db: Session = Depends(get_db),
):
    query = select(
        ExternalParkingBay
    )

    if road_name:
        query = query.where(
            ExternalParkingBay.road_name.ilike(
                f"%{road_name}%"
            )
        )

    if postcode:
        query = query.where(
            ExternalParkingBay.postcode.ilike(
                f"{postcode}%"
            )
        )

    if restriction_type:
        query = query.where(
            ExternalParkingBay.restriction_type
            == restriction_type
        )

    if min_lat is not None:
        query = query.where(
            ExternalParkingBay.latitude
            >= min_lat
        )

    if max_lat is not None:
        query = query.where(
            ExternalParkingBay.latitude
            <= max_lat
        )

    if min_lon is not None:
        query = query.where(
            ExternalParkingBay.longitude
            >= min_lon
        )

    if max_lon is not None:
        query = query.where(
            ExternalParkingBay.longitude
            <= max_lon
        )

    query = (
        query
        .order_by(
            ExternalParkingBay.road_name,
            ExternalParkingBay.source_identifier,
        )
        .offset(offset)
        .limit(limit)
    )

    return db.scalars(
        query
    ).all()


@router.get(
    "/parking-bays/{source_identifier}",
    response_model=ExternalParkingBayResponse,
)
def get_external_parking_bay(
    source_identifier: str,
    db: Session = Depends(get_db),
):
    parking_bay = db.scalar(
        select(
            ExternalParkingBay
        ).where(
            ExternalParkingBay.source_identifier
            == source_identifier
        )
    )

    if parking_bay is None:
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail=(
                "External parking bay "
                "not found."
            ),
        )

    return parking_bay
