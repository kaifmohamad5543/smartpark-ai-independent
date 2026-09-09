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
from sklearn.model_selection import (
    RandomizedSearchCV,
    train_test_split
)
from xgboost import XGBRegressor


RANDOM_SEED = 42

DATASET_PATH = Path(
    "data/raw/parking_demand.csv"
)

MODEL_PATH = Path(
    "app/ml/model/xgboost_parking_demand_tuned.joblib"
)

RESULTS_PATH = Path(
    "data/processed/xgboost_tuning_results.json"
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


def tune_xgboost():
    print("Loading SmartPark AI dataset...")

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

    print(f"Training records: {len(X_train)}")
    print(f"Testing records: {len(X_test)}")

    base_model = XGBRegressor(
        objective="reg:squarederror",
        random_state=RANDOM_SEED,
        n_jobs=1
    )

    parameter_space = {
        "n_estimators": [
            200,
            300,
            400,
            500,
            650
        ],

        "learning_rate": [
            0.01,
            0.03,
            0.05,
            0.08,
            0.10
        ],

        "max_depth": [
            2,
            3,
            4,
            5,
            6,
            7
        ],

        "min_child_weight": [
            1,
            2,
            3,
            5,
            7
        ],

        "subsample": [
            0.70,
            0.80,
            0.90,
            1.00
        ],

        "colsample_bytree": [
            0.70,
            0.80,
            0.90,
            1.00
        ],

        "reg_alpha": [
            0.0,
            0.01,
            0.05,
            0.10,
            0.50
        ],

        "reg_lambda": [
            0.50,
            1.0,
            1.5,
            2.0,
            3.0
        ]
    }

    search = RandomizedSearchCV(
        estimator=base_model,
        param_distributions=parameter_space,
        n_iter=25,
        scoring="neg_root_mean_squared_error",
        cv=5,
        random_state=RANDOM_SEED,
        n_jobs=-1,
        verbose=1,
        return_train_score=False
    )

    print(
        "\nStarting XGBoost hyperparameter optimisation..."
    )

    search.fit(
        X_train,
        y_train
    )

    best_model = search.best_estimator_

    predictions = best_model.predict(
        X_test
    )

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

    results = {
        "model": "Tuned XGBoost Regression",

        "search_iterations": 25,

        "cross_validation_folds": 5,

        "training_rows": int(
            len(X_train)
        ),

        "testing_rows": int(
            len(X_test)
        ),

        "best_cross_validation_rmse": round(
            float(-search.best_score_),
            4
        ),

        "test_mae": round(
            float(mae),
            4
        ),

        "test_rmse": round(
            float(rmse),
            4
        ),

        "test_r2": round(
            float(r2),
            4
        ),

        "best_parameters": search.best_params_
    }

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    RESULTS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    model_bundle = {
        "model": best_model,

        "feature_columns":
            FEATURE_COLUMNS,

        "target_column":
            TARGET_COLUMN,

        "model_name":
            "Tuned XGBoost Regression",

        "version":
            "2.0",

        "best_parameters":
            search.best_params_
    }

    joblib.dump(
        model_bundle,
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
        "\nXGBOOST HYPERPARAMETER TUNING RESULTS"
    )

    print(
        "-------------------------------------------"
    )

    print(
        f"Best CV RMSE: "
        f"{results['best_cross_validation_rmse']}"
    )

    print(
        f"Test MAE:     "
        f"{results['test_mae']}"
    )

    print(
        f"Test RMSE:    "
        f"{results['test_rmse']}"
    )

    print(
        f"Test R²:      "
        f"{results['test_r2']}"
    )

    print(
        "\nBest parameters:"
    )

    for parameter, value in (
        search.best_params_.items()
    ):
        print(
            f"{parameter}: {value}"
        )

    print(
        f"\nTuned model saved: {MODEL_PATH}"
    )

    print(
        f"Results saved: {RESULTS_PATH}"
    )


if __name__ == "__main__":
    tune_xgboost()
