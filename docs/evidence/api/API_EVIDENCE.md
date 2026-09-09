# SmartPark AI — REST API Evidence

## 1. API Framework

SmartPark AI uses FastAPI to provide the backend REST API.

FastAPI automatically generates an OpenAPI specification and interactive Swagger documentation.

Local Swagger interface:

`http://127.0.0.1:8000/docs`

---

## 2. Verified API Size

The OpenAPI specification was retrieved directly from the running backend.

Verified result:

- API title: SmartPark AI API
- API version: 1.0.0
- Documented paths: 53
- Documented operations: 59

The complete generated OpenAPI specification is stored in:

`openapi.json`

A human-readable endpoint list is stored in:

`api-endpoints.txt`

---

## 3. Authentication API

Authentication operations include:

- user registration;
- user login;
- authenticated profile retrieval.

Verified routes include:

- POST `/api/auth/register`
- POST `/api/auth/login`
- GET `/api/auth/me`

JWT authentication is used for protected operations.

---

## 4. Parking API

Parking endpoints provide:

- parking-location listing;
- parking-location details;
- parking availability.

Examples:

- GET `/api/parking/locations`
- GET `/api/parking/locations/{parking_location_id}`
- GET `/api/parking/locations/{parking_location_id}/availability`

---

## 5. Reservation and Parking Session API

The backend provides reservation lifecycle functionality together with parking-session history.

The reservation API supports operations including:

- reservation creation;
- reservation retrieval;
- reservation cancellation;
- check-in;
- checkout.

Parking history is exposed through:

- GET `/api/parking-sessions`

---

## 6. Prediction API

The machine-learning API provides parking-demand prediction and prediction-history functionality.

Prediction requests are handled by the backend ML service using the persisted XGBoost model.

Prediction history is available through:

- GET `/api/predictions`

---

## 7. Recommendation API

The recommendation service ranks parking locations using information such as:

- distance;
- price;
- availability;
- current occupancy;
- predicted occupancy;
- rating.

This service is separate from the XGBoost demand-prediction model.

---

## 8. Payments and Wallet API

The application provides operations for:

- wallet management;
- payment records;
- transaction history;
- reservation charges.

Verified payment operations include:

- GET `/api/payments`
- GET `/api/payments/{payment_id}`

Administrator refund processing is provided through:

- POST `/api/admin/payments/{payment_id}/refund`

---

## 9. Notifications API

User notification operations include:

- notification listing;
- unread-count retrieval;
- marking individual notifications as read;
- marking all notifications as read.

Verified examples:

- GET `/api/notifications`
- GET `/api/notifications/unread-count`
- PATCH `/api/notifications/{notification_id}/read`
- PATCH `/api/notifications/read-all`

---

## 10. Administrator API

Administrator routes include functionality for:

- analytics;
- parking locations;
- parking spaces;
- users;
- reservations;
- payments;
- refunds;
- reviews;
- notifications.

Examples include:

- GET `/api/admin/analytics/overview`
- GET `/api/admin/analytics/ai-demand`
- GET `/api/admin/analytics/model-performance`
- GET `/api/admin/parking/locations`
- POST `/api/admin/parking/locations`
- PATCH `/api/admin/parking/locations/{parking_location_id}`
- GET `/api/admin/users`
- GET `/api/admin/reservations`
- GET `/api/admin/payments`
- GET `/api/admin/reviews`

Administrator access is protected using role-based authorization.

---

## 11. Dynamic Pricing API Integration

Dynamic pricing is integrated into parking-location administration and reservation creation.

Parking locations expose whether AI-assisted dynamic pricing is enabled.

When enabled, reservation creation can store:

- base hourly rate;
- applied hourly rate;
- pricing multiplier;
- current occupancy at booking;
- predicted occupancy at booking;
- prediction model version.

This allows the frontend to display the locked booking-price explanation after reservation confirmation.

---

## 12. London Open Data API

The final backend includes three dedicated endpoints for the genuine
London Borough of Camden parking-bay dataset.

Verified routes:

- GET `/api/open-data/parking-bays`
- GET `/api/open-data/parking-bays/stats`
- GET `/api/open-data/parking-bays/{source_identifier}`

The parking-bay list endpoint supports filtering by:

- road name;
- postcode;
- restriction type;
- minimum and maximum latitude;
- minimum and maximum longitude;
- pagination using limit and offset.

The statistics endpoint reports the imported public-data profile,
including:

- 8,787 parking-bay records;
- 35,010 declared parking spaces;
- 856 distinct roads;
- 743 paid-for records;
- 281 EV charging records;
- 793 disabled-bay records.

The detail endpoint retrieves an individual Camden source record using
its original source identifier.

The public-data API deliberately exposes the Camden records separately
from SmartPark's operational and bookable parking locations.

These records represent genuine public parking infrastructure data and
are not claimed to represent real-time parking occupancy.

---

## 13. API Validation

FastAPI and Pydantic provide structured request and response validation.

The backend also performs business-rule validation for operations such as:

- reservation timing;
- parking-space availability;
- account access;
- administrator authorization;
- payments;
- refunds;
- dynamic pricing.

---

## 14. Evidence Files

The retained API evidence consists of:

- `openapi.json`
- `api-endpoints.txt`
- `API_EVIDENCE.md`

The first two files were generated directly from the running SmartPark AI backend rather than manually reconstructed.

