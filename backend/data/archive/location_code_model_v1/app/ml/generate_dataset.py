from pathlib import Path

import numpy as np
import pandas as pd


RANDOM_SEED = 42
NUMBER_OF_ROWS = 5000

OUTPUT_PATH = Path("data/raw/parking_demand.csv")


def generate_dataset():
    rng = np.random.default_rng(RANDOM_SEED)

    hour = rng.integers(0, 24, NUMBER_OF_ROWS)
    day_of_week = rng.integers(0, 7, NUMBER_OF_ROWS)

    parking_location = rng.integers(
        0,
        3,
        NUMBER_OF_ROWS
    )

    previous_occupancy = rng.uniform(
        5,
        95,
        NUMBER_OF_ROWS
    )

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

    parking_price = np.select(
        [
            parking_location == 0,
            parking_location == 1,
            parking_location == 2
        ],
        [
            4.50,
            3.20,
            5.00
        ]
    )

    total_spaces = np.select(
        [
            parking_location == 0,
            parking_location == 1,
            parking_location == 2
        ],
        [
            40,
            55,
            35
        ]
    )

    current_occupied_spaces = np.rint(
        (previous_occupancy / 100)
        * total_spaces
    ).astype(int)

    available_spaces = (
        total_spaces - current_occupied_spaces
    )

    morning_peak = (
        (hour >= 7) &
        (hour <= 10)
    ).astype(int)

    evening_peak = (
        (hour >= 16) &
        (hour <= 19)
    ).astype(int)

    weekend = (
        day_of_week >= 5
    ).astype(int)

    future_demand = (
        0.55 * previous_occupancy
        + 6.0 * traffic_level
        + 5.5 * event_level
        + 8.0 * morning_peak
        + 10.0 * evening_peak
        + 2.0 * weather
        + 2.5 * parking_location
        - 2.0 * parking_price
        - 0.12 * available_spaces
        - 3.0 * weekend
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
            "parking_location": parking_location,
            "previous_occupancy": np.round(
                previous_occupancy,
                2
            ),
            "traffic_level": traffic_level,
            "weather": weather,
            "event_level": event_level,
            "parking_price": parking_price,
            "available_spaces": available_spaces,
            "occupancy_percentage": np.round(
                occupancy_percentage,
                2
            )
        }
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
        f"Dataset created successfully: {OUTPUT_PATH}"
    )
    print(
        f"Rows: {len(dataset)}"
    )
    print(
        f"Columns: {len(dataset.columns)}"
    )

    print("\nMissing values:")
    print(dataset.isnull().sum())

    print("\nFirst five rows:")
    print(dataset.head())

    print("\nTarget summary:")
    print(
        dataset[
            "occupancy_percentage"
        ].describe()
    )


if __name__ == "__main__":
    generate_dataset()
