import uuid
from decimal import Decimal

from app.models.parking_location import ParkingLocation
from app.models.parking_space import ParkingSpace


def create_location(
    db_session,
    *,
    name="Test Parking Centre",
    is_active=True,
    total_spaces=10,
):
    location = ParkingLocation(
        name=name,
        address="10 Test Street",
        city="London",
        postcode="E1 1AA",
        latitude=51.515,
        longitude=-0.070,
        total_spaces=total_spaces,
        hourly_rate=Decimal("4.50"),
        opening_time=None,
        closing_time=None,
        is_24_hours=True,
        is_active=is_active,
    )

    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)

    return location


def create_space(
    db_session,
    location,
    number,
    *,
    is_available=True,
    is_active=True,
):
    space = ParkingSpace(
        parking_location_id=location.id,
        space_number=number,
        space_type="standard",
        is_available=is_available,
        has_ev_charging=False,
        is_accessible=False,
        is_active=is_active,
    )

    db_session.add(space)
    db_session.commit()
    db_session.refresh(space)

    return space


def test_list_returns_only_active_locations_in_name_order(
    client,
    db_session,
):
    create_location(
        db_session,
        name="Zulu Parking",
    )

    create_location(
        db_session,
        name="Alpha Parking",
    )

    create_location(
        db_session,
        name="Hidden Parking",
        is_active=False,
    )

    response = client.get(
        "/api/parking/locations"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert [
        item["name"]
        for item in data
    ] == [
        "Alpha Parking",
        "Zulu Parking",
    ]


def test_get_active_parking_location(
    client,
    db_session,
):
    location = create_location(
        db_session,
        name="Location Detail Test",
        total_spaces=25,
    )

    response = client.get(
        f"/api/parking/locations/{location.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(location.id)
    assert data["name"] == "Location Detail Test"
    assert data["city"] == "London"
    assert data["postcode"] == "E1 1AA"
    assert data["total_spaces"] == 25
    assert data["hourly_rate"] == 4.5
    assert data["is_24_hours"] is True
    assert data["is_active"] is True


def test_inactive_parking_location_is_not_publicly_accessible(
    client,
    db_session,
):
    location = create_location(
        db_session,
        name="Inactive Location",
        is_active=False,
    )

    response = client.get(
        f"/api/parking/locations/{location.id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Parking location not found."
    )


def test_unknown_parking_location_returns_404(client):
    unknown_id = uuid.uuid4()

    response = client.get(
        f"/api/parking/locations/{unknown_id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Parking location not found."
    )


def test_availability_counts_only_active_space_rows(
    client,
    db_session,
):
    location = create_location(
        db_session,
        name="Availability Test",
        total_spaces=99,
    )

    create_space(
        db_session,
        location,
        "A1",
        is_available=True,
    )

    create_space(
        db_session,
        location,
        "A2",
        is_available=True,
    )

    create_space(
        db_session,
        location,
        "A3",
        is_available=False,
    )

    create_space(
        db_session,
        location,
        "A4",
        is_available=False,
    )

    # This inactive space must not be included
    # in either total or available counts.
    create_space(
        db_session,
        location,
        "A5",
        is_available=True,
        is_active=False,
    )

    response = client.get(
        (
            "/api/parking/locations/"
            f"{location.id}/availability"
        )
    )

    assert response.status_code == 200

    data = response.json()

    assert data["parking_location_id"] == str(
        location.id
    )

    assert data["parking_name"] == (
        "Availability Test"
    )

    assert data["total_spaces"] == 4
    assert data["available_spaces"] == 2
    assert data["occupied_spaces"] == 2
    assert data["occupancy_percentage"] == 50.0


def test_availability_handles_zero_active_spaces(
    client,
    db_session,
):
    location = create_location(
        db_session,
        name="Empty Parking",
        total_spaces=20,
    )

    create_space(
        db_session,
        location,
        "X1",
        is_available=True,
        is_active=False,
    )

    response = client.get(
        (
            "/api/parking/locations/"
            f"{location.id}/availability"
        )
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_spaces"] == 0
    assert data["available_spaces"] == 0
    assert data["occupied_spaces"] == 0
    assert data["occupancy_percentage"] == 0.0


def test_inactive_location_availability_returns_404(
    client,
    db_session,
):
    location = create_location(
        db_session,
        name="Inactive Availability Test",
        is_active=False,
    )

    response = client.get(
        (
            "/api/parking/locations/"
            f"{location.id}/availability"
        )
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Parking location not found."
    )
