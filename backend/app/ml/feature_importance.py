import json
from pathlib import Path

import joblib
import pandas as pd

from app.ml.features import (
    FEATURE_COLUMNS,
    FEATURE_LABELS,
)


MODEL_PATH = Path(
    "app/ml/model/xgboost_parking_demand_v2_tuned.joblib"
)

JSON_OUTPUT_PATH = Path(
    "data/processed/feature_importance_v2.json"
)

CSV_OUTPUT_PATH = Path(
    "data/processed/feature_importance_v2.csv"
)


def calculate_feature_importance():
    bundle = joblib.load(
        MODEL_PATH
    )

    model = bundle["model"]

    feature_columns = bundle[
        "feature_columns"
    ]

    if feature_columns != FEATURE_COLUMNS:
        raise ValueError(
            "Loaded model feature columns do not match "
            "SmartPark AI ML Version 2."
        )

    raw_importance = (
        model.feature_importances_
    )

    total_importance = float(
        raw_importance.sum()
    )

    results = []

    for feature, importance in zip(
        feature_columns,
        raw_importance
    ):
        importance = float(
            importance
        )

        percentage = (
            importance
            / total_importance
            * 100
            if total_importance > 0
            else 0.0
        )

        results.append(
            {
                "feature": feature,
                "display_name": FEATURE_LABELS.get(
                    feature,
                    feature
                ),
                "importance": round(
                    importance,
                    6
                ),
                "importance_percentage": round(
                    percentage,
                    2
                ),
            }
        )

    results.sort(
        key=lambda item:
            item["importance_percentage"],
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
            {
                "model_version": bundle.get(
                    "model_version",
                    "2.0-tuned"
                ),
                "dataset_type": bundle.get(
                    "dataset_type",
                    "synthetic"
                ),
                "importance_method":
                    "XGBoost model-native feature importance",
                "features": results,
            },
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
        "\n===== XGBOOST V2 FEATURE IMPORTANCE ====="
    )

    for index, result in enumerate(
        results,
        start=1
    ):
        print(
            f"{index}. "
            f"{result['display_name']:<24} "
            f"{result['importance_percentage']:>6.2f}%"
        )

    print(
        "\nLegacy parking_location present:",
        any(
            result["feature"] == "parking_location"
            for result in results
        )
    )

    print(
        "Legacy available_spaces present:",
        any(
            result["feature"] == "available_spaces"
            for result in results
        )
    )

    print(
        f"\nJSON saved: {JSON_OUTPUT_PATH}"
    )

    print(
        f"CSV saved: {CSV_OUTPUT_PATH}"
    )

    return results


if __name__ == "__main__":
    calculate_feature_importance()
