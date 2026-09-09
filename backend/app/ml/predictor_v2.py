from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from app.ml.features import FEATURE_COLUMNS


MODEL_PATH = Path(
    "app/ml/model/xgboost_parking_demand_v2_tuned.joblib"
)


class ParkingDemandPredictorV2:

    def __init__(self):
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"ML V2 model not found: {MODEL_PATH}"
            )

        bundle = joblib.load(
            MODEL_PATH
        )

        self.model = bundle["model"]

        self.feature_columns = bundle[
            "feature_columns"
        ]

        self.model_version = bundle.get(
            "model_version",
            "2.0-tuned"
        )

        if self.feature_columns != FEATURE_COLUMNS:
            raise ValueError(
                "Loaded V2 model feature definition "
                "does not match app/ml/features.py."
            )

    def predict(
        self,
        hour: int,
        day_of_week: int,
        previous_occupancy: float,
        current_occupancy: float,
        traffic_level: int,
        weather: int,
        event_level: int,
        parking_price: float,
        total_spaces: int,
    ) -> float:

        input_data = pd.DataFrame(
            [
                {
                    "hour": hour,
                    "day_of_week": day_of_week,
                    "previous_occupancy":
                        previous_occupancy,
                    "current_occupancy":
                        current_occupancy,
                    "traffic_level":
                        traffic_level,
                    "weather":
                        weather,
                    "event_level":
                        event_level,
                    "parking_price":
                        parking_price,
                    "total_spaces":
                        total_spaces,
                }
            ],
            columns=self.feature_columns
        )

        prediction = self.model.predict(
            input_data
        )[0]

        prediction = np.clip(
            prediction,
            0,
            100
        )

        return round(
            float(prediction),
            2
        )


predictor_v2 = ParkingDemandPredictorV2()
