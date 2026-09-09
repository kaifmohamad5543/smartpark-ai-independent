# SmartPark AI — Dissertation Evidence Index

This folder contains the final dissertation evidence for the SmartPark AI project.

## 1. User Interface Evidence

Folder:

`screenshots/`

Verified screenshots include:

- login
- registration
- dashboard
- parking search and map
- booking form
- AI dynamic pricing notice
- Camden Open Data map integration

Key real-data screenshot:

`36-camden-open-data-map.png`

This screenshot demonstrates:

- London Borough of Camden Open Data integration
- genuine public parking infrastructure records
- 8,787 total source records
- 35,010 declared parking spaces
- 500 real records rendered within the visible map area

The Camden layer is clearly separated from SmartPark's bookable prototype
locations and is not described as live occupancy data.

---

## 2. Testing Evidence

Folder:

`testing/`

Final verified results:

- Backend Pytest: 86 passed
- Frontend Vitest: 10 passed
- Total automated tests: 96 passed
- Backend failures: 0
- Frontend failures: 0
- Production build: PASS
- Vite modules transformed: 2,192
- Final production build time: 669 ms

Important evidence files:

- `backend-tests-final-with-open-data.txt`
- `frontend-tests-after-real-data.txt`
- `frontend-build-final-with-real-data.txt`
- `TESTING_EVIDENCE.md`

The four additional backend tests specifically validate:

- Camden statistics endpoint
- filtering and geographic query behaviour
- individual source-record retrieval
- unknown-record 404 handling

---

## 3. Real London Open Data Evidence

Folder:

`real-data/`

Primary source:

**London Borough of Camden — Camden Parking Bays**

Verified dataset:

- 8,787 records
- 26 source columns
- 8,787 valid coordinate records
- 35,010 declared parking spaces
- 856 distinct roads
- 743 paid-for bay records
- 281 EV charging records
- 793 disabled-bay records
- 8,787 unique source identifiers
- 0 duplicate source identifiers

Dataset fingerprint:

`73ee2879e29dca6515a6b0549c4c96f8be3efc5ea38a8da1c203193682163450`

Evidence files:

- `camden_parking_bays_profile.txt`
- `camden_database_import_evidence.txt`
- `REAL_DATA_EVIDENCE.md`

Integration pipeline:

`Camden Open Data -> CSV -> PostgreSQL -> FastAPI -> Vue -> Leaflet`

Important limitation:

The Camden dataset represents genuine parking infrastructure information.
It is not real-time parking occupancy data.

---

## 4. PostgreSQL Database Evidence

Folder:

`database/`

Final database:

- 14 total PostgreSQL tables
- 13 application tables
- 1 Alembic version table

Real-data table:

`external_parking_bays`

This table stores the genuine Camden public parking records separately from
SmartPark's operational `parking_locations`.

Final migration:

`1383148ede99`

Migration description:

`add external Camden parking bays`

Final database revision:

`1383148ede99 (head)`

Important evidence files:

- `database-schema.txt`
- `alembic-history.txt`
- `DATABASE_EVIDENCE.md`

---

## 5. Database ER Diagram

Folder:

`../diagrams/`

Final live-schema ER diagram:

- 13 application entities
- `external_parking_bays` included
- generated from the live PostgreSQL schema

Files:

- `database-er-diagram.mmd`
- `rendered/database-er-diagram.png`
- `rendered/database-er-diagram.svg`

The public Camden entity intentionally has no artificial foreign key to
SmartPark's bookable parking locations.

---

## 6. Artificial Intelligence Evidence

Folder:

`ai/`

Final production model:

**Tuned XGBoost Parking Demand Model V2**

Model comparison evidence includes:

- XGBoost
- Gradient Boosting
- Random Forest
- Linear Regression

Final unseen synthetic evaluation under the same simulation assumptions:

- MAE: 4.7191
- RMSE: 5.9884
- R²: 0.9159
- Median absolute error: 3.8522
- 90th percentile absolute error: 9.8915

Important evidence:

- model comparison
- hyperparameter tuning
- independent synthetic evaluation
- feature importance
- prediction API
- recommendation API

Important academic distinction:

The Camden public dataset strengthens real-world infrastructure integration,
but it does not provide real occupancy labels.

Therefore the ML results are not presented as real-world validation.

---

## 7. API Evidence

Folder:

`api/`

FastAPI evidence includes:

- OpenAPI schema
- Swagger documentation
- public parking endpoints
- authentication endpoints
- reservation endpoints
- prediction endpoints
- recommendation endpoints
- payment and wallet endpoints
- administrative endpoints
- London Open Data endpoints

New real-data endpoints:

`GET /api/open-data/parking-bays`

`GET /api/open-data/parking-bays/stats`

`GET /api/open-data/parking-bays/{source_identifier}`

The real-data list endpoint supports:

- road filtering
- postcode filtering
- restriction filtering
- geographic bounding boxes
- limit
- offset

---

## 8. Security Evidence

Folder:

`security/`

Security evidence includes:

- Argon2 password hashing
- JWT authentication
- authenticated-user dependencies
- admin-role authorization
- protected routes
- input validation
- isolated test database protection
- environment-based configuration

Evidence file:

`SECURITY_EVIDENCE.md`

---

## 9. Architecture and Design Evidence

Folder:

`../diagrams/`

Available architecture diagrams include:

- system architecture
- database ER diagram
- machine-learning workflow
- reservation and dynamic-pricing flow
- frontend/backend API flow

Rendered PNG and SVG versions are available in:

`docs/diagrams/rendered/`

---

## 10. Final Verified Project State

SmartPark AI currently demonstrates:

- Vue 3 frontend
- FastAPI backend
- PostgreSQL database
- SQLAlchemy ORM
- Alembic migrations
- XGBoost demand prediction
- AI-assisted parking recommendations
- reservation lifecycle
- digital wallet
- payments and refunds
- EV charging representation
- reviews
- notifications
- administrative management
- dynamic pricing
- Leaflet mapping
- genuine London public parking data integration

Final automated validation:

**96 tests passed**

Final production build:

**PASS**

Real London parking records integrated:

**8,787**

Final application database entities:

**13**

---

## 11. Important Dissertation Limitations

The prototype does not claim:

- real parking-sensor integration
- real-time Camden parking occupancy
- real EV charger sensor integration
- live traffic feeds
- live weather feeds
- live event feeds
- real-world ML demand validation

The Camden Open Data integration represents genuine London parking
infrastructure evidence.

The XGBoost evaluation remains correctly described as:

**unseen synthetic evaluation under the same simulation assumptions**

---

## 12. Real London Data Integration Diagram

A dedicated architecture diagram documents how genuine London Borough of
Camden parking infrastructure data is integrated into SmartPark AI.

Pipeline:

`Camden Open Data -> CSV -> Profiling -> PostgreSQL -> FastAPI -> Vue -> Leaflet`

Diagram files:

- `docs/diagrams/real-data-integration-pipeline.mmd`
- `docs/diagrams/rendered/real-data-integration-pipeline.png`
- `docs/diagrams/rendered/real-data-integration-pipeline.svg`

The diagram explicitly distinguishes:

- genuine Camden public parking infrastructure data;
- SmartPark operational/bookable parking locations;
- synthetic ML demand-evaluation data.

It also records the research boundary that the Camden dataset is not
real-time occupancy data and is not used as real-world ML validation labels.
