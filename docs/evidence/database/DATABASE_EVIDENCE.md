# SmartPark AI — Database Evidence

## 1. Database Platform

SmartPark AI uses PostgreSQL as the primary relational database.

SQLAlchemy is used by the FastAPI backend for database access and ORM mapping.

Alembic is used for schema migration management and database version control.

---

## 2. Live Schema Verification

The database schema was inspected directly from the running PostgreSQL database.

Verified result:

- Total database tables: 13
- Primary keys: verified
- Foreign-key relationships: verified
- Dynamic-pricing fields: verified
- EV-related fields: verified

The full automatically generated schema evidence is stored in:

`database-schema.txt`

---

## 3. Main Database Entities

The schema contains application entities for areas including:

- users;
- vehicles;
- parking locations;
- parking spaces;
- reservations;
- parking sessions;
- wallet/payment data;
- reviews;
- notifications;
- prediction-related data.

The exact live table list and column definitions are retained in the schema evidence file.

---

## 4. Parking Locations

The `parking_locations` table contains fields including:

- UUID primary key;
- name;
- address;
- city;
- postcode;
- latitude;
- longitude;
- total spaces;
- hourly rate;
- opening time;
- closing time;
- 24-hour status;
- active status;
- timestamps;
- dynamic pricing enabled status.

The verified live schema includes:

`dynamic_pricing_enabled: BOOLEAN NOT NULL`

This allows AI-assisted dynamic pricing to be enabled or disabled independently for each parking location.

---

## 5. Reservation Pricing Snapshot

The reservation schema supports storing the pricing conditions that existed when a reservation was created.

Dynamic-pricing metadata includes:

- base hourly rate;
- applied hourly rate;
- pricing multiplier;
- current occupancy at booking;
- predicted occupancy at booking;
- pricing model version.

This prevents later changes to a parking location's hourly rate from altering the rate already accepted by a customer.

Legacy reservations remain compatible through nullable snapshot fields and fallback behaviour.

---

## 6. EV Charging Data

Parking-space data supports EV charging information and charger operational status.

Supported prototype charger states include:

- available;
- occupied;
- offline;
- maintenance.

The application manages these values through backend reservation activity and administrator controls.

The prototype does not claim integration with physical EV hardware or IoT sensor feeds.

---

## 7. Referential Integrity

Foreign keys are used to maintain relationships between major entities.

Examples verified in the live schema include notification relationships to:

- users;
- reservations.

Additional application relationships are documented in `database-schema.txt`.

Foreign-key constraints help maintain consistency between related records.

---

## 8. Alembic Migration History

The current live development database revision is:

`c8a21d45e901 (head)`

Verified migration chain:

1. `3bb757555d38` — initial SmartPark schema
2. `7138a812e802` — prediction reproducibility metadata
3. `9c4e1a7b2f10` — EV charger live status
4. `b7f3d91a4c22` — dynamic pricing fields for reservations
5. `c8a21d45e901` — dynamic pricing switch for parking locations

The original Alembic terminal output is stored in:

`alembic-history.txt`

---

## 9. Migration Benefits

Using Alembic provides:

- reproducible schema changes;
- traceable database evolution;
- controlled upgrades;
- development/test schema consistency;
- rollback support where implemented;
- evidence of incremental system development.

This is preferable to manually modifying a production-style database schema without version tracking.

---

## 10. Database Security

Sensitive connection details are stored in environment configuration rather than source-code documentation.

The dissertation evidence must not expose:

- database passwords;
- JWT secrets;
- private environment values;
- authentication tokens.

The generated schema evidence contains structural information only.

---

## 11. Test Database Isolation

Automated backend testing uses a dedicated test database configuration.

The test suite is designed to avoid accidentally using the normal development database for test operations.

This reduces the risk of automated tests modifying development data.

---

## 12. Evidence Files

Database evidence retained for the dissertation:

- `database-schema.txt`
- `alembic-history.txt`
- `DATABASE_EVIDENCE.md`

Together these provide:

- live schema evidence;
- table and column evidence;
- foreign-key evidence;
- schema-version history;
- documentation of database design decisions.


---

# Final Database Update — London Open Data Integration

## Final PostgreSQL Schema

Following integration of the London Borough of Camden public parking
dataset, the final SmartPark AI database contains:

- 14 total PostgreSQL tables
- 13 application tables
- 1 Alembic version table

The new real-data entity is:

`external_parking_bays`

It contains genuine London Borough of Camden public parking
infrastructure records.

## External Parking Bays

The table stores:

- Camden source identifier
- restriction type
- declared parking spaces
- operating times
- maximum stay
- tariff
- road name
- postcode
- controlled parking zone
- latitude
- longitude
- EV and disabled parking information
- source update timestamp
- source organisation
- source dataset
- source URL
- import timestamp

The dataset currently contains:

- 8,787 records
- 35,010 declared parking spaces
- 856 distinct roads
- 281 EV charging records
- 793 disabled-bay records

## Separation of Operational and Public Data

`external_parking_bays` intentionally has no foreign-key relationship
to `parking_locations`.

This keeps two data domains separate:

`parking_locations`
→ SmartPark bookable operational prototype locations

`external_parking_bays`
→ genuine Camden public parking infrastructure records

This prevents public infrastructure data from being incorrectly treated
as SmartPark reservation or live-occupancy data.

## Migration

Final migration:

`1383148ede99`

Migration description:

`add external Camden parking bays`

Previous revision:

`c8a21d45e901`

Final revision:

`1383148ede99 (head)`

Both development and isolated test databases were migrated to the same
schema revision before final automated testing.

## Final ER Diagram

The final ER diagram was regenerated directly from the live PostgreSQL
schema.

Application entities:

`13`

The diagram includes `external_parking_bays` as a separate public-data
entity.

Final diagram files:

- `docs/diagrams/database-er-diagram.mmd`
- `docs/diagrams/rendered/database-er-diagram.png`
- `docs/diagrams/rendered/database-er-diagram.svg`

## Final Validation

Database integration validation:

**PASS**

Real-data import validation:

**PASS**

Backend regression testing:

**86 passed**

Frontend testing:

**10 passed**

Total automated tests:

**96 passed**

Production build:

**PASS**
