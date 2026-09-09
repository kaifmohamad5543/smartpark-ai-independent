import json
from pathlib import Path


PROCESSED_DATA_PATH = Path(
    "data/processed"
)


def load_json(
    filename: str
):
    path = (
        PROCESSED_DATA_PATH
        / filename
    )

    if not path.exists():
        raise FileNotFoundError(
            f"ML evaluation file not found: {filename}"
        )

    with open(
        path,
        "r"
    ) as file:
        return json.load(file)


def get_model_performance() -> dict:

    baseline = load_json(
        "xgboost_v2_metrics.json"
    )

    comparison = load_json(
        "model_comparison_v2.json"
    )

    cross_validation = load_json(
        "cross_validation_results_v2.json"
    )

    tuning = load_json(
        "xgboost_v2_tuning_results.json"
    )

    evaluation = load_json(
        "xgboost_v2_evaluation_metrics.json"
    )

    feature_importance_data = load_json(
        "feature_importance_v2.json"
    )

    feature_importance = (
        feature_importance_data[
            "features"
        ]
    )

    baseline_features = baseline[
        "feature_columns"
    ]

    tuning_features = tuning[
        "feature_columns"
    ]

    evaluation_features = evaluation[
        "feature_columns"
    ]

    if not (
        baseline_features
        == tuning_features
        == evaluation_features
    ):
        raise ValueError(
            "ML Version 2 feature definitions "
            "are inconsistent across evaluation files."
        )

    return {
        "selected_model":
            "XGBoost Regressor",

        "model_version":
            evaluation["model_version"],

        "dataset_type":
            evaluation["dataset_type"],

        "development_rows":
            tuning["records_used"],

        "baseline_training_rows":
            baseline["training_records"],

        "baseline_testing_rows":
            baseline["testing_records"],

        "baseline_mae":
            baseline["mae"],

        "baseline_rmse":
            baseline["rmse"],

        "baseline_r2":
            baseline["r2"],

        "search_iterations":
            tuning["iterations"],

        "tuning_cross_validation_folds":
            tuning["cv_folds"],

        "best_cross_validation_rmse":
            tuning[
                "best_cross_validation_rmse"
            ],

        "best_parameters":
            tuning["best_parameters"],

        "evaluation_rows":
            evaluation[
                "evaluation_records"
            ],

        "evaluation_seed":
            evaluation[
                "evaluation_seed"
            ],

        "evaluation_mae":
            evaluation["mae"],

        "evaluation_rmse":
            evaluation["rmse"],

        "evaluation_r2":
            evaluation["r2"],

        "median_absolute_error":
            evaluation[
                "median_absolute_error"
            ],

        "p90_absolute_error":
            evaluation[
                "p90_absolute_error"
            ],

        "feature_columns":
            evaluation_features,

        "model_comparison":
            comparison,

        "baseline_cross_validation":
            cross_validation,

        "feature_importance":
            feature_importance,

        "evaluation_scope":
            (
                "Independent synthetic evaluation "
                "using 2,500 unseen records generated "
                "with a different random seed but the "
                "same simulation assumptions. These "
                "results do not represent external "
                "real-world validation."
            )
    }
