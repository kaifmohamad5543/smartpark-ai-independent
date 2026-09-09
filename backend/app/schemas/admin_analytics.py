from pydantic import BaseModel


class AdminAnalyticsOverview(BaseModel):
    total_users: int
    active_users: int

    total_reservations: int
    confirmed_reservations: int
    checked_in_reservations: int
    cancelled_reservations: int
    completed_reservations: int

    completed_parking_sessions: int
    total_revenue: float

    total_parking_locations: int
    total_parking_spaces: int
    available_parking_spaces: int
    overall_occupancy_percentage: float

    total_predictions: int
    average_predicted_occupancy: float


class ParkingLocationPerformance(BaseModel):
    parking_location_id: str
    parking_name: str

    total_spaces: int
    available_spaces: int
    current_occupancy_percentage: float

    total_reservations: int
    completed_reservations: int
    cancelled_reservations: int

    completed_sessions: int
    total_revenue: float

    average_predicted_occupancy: float

    average_rating: float
    review_count: int




from datetime import date


class ReservationTrendItem(BaseModel):
    date: date
    total_reservations: int
    confirmed: int
    checked_in: int
    completed: int
    cancelled: int


from datetime import datetime


class AIDemandPredictionItem(BaseModel):
    prediction_id: str
    parking_location_id: str
    parking_name: str

    predicted_occupancy: float
    predicted_availability: float

    demand_level: str

    created_at: datetime


class AIDemandAnalyticsResponse(BaseModel):
    total_predictions: int
    average_predicted_occupancy: float

    low_demand_count: int
    medium_demand_count: int
    high_demand_count: int
    very_high_demand_count: int

    recent_predictions: list[AIDemandPredictionItem]
