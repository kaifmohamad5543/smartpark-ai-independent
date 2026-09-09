import json
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.ensemble import (
    GradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_validate
from xgboost import XGBRegressor

from app.ml.features import FEATURE_COLUMNS, TARGET_COLUMN


RANDOM_SEED = 42
NUMBER_OF_FOLDS = 5

DATASET_PATH = Path(
    "data/raw/parking_demand.csv"
)

CSV_OUTPUT_PATH = Path(
    "data/processed/cross_validation_results_v2.csv"
)

JSON_OUTPUT_PATH = Path(
    "data/processed/cross_validation_results_v2.json"
)


def cross_validate_models():
    dataset = pd.read_csv(
        DATASET_PATH
    )

    X = dataset[FEATURE_COLUMNS]
    y = dataset[TARGET_COLUMN]

    cross_validator = KFold(
        n_splits=NUMBER_OF_FOLDS,
        shuffle=True,
        random_state=RANDOM_SEED
    )

    models = {
        "Linear Regression": LinearRegression(),

        "Random Forest": RandomForestRegressor(
            n_estimators=300,
            min_samples_leaf=2,
            random_state=RANDOM_SEED,
            n_jobs=-1
        ),

        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=3,
            random_state=RANDOM_SEED
        ),

        "XGBoost": XGBRegressor(
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
        ),
    }

    scoring = {
        "mae": "neg_mean_absolute_error",
        "rmse": "neg_root_mean_squared_error",
        "r2": "r2",
    }

    results = []

    print(
        "===== SMARTPARK AI V2 "
        "5-FOLD CROSS-VALIDATION ====="
    )

    for model_name, model in models.items():

        print(f"\nEvaluating: {model_name}")

        scores = cross_validate(
            model,
            X,
            y,
            cv=cross_validator,
            scoring=scoring,
            n_jobs=-1
        )

        mae_values = -scores["test_mae"]
        rmse_values = -scores["test_rmse"]
        r2_values = scores["test_r2"]

        result = {
            "model": model_name,

            "mae_mean": round(
                float(np.mean(mae_values)),
                4
            ),
            "mae_std": round(
                float(np.std(mae_values)),
                4
            ),

            "rmse_mean": round(
                float(np.mean(rmse_values)),
                4
            ),
            "rmse_std": round(
                float(np.std(rmse_values)),
                4
            ),

            "r2_mean": round(
                float(np.mean(r2_values)),
                4
            ),
            "r2_std": round(
                float(np.std(r2_values)),
                4
            ),
        }

        results.append(result)

        print(
            f"MAE:  "
            f"{result['mae_mean']:.4f} "
            f"± {result['mae_std']:.4f}"
        )

        print(
            f"RMSE: "
            f"{result['rmse_mean']:.4f} "
            f"± {result['rmse_std']:.4f}"
        )

        print(
            f"R²:   "
            f"{result['r2_mean']:.4f} "
            f"± {result['r2_std']:.4f}"
        )

    results = sorted(
        results,
        key=lambda item: item["rmse_mean"]
    )

    for rank, result in enumerate(
        results,
        start=1
    ):
        result["rank"] = rank

    dataframe = pd.DataFrame(results)

    dataframe = dataframe[
        [
            "rank",
            "model",
            "mae_mean",
            "mae_std",
            "rmse_mean",
            "rmse_std",
            "r2_mean",
            "r2_std",
        ]
    ]

    CSV_OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    dataframe.to_csv(
        CSV_OUTPUT_PATH,
        index=False
    )

    with open(
        JSON_OUTPUT_PATH,
        "w"
    ) as file:
        json.dump(
            dataframe.to_dict(
                orient="records"
            ),
            file,
            indent=4
        )

    print(
        "\n===== FINAL 5-FOLD RANKING ====="
    )

    print(
        dataframe.to_string(
            index=False
        )
    )

    print(
        f"\nCSV saved: {CSV_OUTPUT_PATH}"
    )

    print(
        f"JSON saved: {JSON_OUTPUT_PATH}"
    )


if __name__ == "__main__":
    cross_validate_models()
