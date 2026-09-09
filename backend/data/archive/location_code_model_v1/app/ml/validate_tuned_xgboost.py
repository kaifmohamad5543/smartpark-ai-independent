import json
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.model_selection import KFold, cross_validate
from xgboost import XGBRegressor


RANDOM_SEED = 42

DATASET_PATH = Path(
    "data/raw/parking_demand.csv"
)

OUTPUT_PATH = Path(
    "data/processed/tuned_xgboost_cross_validation.json"
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


def validate():
    print("Loading SmartPark AI dataset...")

    dataset = pd.read_csv(
        DATASET_PATH
    )

    X = dataset[FEATURE_COLUMNS]
    y = dataset[TARGET_COLUMN]

    model = XGBRegressor(
        objective="reg:squarederror",
        subsample=0.8,
        reg_lambda=3.0,
        reg_alpha=0.01,
        n_estimators=500,
        min_child_weight=7,
        max_depth=2,
        learning_rate=0.1,
        colsample_bytree=0.8,
        random_state=RANDOM_SEED,
        n_jobs=1
    )

    cv = KFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_SEED
    )

    print(
        "Running 5-fold validation of tuned XGBoost..."
    )

    scores = cross_validate(
        model,
        X,
        y,
        cv=cv,
        scoring={
            "mae": "neg_mean_absolute_error",
            "rmse": "neg_root_mean_squared_error",
            "r2": "r2"
        },
        n_jobs=-1
    )

    mae = -scores["test_mae"]
    rmse = -scores["test_rmse"]
    r2 = scores["test_r2"]

    results = {
        "model": "Tuned XGBoost Regression",
        "folds": 5,

        "mean_mae": round(
            float(np.mean(mae)),
            4
        ),

        "std_mae": round(
            float(np.std(mae)),
            4
        ),

        "mean_rmse": round(
            float(np.mean(rmse)),
            4
        ),

        "std_rmse": round(
            float(np.std(rmse)),
            4
        ),

        "mean_r2": round(
            float(np.mean(r2)),
            4
        ),

        "std_r2": round(
            float(np.std(r2)),
            4
        )
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_PATH,
        "w"
    ) as file:
        json.dump(
            results,
            file,
            indent=4
        )

    print(
        "\nTUNED XGBOOST 5-FOLD VALIDATION"
    )

    print("-----------------------------")

    print(
        f"MAE:  {results['mean_mae']} "
        f"± {results['std_mae']}"
    )

    print(
        f"RMSE: {results['mean_rmse']} "
        f"± {results['std_rmse']}"
    )

    print(
        f"R²:   {results['mean_r2']} "
        f"± {results['std_r2']}"
    )

    print(
        f"\nResults saved: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    validate()
