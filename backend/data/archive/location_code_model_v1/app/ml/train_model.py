import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_absolute_error,
    r2_score,
    root_mean_squared_error
)
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor


RANDOM_SEED = 42

DATASET_PATH = Path(
    "data/raw/parking_demand.csv"
)

MODEL_PATH = Path(
    "app/ml/model/xgboost_parking_demand.joblib"
)

METRICS_PATH = Path(
    "data/processed/xgboost_metrics.json"
)

PREDICTIONS_PATH = Path(
    "data/processed/xgboost_test_predictions.csv"
)


FEATURE_COLUMNS = [
    "hour",
    "day_of_week",
    "parking_location",
    "previous_occupancy",
    "traffic_level",
    "weather",
    "event_level",
    "parking_price",
    "available_spaces"
]

TARGET_COLUMN = "occupancy_percentage"


def train_model():
    print("Loading SmartPark AI parking dataset...")

    dataset = pd.read_csv(
        DATASET_PATH
    )

    X = dataset[FEATURE_COLUMNS]
    y = dataset[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=RANDOM_SEED
    )

    print(
        f"Training records: {len(X_train)}"
    )
    print(
        f"Testing records: {len(X_test)}"
    )

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

    print("\nTraining XGBoost model...")

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    # Parking occupancy cannot physically
    # be below 0% or above 100%.
    predictions = np.clip(
        predictions,
        0,
        100
    )

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = root_mean_squared_error(
        y_test,
        predictions
    )

    r2 = r2_score(
        y_test,
        predictions
    )

    metrics = {
        "model": "XGBoost Regression",
        "dataset_rows": int(len(dataset)),
        "training_rows": int(len(X_train)),
        "testing_rows": int(len(X_test)),
        "test_size": 0.20,
        "random_seed": RANDOM_SEED,
        "mae": round(float(mae), 4),
        "rmse": round(float(rmse), 4),
        "r2": round(float(r2), 4)
    }

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    METRICS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    model_bundle = {
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "target_column": TARGET_COLUMN,
        "model_name": "XGBoost Regression",
        "version": "1.0"
    }

    joblib.dump(
        model_bundle,
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

    results = X_test.copy()

    results["actual_occupancy"] = (
        y_test.values
    )

    results["predicted_occupancy"] = (
        np.round(
            predictions,
            2
        )
    )

    results["absolute_error"] = np.round(
        np.abs(
            results["actual_occupancy"]
            - results["predicted_occupancy"]
        ),
        2
    )

    results.to_csv(
        PREDICTIONS_PATH,
        index=False
    )

    print("\nMODEL EVALUATION")
    print("---------------------------")
    print(
        f"MAE:  {metrics['mae']}"
    )
    print(
        f"RMSE: {metrics['rmse']}"
    )
    print(
        f"R²:   {metrics['r2']}"
    )

    print("\nFiles saved:")
    print(
        f"Model: {MODEL_PATH}"
    )
    print(
        f"Metrics: {METRICS_PATH}"
    )
    print(
        f"Predictions: {PREDICTIONS_PATH}"
    )

    print(
        "\nXGBoost training completed successfully."
    )


if __name__ == "__main__":
    train_model()
