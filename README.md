cd ~/smartpark-ai-independent

cat > README.md <<'EOF'
# SmartPark AI

**AI-Based Smart Parking Management System with Parking-Demand Prediction, Intelligent Recommendation, Reservation Management, Dynamic Pricing, Digital Wallet, EV Support and London Open-Data Integration**

SmartPark AI is an MSc Software Engineering dissertation project that investigates how artificial intelligence can support urban parking-demand forecasting and parking-location recommendation.

The system combines a Vue.js frontend, FastAPI backend, PostgreSQL database and an XGBoost machine-learning model to provide prediction-informed parking services through a complete web application.

---

## Project Objectives

SmartPark AI was designed to:

- predict future parking occupancy using machine learning;
- recommend suitable parking locations using multiple decision criteria;
- display current and predicted parking availability;
- support vehicle and parking-location management;
- allow users to create, manage and cancel reservations;
- provide barcode-based reservation identification;
- support parking check-in, session monitoring and checkout;
- provide wallet-based and card-based payment workflows;
- calculate bounded dynamic parking prices;
- support EV-charging availability states;
- provide reviews and notifications;
- provide role-based administration functionality;
- integrate genuine London Borough of Camden parking-infrastructure data separately from operational SmartPark parking locations.

---

## Technology Stack

### Frontend

- Vue 3
- Vite
- Tailwind CSS
- Axios
- Vue Router
- Chart.js
- Leaflet
- ZXing
- JsBarcode
- Vitest

### Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic
- Alembic
- PostgreSQL
- Pytest

### Machine Learning

- XGBoost
- scikit-learn
- Pandas
- NumPy
- Joblib

### Development and Version Control

- Git
- GitHub
- REST API / OpenAPI
- Agile iterative development
- Design Science Research methodology

---

## System Architecture

SmartPark AI follows a separated multi-layer architecture:

```text
Vue 3 Frontend
       |
       | REST / JSON
       v
FastAPI Backend
       |
       +--------------------+
       |                    |
       v                    v
Business Services      ML Prediction Service
       |                    |
       v                    v
PostgreSQL          Tuned XGBoost Model
       |
       v
Operational + External Open-Data Tables
