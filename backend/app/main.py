from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import engine
from app.routes.auth import router as auth_router
from app.routes.vehicles import router as vehicles_router
from app.routes.parking import router as parking_router
from app.routes.open_data import router as open_data_router
from app.routes.reservations import router as reservations_router
from app.routes.predictions import router as predictions_router
from app.routes.recommendations import router as recommendations_router
from app.routes.reviews import router as reviews_router
from app.routes.notifications import router as notifications_router
from app.routes.parking_sessions import router as parking_sessions_router


app = FastAPI(
    title="SmartPark AI API",
    description="AI-based parking demand prediction and parking recommendation system.",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(vehicles_router)
app.include_router(parking_router)
app.include_router(open_data_router)
app.include_router(reservations_router)
app.include_router(predictions_router)
app.include_router(recommendations_router)
app.include_router(reviews_router)
app.include_router(notifications_router)
app.include_router(parking_sessions_router)


@app.get("/")
def root():
    return {
        "message": "SmartPark AI backend is running",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SmartPark AI API"
    }


@app.get("/health/database")
def database_health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "PostgreSQL",
            "connection": "successful"
        }

    except Exception as error:
        return {
            "status": "unhealthy",
            "database": "PostgreSQL",
            "error": str(error)
        }

from app.routes.admin_analytics import router as admin_analytics_router

app.include_router(admin_analytics_router)

from app.routes.admin_parking import router as admin_parking_router

app.include_router(admin_parking_router)

from app.routes.payments import router as payments_router

app.include_router(payments_router)

from app.routes.wallet import router as wallet_router

app.include_router(wallet_router)

from app.routes.admin_payments import router as admin_payments_router

app.include_router(admin_payments_router)

from app.routes.admin_users import router as admin_users_router
app.include_router(admin_users_router)

from app.routes.admin_reservations import router as admin_reservations_router
app.include_router(admin_reservations_router)

from app.routes.admin_reviews import router as admin_reviews_router
app.include_router(admin_reviews_router)

from app.routes.admin_notifications import router as admin_notifications_router
app.include_router(admin_notifications_router)
