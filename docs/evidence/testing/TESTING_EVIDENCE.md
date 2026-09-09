# SmartPark AI — Testing Evidence

## 1. Testing Overview

SmartPark AI was evaluated using automated backend testing, automated frontend testing and a production frontend build verification.

The purpose of testing was to confirm that the main application modules continued to operate correctly after implementation and integration of features such as reservations, EV charging, machine-learning prediction and AI-assisted dynamic pricing.

---

## 2. Backend Automated Testing

Testing framework:

Pytest

Latest verified result:

- 82 tests passed
- 1 warning
- execution time: 13.35 seconds

The backend tests cover major application areas including:

- authentication
- vehicle management
- parking locations
- parking spaces
- reservations
- wallet and payments
- refunds
- reviews
- notifications
- administrator functionality
- EV charger status
- machine-learning prediction
- parking recommendations
- AI-assisted dynamic pricing

The complete terminal output is stored in:

`backend-tests.txt`

### Warning

The test run produced one Starlette TestClient/httpx deprecation warning.

This warning did not cause any test failures and does not indicate a failed application function.

---

## 3. Frontend Automated Testing

Testing framework:

Vitest

Latest verified result:

- 3 test files passed
- 10 tests passed
- 0 failed tests
- execution time: 1.58 seconds

Current automated frontend tests cover:

- authentication store behaviour
- router behaviour
- Not Found / 404 page behaviour

The complete terminal output is stored in:

`frontend-tests.txt`

---

## 4. Production Build Verification

The frontend was also compiled using the Vite production-build command.

Latest verified result:

- 2192 modules transformed
- production build completed successfully
- build time: 748 ms

The successful build confirms that the Vue frontend, including the newly integrated booking and administrator components, can be compiled into deployable production assets without build errors.

The complete build output is stored in:

`frontend-build.txt`

---

## 5. Overall Automated Result

| Test Area | Result |
|---|---:|
| Backend tests | 82 passed |
| Frontend tests | 10 passed |
| Total automated tests | 92 passed |
| Frontend production build | Passed |

Overall automated result:

**92 automated tests passed with no test failures.**

---

## 6. Dynamic Pricing Testing

The backend test suite includes dedicated tests for AI-assisted dynamic pricing.

Testing verifies:

- existing fixed-price cost calculation remains supported;
- neutral demand produces a neutral pricing result;
- high demand can increase the hourly rate;
- low demand can reduce the hourly rate;
- the pricing multiplier remains inside the configured safe bounds;
- the booking stores the AI pricing snapshot;
- the applied hourly rate remains locked after booking;
- later changes to the parking-location base rate do not modify the previously accepted booking rate.

This is important because the dynamic-pricing implementation affects both reservation creation and checkout cost calculation.

---

## 7. EV Charging Testing

Automated backend tests also verify EV charging behaviour.

The prototype supports charger states including:

- available
- occupied
- offline
- maintenance

Tests verify that application activity can update suitable charger states while preserving offline and maintenance conditions.

The implementation represents prototype application-managed EV status and does not claim integration with physical EV charger hardware.

---

## 8. Reservation Testing

Reservation testing covers the reservation lifecycle and associated validation.

Relevant behaviours include:

- reservation creation;
- parking-space allocation;
- reservation timing;
- check-in;
- checkout;
- opening-hour validation;
- payment calculation;
- locked booking pricing;
- dynamic-pricing metadata.

---

## 9. Evaluation Interpretation

The automated results demonstrate that the implemented prototype functions are internally consistent under the tested scenarios.

However, passing software tests does not by itself prove real-world deployment performance.

Additional real-world validation would require:

- real parking occupancy data;
- external usability testing;
- production infrastructure;
- real traffic/weather/event feeds;
- physical parking or EV hardware integration;
- larger-scale performance testing.

---

## 10. Evidence Files

The following evidence files are retained:

- `backend-tests.txt`
- `frontend-tests.txt`
- `frontend-build.txt`

These files preserve the original terminal results used to support the dissertation testing chapter.


---

# Final Validation After London Open Data Integration

## Automated Test Summary

Following integration of the London Borough of Camden public parking
dataset, the complete SmartPark AI system was revalidated.

| Test Area | Result |
|---|---:|
| Backend Pytest tests | 86 passed |
| Frontend Vitest tests | 10 passed |
| Total automated tests | 96 passed |
| Backend failures | 0 |
| Frontend failures | 0 |
| Production build | PASS |

## Backend Validation

Final backend suite:

`86 passed, 1 warning in 12.56s`

The four additional tests specifically validate the Camden Open Data
integration:

- dataset statistics endpoint
- filtering and geographic query behaviour
- individual source-record retrieval
- 404 handling for unknown source identifiers

The existing 82 SmartPark backend tests also continued to pass after the
real-data integration.

This provides regression evidence that the new external-data functionality
did not break existing authentication, reservations, parking management,
wallet, payments, refunds, EV charging, dynamic pricing, predictions,
recommendations, reviews, notifications or administrative functionality.

Evidence file:

`backend-tests-final-with-open-data.txt`

## Frontend Validation

Final frontend result:

`10 passed`

Across:

`3 passed test files`

Evidence file:

`frontend-tests-after-real-data.txt`

## Production Build Validation

The final Vue production build completed successfully.

- Vite: 8.2.2
- Modules transformed: 2,192
- Build result: PASS
- Build time: 669 ms

Evidence file:

`frontend-build-final-with-real-data.txt`

## Real Data Integration Validation

The London Open Data integration was also verified across the full
application pipeline:

`Camden Open Data -> CSV -> PostgreSQL -> FastAPI -> Vue -> Leaflet`

Verified results:

- 8,787 genuine public parking-bay records
- 35,010 declared parking spaces
- 856 distinct roads
- 281 EV charging records
- 793 disabled-bay records
- 500 genuine records rendered in the visible Leaflet map area
- database import validation: PASS
- API validation: PASS
- map integration validation: PASS

The Camden dataset represents genuine parking infrastructure information
and is not described as real-time occupancy data.

The XGBoost demand-prediction evaluation therefore remains separately
reported as evaluation on unseen synthetic observations under the same
simulation assumptions.
