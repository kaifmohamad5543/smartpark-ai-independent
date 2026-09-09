import json
from pathlib import Path

import pandas as pd

from sklearn.ensemble import (
    GradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression
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

CSV_OUTPUT_PATH = Path(
    "data/processed/model_comparison_v2.csv"
)

JSON_OUTPUT_PATH = Path(
    "data/processed/model_comparison_v2.json"
)


def compare_models():
    dataset = pd.read_csv(
        DATASET_PATH
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

    models = {
        "Linear Regression": LinearRegression(),

        "Random Forest": RandomForestRegressor(
            n_estimators=300,
            max_depth=None,
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

    results = []

    print(
        "===== SMARTPARK AI V2 MODEL COMPARISON ====="
    )

    for model_name, model in models.items():

        print(
            f"\nTraining: {model_name}"
        )

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

        result = {
            "model": model_name,
            "mae": round(mae, 4),
            "rmse": round(rmse, 4),
            "r2": round(r2, 4),
        }

        results.append(
            result
        )

        print(
            f"MAE:  {mae:.4f}"
        )

        print(
            f"RMSE: {rmse:.4f}"
        )

        print(
            f"R²:   {r2:.4f}"
        )

    results = sorted(
        results,
        key=lambda item: item["rmse"]
    )

    for rank, result in enumerate(
        results,
        start=1
    ):
        result["rank"] = rank

    dataframe = pd.DataFrame(
        results
    )

    dataframe = dataframe[
        [
            "rank",
            "model",
            "mae",
            "rmse",
            "r2",
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
        "\n===== FINAL RANKING BY RMSE ====="
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
    compare_models()
