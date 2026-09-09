from sqlalchemy import inspect, text


def test_uses_isolated_test_database(db_session):
    database_name = db_session.execute(
        text("SELECT current_database()")
    ).scalar_one()

    assert database_name == "smartpark_test_db"


def test_all_expected_tables_are_created(db_session):
    inspector = inspect(
        db_session.get_bind()
    )

    tables = set(
        inspector.get_table_names()
    )

    expected_tables = {
        "users",
        "vehicles",
        "parking_locations",
        "parking_spaces",
        "reservations",
        "predictions",
        "reviews",
        "notifications",
        "parking_sessions",
        "payments",
        "wallets",
        "wallet_transactions",
    }

    assert expected_tables.issubset(tables)
