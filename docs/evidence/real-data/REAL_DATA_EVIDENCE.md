# SmartPark AI — Real London Open Data Evidence

## 1. Purpose

SmartPark AI incorporates genuine publicly available London parking
infrastructure data to strengthen the realism and external-data
integration of the prototype.

The real-world dataset is kept separate from SmartPark's operational
reservation database and from the synthetic dataset used for the
controlled machine-learning experiment.

---

## 2. Public Dataset

**Dataset:** Camden Parking Bays  
**Organisation:** London Borough of Camden  
**Source:** Camden Open Data  
**Dataset ID:** 7hiv-3r9k  
**Records downloaded:** 8,787  
**Columns:** 26  

The dataset contains genuine parking infrastructure information including:

- parking restriction type
- declared parking spaces
- operating times
- maximum stay
- tariff information
- road name
- postcode
- controlled parking zone
- latitude and longitude
- EV charging bays
- disabled parking bays
- public source identifiers
- source update timestamp

The dataset is used as real parking-infrastructure evidence.

It is **not described as real-time parking occupancy data**.

---

## 3. Dataset Quality Profile

The downloaded dataset was profiled before database integration.

| Measure | Result |
|---|---:|
| Records | 8,787 |
| Columns | 26 |
| Valid coordinates | 8,787 |
| Declared parking spaces | 35,010 |
| Records with postcode | 8,787 |
| Records with operating times | 8,787 |
| Unique source identifiers | 8,787 |
| Duplicate source identifiers | 0 |
| Distinct roads after import | 856 |
| Paid-for bay records | 743 |
| EV charging bay records | 281 |
| Disabled bay records | 793 |

Geographic range:

- Latitude: 51.512998 to 51.571519
- Longitude: -0.212965 to -0.106455

---

## 4. Data Integrity and Provenance

The source CSV was fingerprinted using SHA-256:

`73ee2879e29dca6515a6b0549c4c96f8be3efc5ea38a8da1c203193682163450`

This supports reproducibility by allowing the exact dataset version used
during implementation to be identified.

The original Camden source identifier is preserved for every imported row.

---

## 5. PostgreSQL Integration

A dedicated SQLAlchemy entity was introduced:

`ExternalParkingBay`

Database table:

`external_parking_bays`

The table contains 24 columns and stores the public parking data separately
from SmartPark's bookable `parking_locations`.

Alembic migration:

`1383148ede99_add_external_camden_parking_bays.py`

Migration relationship:

`c8a21d45e901 -> 1383148ede99`

The migration created only the new public-data table and supporting indexes.

Indexes are provided for:

- source identifier
- road name
- postcode
- controlled parking zone
- latitude
- longitude

---

## 6. Import Process

Import script:

`scripts/import_camden_parking_bays.py`

Import method:

**SQLAlchemy PostgreSQL upsert**

Conflict key:

`source_identifier`

Validation result:

**PASS**

CSV valid records:

`8,787`

PostgreSQL records:

`8,787`

The matching counts demonstrate that all valid source records were
successfully persisted.

The upsert implementation also prevents duplicate records when the
import process is executed again.

---

## 7. Real Data API

SmartPark exposes the imported public dataset through FastAPI.

Endpoints:

`GET /api/open-data/parking-bays`

`GET /api/open-data/parking-bays/stats`

`GET /api/open-data/parking-bays/{source_identifier}`

The API supports filters for:

- road name
- postcode
- restriction type
- minimum and maximum latitude
- minimum and maximum longitude
- pagination limit
- pagination offset

The geographic bounding-box filters allow the frontend to request only
records relevant to the current visible map area.

---

## 8. API Verification

The live statistics API returned:

- 8,787 total records
- 35,010 declared parking spaces
- 856 distinct roads
- 743 paid-for records
- 281 EV charging records
- 793 disabled-bay records

A live Abbey Road query also returned genuine records including source IDs,
postcodes, restriction types, operating periods, parking-space counts,
tariffs and geographic coordinates.

This demonstrates:

**PostgreSQL -> FastAPI -> JSON response**

using genuine imported public data.

---

## 9. Vue and Leaflet Integration

A separate **Camden Open Data** layer was added to the SmartPark parking map.

It remains visually and logically separate from SmartPark's bookable
prototype locations.

The user can enable or disable the public-data layer.

The map displays information including:

- road
- postcode
- restriction
- declared spaces
- operating times
- tariff where available
- EV identification
- disabled-bay identification
- Camden source ID

The interface explicitly states:

**Public parking infrastructure record — not live occupancy.**

For frontend performance, a maximum of 500 records is requested for the
current map bounding box.

---

## 10. Frontend Verification

Production build:

**PASS**

- Vite 8.2.2
- 2,192 modules transformed
- build completed successfully

Runtime map validation:

- Camden Open Data panel: PASS
- dataset totals displayed: PASS
- real Camden markers rendered: 500
- visible Camden records: 500

Evidence screenshot:

`docs/evidence/screenshots/36-camden-open-data-map.png`

---

## 11. Research Significance

This integration strengthens SmartPark AI by demonstrating that the
prototype can ingest, store, query and visualise genuine external urban
parking data rather than relying exclusively on manually configured
prototype locations.

The real dataset contributes evidence for:

- external-data integration
- database design
- data provenance
- geospatial information handling
- REST API development
- frontend mapping
- EV parking representation
- realistic London parking infrastructure

However, this public dataset does not provide real-time occupancy labels.

Therefore, the XGBoost demand-prediction evaluation must continue to be
reported separately as evaluation on unseen synthetic observations under
the same simulation assumptions.

This distinction prevents real infrastructure data from being incorrectly
presented as real-world validation of the demand-prediction model.

---

## 12. Evidence Files

Supporting evidence:

- `camden_parking_bays_profile.txt`
- `camden_database_import_evidence.txt`
- `../../screenshots/36-camden-open-data-map.png`
- `../../../diagrams/database-er-diagram.mmd`
- `../../../diagrams/rendered/database-er-diagram.png`

Source dataset:

- `backend/data/real/camden_parking_bays.csv`

Implementation:

- `backend/app/models/external_parking_bay.py`
- `backend/app/schemas/open_data.py`
- `backend/app/routes/open_data.py`
- `backend/scripts/import_camden_parking_bays.py`
- `frontend/src/views/ParkingView.vue`
