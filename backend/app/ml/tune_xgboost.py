import json
from pathlib import Path

import joblib
import pandas as pd

from sklearn.model_selection import (
    KFold,
    RandomizedSearchCV,
)
from xgboost import XGBRegressor

from app.ml.features import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
)


RANDOM_SEED = 42
NUMBER_OF_ITERATIONS = 30
NUMBER_OF_FOLDS = 5

DATASET_PATH = Path(
    "data/raw/parking_demand.csv"
)

MODEL_PATH = Path(
    "app/ml/model/xgboost_parking_demand_v2_tuned.joblib"
)

RESULTS_PATH = Path(
    "data/processed/xgboost_v2_tuning_results.json"
)


def tune_xgboost():
    print(
        "Loading SmartPark AI V2 development dataset..."
    )

    dataset = pd.read_csv(
        DATASET_PATH
    )

    X = dataset[FEATURE_COLUMNS]
    y = dataset[TARGET_COLUMN]

    model = XGBRegressor(
        objective="reg:squarederror",
        random_state=RANDOM_SEED,
        n_jobs=-1
    )

    parameter_space = {
        "n_estimators": [
            200,
            300,
            400,
            500,
            650,
        ],
        "learning_rate": [
            0.01,
            0.03,
            0.05,
            0.08,
            0.10,
        ],
        "max_depth": [
            2,
            3,
            4,
            5,
            6,
        ],
        "min_child_weight": [
            1,
            3,
            5,
            7,
        ],
        "subsample": [
            0.70,
            0.80,
            0.90,
            1.00,
        ],
        "colsample_bytree": [
            0.70,
            0.80,
            0.90,
            1.00,
        ],
        "reg_alpha": [
            0.0,
            0.01,
            0.05,
            0.10,
            0.50,
        ],
        "reg_lambda": [
            0.5,
            1.0,
            2.0,
            3.0,
            5.0,
        ],
    }

    cross_validator = KFold(
        n_splits=NUMBER_OF_FOLDS,
        shuffle=True,
        random_state=RANDOM_SEED
    )

    search = RandomizedSearchCV(
        estimator=model,
        param_distributions=parameter_space,
        n_iter=NUMBER_OF_ITERATIONS,
        scoring="neg_root_mean_squared_error",
        cv=cross_validator,
        random_state=RANDOM_SEED,
        n_jobs=-1,
        verbose=1,
        return_train_score=False
    )

    print(
        "\nStarting XGBoost V2 hyperparameter tuning..."
    )

    search.fit(
        X,
        y
    )

    best_rmse = float(
        -search.best_score_
    )

    results = {
        "model_version": "2.0",
        "dataset_type": "synthetic",
        "tuning_method": "RandomizedSearchCV",
        "iterations": NUMBER_OF_ITERATIONS,
        "cv_folds": NUMBER_OF_FOLDS,
        "scoring": "RMSE",
        "best_cross_validation_rmse": round(
            best_rmse,
            4
        ),
        "best_parameters": search.best_params_,
        "feature_columns": FEATURE_COLUMNS,
        "records_used": len(dataset),
    }

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    RESULTS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        {
            "model": search.best_estimator_,
            "feature_columns": FEATURE_COLUMNS,
            "target_column": TARGET_COLUMN,
            "model_version": "2.0-tuned",
            "dataset_type": "synthetic",
            "best_parameters": search.best_params_,
        },
        MODEL_PATH
    )

    with open(
        RESULTS_PATH,
        "w"
    ) as file:
        json.dump(
            results,
            file,
            indent=4
        )

    print(
        "\n===== XGBOOST V2 TUNING RESULTS ====="
    )

    print(
        f"Best 5-fold CV RMSE: {best_rmse:.4f}"
    )

    print(
        "\nBest parameters:"
    )

    for name, value in sorted(
        search.best_params_.items()
    ):
        print(
            f"{name}: {value}"
        )

    print(
        f"\nTuned model saved: {MODEL_PATH}"
    )

    print(
        f"Tuning results saved: {RESULTS_PATH}"
    )


if __name__ == "__main__":
    tune_xgboost()
