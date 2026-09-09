# SmartPark AI — System Architecture

## Overview

SmartPark AI uses a layered client-server architecture.

The Vue 3 frontend provides the user and administrator interfaces and communicates with the FastAPI backend using REST API requests and JSON responses.

## Frontend Layer

The frontend includes:

- Vue views and reusable components;
- Vue Router for navigation;
- an authentication store for user session state;
- Axios for communication with the backend.

## Backend Layer

The FastAPI backend separates the main business functions into modules including:

- authentication and role-based access control;
- parking management;
- reservations;
- wallet and payments;
- reviews;
- notifications;
- parking recommendations;
- AI-assisted dynamic pricing;
- administrator analytics;
- parking-demand prediction.

## Persistence Layer

SQLAlchemy is used as the ORM layer.

PostgreSQL stores the application data.

Alembic manages database schema migrations and provides traceable schema evolution.

## Machine-Learning Layer

The prediction service loads the persisted XGBoost parking-demand model.

The model is stored using Joblib.

Predicted occupancy is used by:

- the prediction interface;
- parking recommendations;
- administrator analytics;
- AI-assisted dynamic pricing.

## Architecture Figure

The Mermaid source for the architecture figure is stored in:

`system-architecture.mmd`

## Prototype Scope

The current prototype does not claim direct integration with:

- physical parking sensors;
- real EV charger hardware;
- live traffic feeds;
- live weather feeds;
- live city-event feeds.

These integrations are suitable future extensions.
