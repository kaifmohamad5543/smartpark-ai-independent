# SmartPark AI — Database ER Diagram

## Overview

The SmartPark AI entity-relationship diagram was generated directly from the live PostgreSQL development database.

The diagram therefore represents the implemented database rather than a conceptual or manually reconstructed schema.

## Main Entities

The database contains entities supporting:

- users and authentication;
- vehicles;
- parking locations;
- parking spaces;
- reservations;
- parking sessions;
- wallet and payment transactions;
- reviews;
- notifications;
- machine-learning prediction history.

## Key Relationships

Foreign-key relationships connect users with their vehicles, reservations, payments, notifications and prediction records.

Parking locations contain parking spaces and are referenced by reservations and parking sessions.

Reservations connect users, vehicles, parking locations and allocated parking spaces, while completed parking activity can produce parking-session and payment records.

## EV Charging

Parking-space records contain EV charging capability and charger-status fields.

Prototype charger states include available, occupied, offline and maintenance.

## AI Dynamic Pricing

Parking locations contain a dynamic-pricing enable/disable field.

Reservations store pricing snapshot information so the accepted hourly rate can remain locked after booking.

## Diagram Source

The Mermaid ER source is stored in:

`database-er-diagram.mmd`

The internal Alembic version table is intentionally excluded from the dissertation ER figure.
