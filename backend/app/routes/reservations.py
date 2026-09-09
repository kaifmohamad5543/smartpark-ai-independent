import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.reservation import (
    CheckInRequest,
    CheckInResponse,
    CheckOutRequest,
    CheckOutResponse,
    ReservationCancelResponse,
    ReservationCreate,
    ReservationResponse
)
from app.services.reservation_service import (
    cancel_reservation,
    create_reservation,
    get_user_reservation_by_id,
    get_user_reservations
)
from app.services.payment_service import get_payment_by_reservation
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/reservations",
    tags=["Reservations"]
)


@router.post(
    "",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED
)
def make_reservation(
    reservation_data: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return create_reservation(
            db=db,
            user_id=current_user.id,
            reservation_data=reservation_data
        )

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@router.get(
    "",
    response_model=list[ReservationResponse]
)
def list_my_reservations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_reservations(
        db=db,
        user_id=current_user.id
    )


@router.patch(
    "/{reservation_id}/cancel",
    response_model=ReservationCancelResponse
)
def cancel_my_reservation(
    reservation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reservation = get_user_reservation_by_id(
        db=db,
        user_id=current_user.id,
        reservation_id=reservation_id
    )

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found."
        )

    try:
        return cancel_reservation(
            db=db,
            reservation=reservation
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@router.post(
    "/check-in",
    response_model=CheckInResponse
)
def check_in(
    check_in_data: CheckInRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.services.reservation_service import (
        check_in_reservation,
        get_user_reservation_by_booking_code
    )

    reservation = get_user_reservation_by_booking_code(
        db=db,
        user_id=current_user.id,
        booking_code=check_in_data.booking_code
    )

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid booking code."
        )

    try:
        reservation = check_in_reservation(
            db=db,
            reservation=reservation
        )

        return CheckInResponse(
            reservation_id=reservation.id,
            booking_code=reservation.booking_code,
            parking_space_id=reservation.parking_space_id,
            status=reservation.status,
            checked_in_at=reservation.checked_in_at
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@router.post(
    "/{reservation_id}/check-out",
    response_model=CheckOutResponse
)
def check_out(
    reservation_id: uuid.UUID,
    checkout_data: CheckOutRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.services.reservation_service import check_out_reservation

    reservation = get_user_reservation_by_id(
        db=db,
        user_id=current_user.id,
        reservation_id=reservation_id
    )

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found."
        )

    try:
        payment_method = (
            checkout_data.payment_method
            if checkout_data
            else "card"
        )

        reservation = check_out_reservation(
            db=db,
            reservation=reservation,
            payment_method=payment_method
        )

        payment = get_payment_by_reservation(
            db=db,
            reservation_id=reservation.id
        )

        return CheckOutResponse(
            reservation_id=reservation.id,
            booking_code=reservation.booking_code,
            status=reservation.status,
            checked_in_at=reservation.checked_in_at,
            checked_out_at=reservation.checked_out_at,
            final_cost=reservation.final_cost,
            payment_method=payment.payment_method,
            payment_reference=payment.payment_reference
        )

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
