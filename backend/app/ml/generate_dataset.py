from pathlib import Path

import numpy as np
import pandas as pd

from app.ml.features import FEATURE_COLUMNS, TARGET_COLUMN


RANDOM_SEED = 42
NUMBER_OF_ROWS = 8000

OUTPUT_PATH = Path(
    "data/raw/parking_demand.csv"
)


def generate_dataset() -> pd.DataFrame:
    rng = np.random.default_rng(
        RANDOM_SEED
    )

    # ---------------------------------------------------------
    # Time features
    # ---------------------------------------------------------
    hour = rng.integers(
        0,
        24,
        NUMBER_OF_ROWS
    )

    day_of_week = rng.integers(
        0,
        7,
        NUMBER_OF_ROWS
    )

    weekend = (
        day_of_week >= 5
    ).astype(int)

    morning_peak = (
        (hour >= 7)
        & (hour <= 10)
    ).astype(int)

    evening_peak = (
        (hour >= 16)
        & (hour <= 19)
    ).astype(int)

    overnight = (
        (hour >= 0)
        & (hour <= 5)
    ).astype(int)

    # ---------------------------------------------------------
    # Parking-site characteristics
    #
    # These are varied rather than tied to fixed location IDs.
    # This allows the trained model to accept new parking sites
    # that have characteristics within the training range.
    # ---------------------------------------------------------
    total_spaces = rng.integers(
        10,
        151,
        NUMBER_OF_ROWS
    )

    parking_price = rng.uniform(
        1.50,
        7.50,
        NUMBER_OF_ROWS
    )

    parking_price = np.round(
        parking_price,
        2
    )

    # ---------------------------------------------------------
    # Environmental/context features
    # ---------------------------------------------------------
    traffic_level = rng.integers(
        0,
        4,
        NUMBER_OF_ROWS
    )

    weather = rng.integers(
        0,
        4,
        NUMBER_OF_ROWS
    )

    event_level = rng.integers(
        0,
        4,
        NUMBER_OF_ROWS
    )

    # ---------------------------------------------------------
    # Historical/current occupancy
    # ---------------------------------------------------------
    previous_occupancy = rng.uniform(
        5,
        95,
        NUMBER_OF_ROWS
    )

    current_occupancy = (
        0.72 * previous_occupancy
        + 5.0 * traffic_level
        + 4.0 * event_level
        + 5.0 * morning_peak
        + 7.0 * evening_peak
        - 8.0 * overnight
        - 2.0 * weekend
        + rng.normal(
            0,
            7,
            NUMBER_OF_ROWS
        )
    )

    current_occupancy = np.clip(
        current_occupancy,
        0,
        100
    )

    # ---------------------------------------------------------
    # Future parking demand target
    #
    # IMPORTANT:
    # The target is generated only from legitimate predictive
    # inputs plus random noise. No future/target-derived
    # availability feature is used.
    # ---------------------------------------------------------
    future_demand = (
        0.42 * current_occupancy
        + 0.23 * previous_occupancy
        + 5.5 * traffic_level
        + 5.0 * event_level
        + 6.5 * morning_peak
        + 8.5 * evening_peak
        + 1.5 * weather
        - 2.2 * parking_price
        - 0.025 * total_spaces
        - 3.0 * weekend
        - 6.0 * overnight
        + rng.normal(
            0,
            6,
            NUMBER_OF_ROWS
        )
    )

    occupancy_percentage = np.clip(
        future_demand,
        0,
        100
    )

    dataset = pd.DataFrame(
        {
            "hour": hour,
            "day_of_week": day_of_week,
            "previous_occupancy": np.round(
                previous_occupancy,
                2
            ),
            "current_occupancy": np.round(
                current_occupancy,
                2
            ),
            "traffic_level": traffic_level,
            "weather": weather,
            "event_level": event_level,
            "parking_price": parking_price,
            "total_spaces": total_spaces,
            TARGET_COLUMN: np.round(
                occupancy_percentage,
                2
            )
        }
    )

    expected_columns = (
        FEATURE_COLUMNS
        + [TARGET_COLUMN]
    )

    if list(dataset.columns) != expected_columns:
        raise RuntimeError(
            "Generated dataset columns do not match "
            "the SmartPark ML feature definition."
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    dataset.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(
        f"Dataset created successfully: "
        f"{OUTPUT_PATH}"
    )

    print(
        f"Rows: {len(dataset)}"
    )

    print(
        f"Features: {len(FEATURE_COLUMNS)}"
    )

    print(
        "Location-code feature present:",
        "parking_location"
        in dataset.columns
    )

    return dataset


if __name__ == "__main__":
    generate_dataset()
