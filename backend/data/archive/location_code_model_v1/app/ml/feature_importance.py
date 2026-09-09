import json
from pathlib import Path

import joblib
import pandas as pd


MODEL_PATH = Path(
    "app/ml/model/xgboost_parking_demand_tuned.joblib"
)

JSON_OUTPUT_PATH = Path(
    "data/processed/feature_importance.json"
)

CSV_OUTPUT_PATH = Path(
    "data/processed/feature_importance.csv"
)


DISPLAY_NAMES = {
    "hour": "Hour of Day",
    "day_of_week": "Day of Week",
    "parking_location": "Parking Location",
    "previous_occupancy": "Previous Occupancy",
    "traffic_level": "Traffic Level",
    "weather": "Weather",
    "event_level": "Nearby Event Level",
    "parking_price": "Parking Price",
    "available_spaces": "Available Spaces"
}


def calculate_feature_importance():
    bundle = joblib.load(
        MODEL_PATH
    )

    model = bundle["model"]
    feature_columns = bundle[
        "feature_columns"
    ]

    raw_importance = (
        model.feature_importances_
    )

    total_importance = raw_importance.sum()

    results = []

    for feature, importance in zip(
        feature_columns,
        raw_importance
    ):
        percentage = (
            float(importance)
            / float(total_importance)
            * 100
            if total_importance > 0
            else 0
        )

        results.append(
            {
                "feature": feature,
                "display_name": DISPLAY_NAMES.get(
                    feature,
                    feature
                ),
                "importance": round(
                    float(importance),
                    6
                ),
                "importance_percentage": round(
                    percentage,
                    2
                )
            }
        )

    results.sort(
        key=lambda item: item[
            "importance_percentage"
        ],
        reverse=True
    )

    JSON_OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        JSON_OUTPUT_PATH,
        "w"
    ) as file:
        json.dump(
            results,
            file,
            indent=4
        )

    pd.DataFrame(
        results
    ).to_csv(
        CSV_OUTPUT_PATH,
        index=False
    )

    print(
        "\nXGBOOST FEATURE IMPORTANCE"
    )

    print(
        "---------------------------------------------"
    )

    for index, result in enumerate(
        results,
        start=1
    ):
        print(
            f"{index}. "
            f"{result['display_name']:<22} "
            f"{result['importance_percentage']:>6.2f}%"
        )

    print(
        "---------------------------------------------"
    )

    print(
        f"\nJSON saved: {JSON_OUTPUT_PATH}"
    )

    print(
        f"CSV saved: {CSV_OUTPUT_PATH}"
    )


if __name__ == "__main__":
    calculate_feature_importance()
