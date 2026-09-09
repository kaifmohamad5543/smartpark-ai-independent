import json
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.ensemble import (
    GradientBoostingRegressor,
    RandomForestRegressor
)
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_validate

from xgboost import XGBRegressor


RANDOM_SEED = 42

DATASET_PATH = Path(
    "data/raw/parking_demand.csv"
)

JSON_OUTPUT_PATH = Path(
    "data/processed/cross_validation_results.json"
)

CSV_OUTPUT_PATH = Path(
    "data/processed/cross_validation_results.csv"
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


def cross_validate_model(
    model_name,
    model,
    X,
    y,
    cross_validator
):
    print(
        f"\nCross-validating {model_name}..."
    )

    scores = cross_validate(
        model,
        X,
        y,
        cv=cross_validator,
        scoring={
            "mae": "neg_mean_absolute_error",
            "rmse": "neg_root_mean_squared_error",
            "r2": "r2"
        },
        n_jobs=-1
    )

    mae_scores = -scores["test_mae"]
    rmse_scores = -scores["test_rmse"]
    r2_scores = scores["test_r2"]

    return {
        "model": model_name,

        "mean_mae": round(
            float(np.mean(mae_scores)),
            4
        ),

        "std_mae": round(
            float(np.std(mae_scores)),
            4
        ),

        "mean_rmse": round(
            float(np.mean(rmse_scores)),
            4
        ),

        "std_rmse": round(
            float(np.std(rmse_scores)),
            4
        ),

        "mean_r2": round(
            float(np.mean(r2_scores)),
            4
        ),

        "std_r2": round(
            float(np.std(r2_scores)),
            4
        )
    }


def run_cross_validation():
    print(
        "Loading SmartPark AI dataset..."
    )

    dataset = pd.read_csv(
        DATASET_PATH
    )

    X = dataset[FEATURE_COLUMNS]
    y = dataset[TARGET_COLUMN]

    print(
        f"Dataset records: {len(dataset)}"
    )

    cross_validator = KFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_SEED
    )

    models = [
        (
            "Linear Regression",
            LinearRegression()
        ),

        (
            "Random Forest Regression",
            RandomForestRegressor(
                n_estimators=300,
                max_depth=12,
                random_state=RANDOM_SEED,
                n_jobs=1
            )
        ),

        (
            "Gradient Boosting Regression",
            GradientBoostingRegressor(
                n_estimators=300,
                learning_rate=0.05,
                max_depth=4,
                random_state=RANDOM_SEED
            )
        ),

        (
            "XGBoost Regression",
            XGBRegressor(
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
                n_jobs=1
            )
        )
    ]

    results = []

    for model_name, model in models:
        result = cross_validate_model(
            model_name=model_name,
            model=model,
            X=X,
            y=y,
            cross_validator=cross_validator
        )

        results.append(result)

    results.sort(
        key=lambda item: item["mean_rmse"]
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

    print("\n5-FOLD CROSS-VALIDATION RESULTS")
    print(
        "--------------------------------------------------------------------------"
    )

    print(
        f"{'Model':30} "
        f"{'MAE':>8} "
        f"{'RMSE':>8} "
        f"{'R²':>8}"
    )

    print(
        "--------------------------------------------------------------------------"
    )

    for result in results:
        print(
            f"{result['model']:30} "
            f"{result['mean_mae']:>8.4f} "
            f"{result['mean_rmse']:>8.4f} "
            f"{result['mean_r2']:>8.4f}"
        )

    print(
        "--------------------------------------------------------------------------"
    )

    print(
        "\nBest model by mean RMSE:",
        results[0]["model"]
    )

    print(
        "\nDetailed stability results:"
    )

    for result in results:
        print(
            f"\n{result['model']}"
        )

        print(
            f"MAE  = {result['mean_mae']} "
            f"± {result['std_mae']}"
        )

        print(
            f"RMSE = {result['mean_rmse']} "
            f"± {result['std_rmse']}"
        )

        print(
            f"R²   = {result['mean_r2']} "
            f"± {result['std_r2']}"
        )

    print(
        f"\nJSON saved: {JSON_OUTPUT_PATH}"
    )

    print(
        f"CSV saved: {CSV_OUTPUT_PATH}"
    )


if __name__ == "__main__":
    run_cross_validation()
