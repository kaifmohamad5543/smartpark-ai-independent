import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_absolute_error,
    r2_score,
    root_mean_squared_error,
)

from app.ml.features import FEATURE_COLUMNS, TARGET_COLUMN


MODEL_PATH = Path(
    "app/ml/model/xgboost_parking_demand_v2_tuned.joblib"
)

EVALUATION_PATH = Path(
    "data/evaluation/parking_demand_evaluation_v2.csv"
)

METRICS_PATH = Path(
    "data/processed/xgboost_v2_evaluation_metrics.json"
)

PREDICTIONS_PATH = Path(
    "data/processed/xgboost_v2_evaluation_predictions.csv"
)


def evaluate_model():
    print("Loading tuned SmartPark AI XGBoost V2 model...")

    bundle = joblib.load(
        MODEL_PATH
    )

    model = bundle["model"]

    model_features = bundle[
        "feature_columns"
    ]

    if model_features != FEATURE_COLUMNS:
        raise ValueError(
            "Model feature definition does not match "
            "current ML Version 2 features."
        )

    dataset = pd.read_csv(
        EVALUATION_PATH
    )

    if "parking_location" in dataset.columns:
        raise ValueError(
            "Legacy parking_location feature detected."
        )

    X = dataset[FEATURE_COLUMNS]
    y = dataset[TARGET_COLUMN]

    predictions = model.predict(
        X
    )

    predictions = np.clip(
        predictions,
        0,
        100
    )

    mae = float(
        mean_absolute_error(
            y,
            predictions
        )
    )

    rmse = float(
        root_mean_squared_error(
            y,
            predictions
        )
    )

    r2 = float(
        r2_score(
            y,
            predictions
        )
    )

    absolute_errors = np.abs(
        y.to_numpy() - predictions
    )

    metrics = {
        "model_version": "2.0-tuned",
        "model": "XGBoost Regressor",
        "dataset_type": "synthetic",
        "evaluation_seed": 2026,
        "evaluation_records": len(dataset),
        "feature_count": len(FEATURE_COLUMNS),
        "feature_columns": FEATURE_COLUMNS,
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "r2": round(r2, 4),
        "median_absolute_error": round(
            float(np.median(absolute_errors)),
            4
        ),
        "p90_absolute_error": round(
            float(np.percentile(
                absolute_errors,
                90
            )),
            4
        ),
    }

    METRICS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        METRICS_PATH,
        "w"
    ) as file:
        json.dump(
            metrics,
            file,
            indent=4
        )

    output = X.copy()

    output["actual_occupancy"] = (
        y.values
    )

    output["predicted_occupancy"] = (
        predictions
    )

    output["absolute_error"] = (
        absolute_errors
    )

    output.to_csv(
        PREDICTIONS_PATH,
        index=False
    )

    print(
        "\n===== XGBOOST V2 SYNTHETIC "
        "EVALUATION RESULTS ====="
    )

    print(f"Evaluation records: {len(dataset)}")
    print(f"MAE:  {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R²:   {r2:.4f}")

    print(
        "Median absolute error: "
        f"{np.median(absolute_errors):.4f}"
    )

    print(
        "90th percentile absolute error: "
        f"{np.percentile(absolute_errors, 90):.4f}"
    )

    print(
        f"\nMetrics saved: {METRICS_PATH}"
    )

    print(
        f"Predictions saved: {PREDICTIONS_PATH}"
    )


if __name__ == "__main__":
    evaluate_model()
