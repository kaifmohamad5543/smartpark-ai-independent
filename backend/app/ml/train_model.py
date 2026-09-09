import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import (
    mean_absolute_error,
    r2_score,
    root_mean_squared_error,
)
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

from app.ml.features import FEATURE_COLUMNS, TARGET_COLUMN


RANDOM_SEED = 42

DATASET_PATH = Path(
    "data/raw/parking_demand.csv"
)

MODEL_PATH = Path(
    "app/ml/model/xgboost_parking_demand_v2.joblib"
)

METRICS_PATH = Path(
    "data/processed/xgboost_v2_metrics.json"
)

PREDICTIONS_PATH = Path(
    "data/processed/xgboost_v2_test_predictions.csv"
)


def train_model():
    print("Loading SmartPark AI ML Version 2 dataset...")

    dataset = pd.read_csv(
        DATASET_PATH
    )

    missing_columns = [
        column
        for column in FEATURE_COLUMNS + [TARGET_COLUMN]
        if column not in dataset.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Dataset is missing columns: {missing_columns}"
        )

    if "parking_location" in dataset.columns:
        raise ValueError(
            "Legacy parking_location feature must not be "
            "present in ML Version 2."
        )

    X = dataset[FEATURE_COLUMNS]
    y = dataset[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=RANDOM_SEED
        )
    )

    print(f"Total records: {len(dataset)}")
    print(f"Training records: {len(X_train)}")
    print(f"Testing records: {len(X_test)}")
    print(f"Feature count: {len(FEATURE_COLUMNS)}")

    model = XGBRegressor(
        objective="reg:squarederror",
        n_estimators=350,
        learning_rate=0.05,
        max_depth=5,
        min_child_weight=3,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_alpha=0.05,
        reg_lambda=1.0,
        random_state=RANDOM_SEED,
        n_jobs=-1
    )

    print("\nTraining XGBoost V2 baseline model...")

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    mae = float(
        mean_absolute_error(
            y_test,
            predictions
        )
    )

    rmse = float(
        root_mean_squared_error(
            y_test,
            predictions
        )
    )

    r2 = float(
        r2_score(
            y_test,
            predictions
        )
    )

    metrics = {
        "model_version": "2.0",
        "model": "XGBoost Regressor",
        "dataset_type": "synthetic",
        "random_seed": RANDOM_SEED,
        "total_records": len(dataset),
        "training_records": len(X_train),
        "testing_records": len(X_test),
        "feature_count": len(FEATURE_COLUMNS),
        "feature_columns": FEATURE_COLUMNS,
        "target_column": TARGET_COLUMN,
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "r2": round(r2, 4),
    }

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    METRICS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        {
            "model": model,
            "feature_columns": FEATURE_COLUMNS,
            "target_column": TARGET_COLUMN,
            "model_version": "2.0",
            "dataset_type": "synthetic",
        },
        MODEL_PATH
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

    prediction_results = X_test.copy()

    prediction_results[
        "actual_occupancy"
    ] = y_test.values

    prediction_results[
        "predicted_occupancy"
    ] = predictions

    prediction_results[
        "absolute_error"
    ] = (
        prediction_results["actual_occupancy"]
        - prediction_results["predicted_occupancy"]
    ).abs()

    prediction_results.to_csv(
        PREDICTIONS_PATH,
        index=False
    )

    print("\n===== XGBOOST V2 BASELINE RESULTS =====")
    print(f"MAE:  {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R²:   {r2:.4f}")

    print(f"\nModel saved: {MODEL_PATH}")
    print(f"Metrics saved: {METRICS_PATH}")
    print(f"Predictions saved: {PREDICTIONS_PATH}")

    return metrics


if __name__ == "__main__":
    train_model()
