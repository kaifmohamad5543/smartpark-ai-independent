from pathlib import Path

import joblib
import numpy as np
import pandas as pd


MODEL_PATH = Path(
    "app/ml/model/xgboost_parking_demand_tuned.joblib"
)


LOCATION_MAPPING = {
    "liverpool_street": 0,
    "stratford": 1,
    "canary_wharf": 2
}


class ParkingDemandPredictor:

    def __init__(self):
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"ML model not found: {MODEL_PATH}"
            )

        bundle = joblib.load(
            MODEL_PATH
        )

        self.model = bundle["model"]
        self.feature_columns = bundle[
            "feature_columns"
        ]

    def predict(
        self,
        hour: int,
        day_of_week: int,
        parking_location: int,
        previous_occupancy: float,
        traffic_level: int,
        weather: int,
        event_level: int,
        parking_price: float,
        available_spaces: int
    ) -> float:

        input_data = pd.DataFrame(
            [
                {
                    "hour": hour,
                    "day_of_week": day_of_week,
                    "parking_location": parking_location,
                    "previous_occupancy": previous_occupancy,
                    "traffic_level": traffic_level,
                    "weather": weather,
                    "event_level": event_level,
                    "parking_price": parking_price,
                    "available_spaces": available_spaces
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


predictor = ParkingDemandPredictor()
