import json
from pathlib import Path

import pandas as pd
from sklearn.ensemble import (
    GradientBoostingRegressor,
    RandomForestRegressor
)
from sklearn.linear_model import LinearRegression
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

OUTPUT_PATH = Path(
    "data/processed/model_comparison.json"
)

CSV_OUTPUT_PATH = Path(
    "data/processed/model_comparison.csv"
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


def evaluate_model(
    model_name,
    model,
    X_train,
    X_test,
    y_train,
    y_test
):
    print(f"\nTraining {model_name}...")

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
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

    return {
        "model": model_name,
        "mae": round(float(mae), 4),
        "rmse": round(float(rmse), 4),
        "r2": round(float(r2), 4)
    }


def compare_models():
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
                n_jobs=-1
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
                n_jobs=-1
            )
        )
    ]

    results = []

    for model_name, model in models:
        result = evaluate_model(
            model_name=model_name,
            model=model,
            X_train=X_train,
            X_test=X_test,
            y_train=y_train,
            y_test=y_test
        )

        results.append(result)

    results.sort(
        key=lambda item: item["rmse"]
    )

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

    pd.DataFrame(
        results
    ).to_csv(
        CSV_OUTPUT_PATH,
        index=False
    )

    print("\nMODEL COMPARISON")
    print(
        "---------------------------------------------------------------"
    )
    print(
        f"{'Model':32} {'MAE':>8} {'RMSE':>8} {'R²':>8}"
    )
    print(
        "---------------------------------------------------------------"
    )

    for result in results:
        print(
            f"{result['model']:32} "
            f"{result['mae']:>8.4f} "
            f"{result['rmse']:>8.4f} "
            f"{result['r2']:>8.4f}"
        )

    print(
        "---------------------------------------------------------------"
    )

    print(
        f"\nBest model by RMSE: {results[0]['model']}"
    )

    print(
        f"\nJSON saved: {OUTPUT_PATH}"
    )

    print(
        f"CSV saved: {CSV_OUTPUT_PATH}"
    )


if __name__ == "__main__":
    compare_models()
