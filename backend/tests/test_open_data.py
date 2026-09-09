from datetime import datetime

from app.models.external_parking_bay import (
    ExternalParkingBay,
)


def make_bay(
    source_identifier,
    road_name,
    postcode,
    restriction_type,
    parking_spaces,
    latitude,
    longitude,
):
    return ExternalParkingBay(
        source_identifier=source_identifier,
        restriction_type=restriction_type,
        parking_spaces=parking_spaces,
        times_of_operation="mon-fri 08:30-18:30",
        maximum_stay="2 hours",
        tariff="£4.00 per hour",
        cashless_identifier=None,
        road_name=road_name,
        postcode=postcode,
        controlled_parking_zone="CA-K",
        valid_parking_permits=None,
        parking_bay_length_metres=6.0,
        easting=529000.0,
        northing=183000.0,
        longitude=longitude,
        latitude=latitude,
        spatial_accuracy="Defined By Custodian",
        source_last_uploaded=datetime(
            2026,
            9,
            3,
            23,
            0,
            0,
        ),
        organisation_uri=(
            "http://opendatacommunities.org/"
            "id/london-borough-council/camden"
        ),
        source_dataset="Camden Parking Bays",
        source_organisation=(
            "London Borough of Camden"
        ),
        source_url=(
            "https://opendata.camden.gov.uk/"
            "resource/7hiv-3r9k"
        ),
    )


def test_open_data_stats_reports_database_values(
    client,
    db_session,
):
    db_session.add_all([
        make_bay(
            "REAL-001",
            "Abbey Road",
            "NW6 4SL",
            "paid-for",
            3,
            51.540310,
            -0.188186,
        ),
        make_bay(
            "REAL-002",
            "Camden High Street",
            "NW1 7JE",
            "electric vehicle recharging",
            4,
            51.539000,
            -0.142000,
        ),
        make_bay(
            "REAL-003",
            "Euston Road",
            "NW1 2RT",
            "disabled (blue badge)",
            2,
            51.528000,
            -0.133000,
        ),
    ])

    db_session.commit()

    response = client.get(
        "/api/open-data/parking-bays/stats"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_records"] == 3
    assert data["declared_parking_spaces"] == 9
    assert data["distinct_roads"] == 3
    assert data["paid_for_records"] == 1
    assert data["ev_charging_records"] == 1
    assert data["disabled_bay_records"] == 1
    assert (
        data["source_organisation"]
        == "London Borough of Camden"
    )


def test_open_data_list_supports_filters(
    client,
    db_session,
):
    db_session.add_all([
        make_bay(
            "FILTER-001",
            "Abbey Road",
            "NW6 4SL",
            "paid-for",
            3,
            51.540310,
            -0.188186,
        ),
        make_bay(
            "FILTER-002",
            "Different Road",
            "NW3 2AA",
            "permit holders only",
            2,
            51.550000,
            -0.160000,
        ),
    ])

    db_session.commit()

    response = client.get(
        "/api/open-data/parking-bays",
        params={
            "road_name": "Abbey",
            "postcode": "NW6",
            "restriction_type": "paid-for",
            "min_lat": 51.53,
            "max_lat": 51.55,
            "min_lon": -0.20,
            "max_lon": -0.18,
            "limit": 10,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert (
        data[0]["source_identifier"]
        == "FILTER-001"
    )
    assert data[0]["road_name"] == "Abbey Road"


def test_open_data_detail_returns_source_record(
    client,
    db_session,
):
    db_session.add(
        make_bay(
            "DETAIL-001",
            "Fitzroy Street",
            "W1T 5BR",
            "paid-for",
            1,
            51.523692,
            -0.140101,
        )
    )

    db_session.commit()

    response = client.get(
        "/api/open-data/parking-bays/DETAIL-001"
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["source_identifier"]
        == "DETAIL-001"
    )
    assert data["road_name"] == "Fitzroy Street"
    assert data["postcode"] == "W1T 5BR"
    assert (
        data["source_dataset"]
        == "Camden Parking Bays"
    )


def test_unknown_open_data_record_returns_404(
    client,
):
    response = client.get(
        "/api/open-data/parking-bays/UNKNOWN-ID"
    )

    assert response.status_code == 404
    assert (
        response.json()["detail"]
        == "External parking bay not found."
    )
