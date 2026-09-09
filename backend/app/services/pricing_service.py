from datetime import datetime
from decimal import (
    Decimal,
    ROUND_HALF_UP,
)
from zoneinfo import ZoneInfo


LONDON_TIMEZONE = ZoneInfo(
    "Europe/London"
)

MIN_PRICING_MULTIPLIER = Decimal(
    "0.75"
)

MAX_PRICING_MULTIPLIER = Decimal(
    "1.50"
)


def money(value) -> Decimal:
    return Decimal(
        str(value)
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


def decimal4(value) -> Decimal:
    return Decimal(
        str(value)
    ).quantize(
        Decimal("0.0001"),
        rounding=ROUND_HALF_UP,
    )


def clamp_percentage(
    value,
) -> Decimal:
    percentage = Decimal(
        str(value)
    )

    return min(
        Decimal("100"),
        max(
            Decimal("0"),
            percentage,
        ),
    )


def calculate_estimated_cost(
    reserved_from: datetime,
    reserved_until: datetime,
    hourly_rate,
) -> Decimal:
    duration_seconds = (
        reserved_until
        - reserved_from
    ).total_seconds()

    duration_hours = Decimal(
        str(
            duration_seconds
            / 3600
        )
    )

    rate = Decimal(
        str(hourly_rate)
    )

    cost = (
        duration_hours
        * rate
    )

    return cost.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


def calculate_time_adjustment(
    reserved_from: datetime,
) -> Decimal:
    """
    Time-of-day adjustment.

    Weekday peak:
        07:00–09:59
        16:00–18:59
        +15%

    Overnight:
        00:00–05:59
        -5%

    Other periods:
        no adjustment
    """

    local_time = (
        reserved_from
        .astimezone(
            LONDON_TIMEZONE
        )
    )

    hour = local_time.hour
    weekday = (
        local_time.weekday()
    )

    is_weekday = (
        weekday < 5
    )

    is_peak = (
        is_weekday
        and (
            7 <= hour < 10
            or 16 <= hour < 19
        )
    )

    if is_peak:
        return Decimal(
            "0.15"
        )

    if 0 <= hour < 6:
        return Decimal(
            "-0.05"
        )

    return Decimal("0")


def calculate_demand_adjustment(
    occupancy,
    maximum_adjustment,
) -> Decimal:
    """
    Occupancy of 50% is neutral.

    Values below 50% reduce the
    multiplier.

    Values above 50% increase the
    multiplier.
    """

    occupancy = (
        clamp_percentage(
            occupancy
        )
    )

    maximum_adjustment = Decimal(
        str(
            maximum_adjustment
        )
    )

    centred_demand = (
        occupancy
        - Decimal("50")
    ) / Decimal("50")

    return (
        centred_demand
        * maximum_adjustment
    )


def calculate_dynamic_hourly_rate(
    *,
    base_hourly_rate,
    reserved_from: datetime,
    current_occupancy,
    predicted_occupancy,
) -> dict:
    """
    Produce a transparent dynamic
    parking price.

    Components:
    - parking location base rate
    - time-of-day adjustment
    - current occupancy adjustment
    - AI-predicted occupancy adjustment

    The final multiplier is bounded
    between 0.75 and 1.50.
    """

    base_rate = money(
        base_hourly_rate
    )

    time_adjustment = (
        calculate_time_adjustment(
            reserved_from
        )
    )

    current_adjustment = (
        calculate_demand_adjustment(
            current_occupancy,
            Decimal("0.15"),
        )
    )

    predicted_adjustment = (
        calculate_demand_adjustment(
            predicted_occupancy,
            Decimal("0.20"),
        )
    )

    raw_multiplier = (
        Decimal("1")
        + time_adjustment
        + current_adjustment
        + predicted_adjustment
    )

    multiplier = min(
        MAX_PRICING_MULTIPLIER,
        max(
            MIN_PRICING_MULTIPLIER,
            raw_multiplier,
        ),
    )

    applied_rate = money(
        base_rate
        * multiplier
    )

    return {
        "base_hourly_rate":
            base_rate,

        "applied_hourly_rate":
            applied_rate,

        "pricing_multiplier":
            decimal4(
                multiplier
            ),

        "time_adjustment":
            decimal4(
                time_adjustment
            ),

        "current_demand_adjustment":
            decimal4(
                current_adjustment
            ),

        "predicted_demand_adjustment":
            decimal4(
                predicted_adjustment
            ),

        "current_occupancy":
            decimal4(
                clamp_percentage(
                    current_occupancy
                )
            ),

        "predicted_occupancy":
            decimal4(
                clamp_percentage(
                    predicted_occupancy
                )
            ),
    }
