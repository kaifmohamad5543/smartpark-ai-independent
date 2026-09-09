from typing import Any

from pydantic import BaseModel


class ModelComparisonItem(BaseModel):
    rank: int
    model: str
    mae: float
    rmse: float
    r2: float


class CrossValidationItem(BaseModel):
    rank: int
    model: str
    mae_mean: float
    mae_std: float
    rmse_mean: float
    rmse_std: float
    r2_mean: float
    r2_std: float


class FeatureImportanceItem(BaseModel):
    feature: str
    display_name: str
    importance: float
    importance_percentage: float


class ModelPerformanceResponse(BaseModel):
    selected_model: str
    model_version: str
    dataset_type: str

    development_rows: int

    baseline_training_rows: int
    baseline_testing_rows: int

    baseline_mae: float
    baseline_rmse: float
    baseline_r2: float

    search_iterations: int
    tuning_cross_validation_folds: int
    best_cross_validation_rmse: float

    best_parameters: dict[str, Any]

    evaluation_rows: int
    evaluation_seed: int

    evaluation_mae: float
    evaluation_rmse: float
    evaluation_r2: float

    median_absolute_error: float
    p90_absolute_error: float

    feature_columns: list[str]

    model_comparison: list[ModelComparisonItem]

    baseline_cross_validation: list[
        CrossValidationItem
    ]

    feature_importance: list[
        FeatureImportanceItem
    ]

    evaluation_scope: str
