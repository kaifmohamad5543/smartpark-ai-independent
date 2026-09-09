"""
Central feature definition for SmartPark AI ML Version 2.

The model is site-agnostic: it does not use a hardcoded parking
location identifier. Parking characteristics and live occupancy
conditions are supplied as model features instead.
"""

FEATURE_COLUMNS = [
    "hour",
    "day_of_week",
    "previous_occupancy",
    "current_occupancy",
    "traffic_level",
    "weather",
    "event_level",
    "parking_price",
    "total_spaces",
]

TARGET_COLUMN = "occupancy_percentage"


FEATURE_LABELS = {
    "hour": "Hour of Day",
    "day_of_week": "Day of Week",
    "previous_occupancy": "Previous Occupancy",
    "current_occupancy": "Current Occupancy",
    "traffic_level": "Traffic Level",
    "weather": "Weather",
    "event_level": "Event Level",
    "parking_price": "Parking Price",
    "total_spaces": "Parking Capacity",
}
