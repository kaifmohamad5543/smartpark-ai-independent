from datetime import (
    datetime,
    timezone,
)
from decimal import Decimal

from app.services.pricing_service import (
    calculate_dynamic_hourly_rate,
    calculate_estimated_cost,
)


def test_existing_cost_calculation_is_preserved():
    start = datetime(
        2026,
        8,
        29,
        10,
        0,
        tzinfo=timezone.utc,
    )

    end = datetime(
        2026,
        8,
        29,
        12,
        0,
        tzinfo=timezone.utc,
    )

    result = (
        calculate_estimated_cost(
            reserved_from=start,
            reserved_until=end,
            hourly_rate=Decimal(
                "4.50"
            ),
        )
    )

    assert result == Decimal(
        "9.00"
    )


def test_neutral_demand_keeps_base_rate():
    booking_time = datetime(
        2026,
        8,
        29,
        12,
        0,
        tzinfo=timezone.utc,
    )

    result = (
        calculate_dynamic_hourly_rate(
            base_hourly_rate=Decimal(
                "4.00"
            ),
            reserved_from=booking_time,
            current_occupancy=50,
            predicted_occupancy=50,
        )
    )

    assert (
        result[
            "pricing_multiplier"
        ]
        == Decimal("1.0000")
    )

    assert (
        result[
            "applied_hourly_rate"
        ]
        == Decimal("4.00")
    )


def test_high_demand_peak_period_increases_price():
    # 08:00 UTC is 09:00 London
    # during British Summer Time.
    booking_time = datetime(
        2026,
        8,
        28,
        8,
        0,
        tzinfo=timezone.utc,
    )

    result = (
        calculate_dynamic_hourly_rate(
            base_hourly_rate=Decimal(
                "4.00"
            ),
            reserved_from=booking_time,
            current_occupancy=90,
            predicted_occupancy=95,
        )
    )

    assert (
        result[
            "pricing_multiplier"
        ] > Decimal("1.00")
    )

    assert (
        result[
            "applied_hourly_rate"
        ] > Decimal("4.00")
    )


def test_low_demand_reduces_price():
    booking_time = datetime(
        2026,
        8,
        29,
        12,
        0,
        tzinfo=timezone.utc,
    )

    result = (
        calculate_dynamic_hourly_rate(
            base_hourly_rate=Decimal(
                "4.00"
            ),
            reserved_from=booking_time,
            current_occupancy=10,
            predicted_occupancy=15,
        )
    )

    assert (
        result[
            "pricing_multiplier"
        ] < Decimal("1.00")
    )

    assert (
        result[
            "applied_hourly_rate"
        ] < Decimal("4.00")
    )


def test_dynamic_price_has_safe_lower_bound():
    booking_time = datetime(
        2026,
        8,
        29,
        2,
        0,
        tzinfo=timezone.utc,
    )

    result = (
        calculate_dynamic_hourly_rate(
            base_hourly_rate=Decimal(
                "4.00"
            ),
            reserved_from=booking_time,
            current_occupancy=0,
            predicted_occupancy=0,
        )
    )

    assert (
        result[
            "pricing_multiplier"
        ]
        == Decimal("0.7500")
    )

    assert (
        result[
            "applied_hourly_rate"
        ]
        == Decimal("3.00")
    )
