import csv
import hashlib
import uuid
from datetime import datetime
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from app.database import engine
from app.models.external_parking_bay import ExternalParkingBay


SOURCE = Path(
    "data/real/camden_parking_bays.csv"
)

EVIDENCE = Path(
    "../docs/evidence/real-data/"
    "camden_database_import_evidence.txt"
)

SOURCE_URL = (
    "https://opendata.camden.gov.uk/"
    "resource/7hiv-3r9k"
)


def clean(value):
    value = (value or "").strip()

    if not value:
        return None

    if value.upper() == "N/A":
        return None

    return value


def to_int(value):
    value = clean(value)

    if value is None:
        return None

    try:
        return int(float(value))
    except ValueError:
        return None


def to_float(value):
    value = clean(value)

    if value is None:
        return None

    try:
        return float(value)
    except ValueError:
        return None


def to_datetime(value):
    value = clean(value)

    if value is None:
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError:
        return None


if not SOURCE.exists():
    raise SystemExit(
        f"Dataset not found: {SOURCE}"
    )


sha256 = hashlib.sha256(
    SOURCE.read_bytes()
).hexdigest()


records = []

with SOURCE.open(
    "r",
    encoding="utf-8-sig",
    newline=""
) as file:
    reader = csv.DictReader(file)

    for row in reader:
        source_id = clean(
            row.get("unique_identifier")
        )

        latitude = to_float(
            row.get("latitude")
        )

        longitude = to_float(
            row.get("longitude")
        )

        road_name = clean(
            row.get("road_name")
        )

        restriction_type = clean(
            row.get("restriction_type")
        )

        if not all([
            source_id,
            latitude is not None,
            longitude is not None,
            road_name,
            restriction_type,
        ]):
            continue

        records.append({
            "id": uuid.uuid4(),
            "source_identifier": source_id,
            "restriction_type":
                restriction_type,
            "parking_spaces":
                to_int(
                    row.get("parking_spaces")
                ),
            "times_of_operation":
                clean(
                    row.get(
                        "times_of_operation"
                    )
                ),
            "maximum_stay":
                clean(
                    row.get("maximum_stay")
                ),
            "tariff":
                clean(
                    row.get("tariff")
                ),
            "cashless_identifier":
                clean(
                    row.get(
                        "cashless_identifier"
                    )
                ),
            "road_name":
                road_name,
            "postcode":
                clean(
                    row.get("postcode")
                ),
            "controlled_parking_zone":
                clean(
                    row.get(
                        "controlled_parking_zone"
                    )
                ),
            "valid_parking_permits":
                clean(
                    row.get(
                        "valid_parking_permits"
                    )
                ),
            "parking_bay_length_metres":
                to_float(
                    row.get(
                        "parking_bay_length_metres"
                    )
                ),
            "easting":
                to_float(
                    row.get("easting")
                ),
            "northing":
                to_float(
                    row.get("northing")
                ),
            "longitude":
                longitude,
            "latitude":
                latitude,
            "spatial_accuracy":
                clean(
                    row.get(
                        "spatial_accuracy"
                    )
                ),
            "source_last_uploaded":
                to_datetime(
                    row.get("last_uploaded")
                ),
            "organisation_uri":
                clean(
                    row.get(
                        "organisation_uri"
                    )
                ),
            "source_dataset":
                "Camden Parking Bays",
            "source_organisation":
                "London Borough of Camden",
            "source_url":
                SOURCE_URL,
})
if not records:
    raise SystemExit(
        "No valid records found." )
table = ExternalParkingBay.__table__
update_columns = {
    column.name: getattr(
        insert(table).excluded,
        column.name,)
    for column in table.columns
    if column.name not in {
        "id",
        "source_identifier",
        "imported_at", }}
with engine.begin() as connection:
    for start in range(
        0,
        len(records),
        500, ):
        batch = records[
            start:start + 500 ]
        statement = (
            insert(table)
            .values(batch)
            .on_conflict_do_update(
                index_elements=[
                    "source_identifier"
                ],
                set_=update_columns, ) )
        connection.execute(
            statement )
with engine.connect() as connection:
    db_count = connection.scalar(
        select(
            func.count()
        ).select_from(
            table )    )

    total_spaces = connection.scalar(
        select(
            func.coalesce(
                func.sum(
                    table.c.parking_spaces
                ),
                0,
            )
        )
    )

    paid_for = connection.scalar(
        select(
            func.count()
        )
        .select_from(table)
        .where(
            table.c.restriction_type
            == "paid-for"
        )
    )

    ev = connection.scalar(
        select(
            func.count()
        )
        .select_from(table)
        .where(
            table.c.restriction_type
            == "electric vehicle recharging"
        )
    )

    road_count = connection.scalar(
        select(
            func.count(
                func.distinct(
                    table.c.road_name
                )
            )
        )
    )


lines = [
    "SMARTPARK AI - REAL DATA DATABASE IMPORT",
    "=" * 60,
    "",
    "Dataset: Camden Parking Bays",
    "Source organisation: London Borough of Camden",
    f"Source URL: {SOURCE_URL}",
    "",
    f"CSV valid records: {len(records):,}",
    f"PostgreSQL records: {db_count:,}",
    f"Declared parking spaces: {int(total_spaces):,}",
    f"Distinct roads: {road_count:,}",
    f"Paid-for bay records: {paid_for:,}",
    f"EV charging bay records: {ev:,}",
    "",
    f"SHA-256: {sha256}",
    "",
    "Database table: external_parking_bays",
    "Import method: SQLAlchemy PostgreSQL upsert",
    "Conflict key: source_identifier",
    "",
    "DATA INTERPRETATION",
    "-" * 60,
    (
        "These records represent genuine Camden "
        "parking infrastructure."
    ),
    (
        "They do not represent real-time "
        "parking occupancy."
    ),
]


if db_count == len(records):
    lines += [
        "",
        "IMPORT VALIDATION: PASS",
        (
            "CSV valid-record count matches "
            "PostgreSQL row count."
        ),
    ]
else:
    lines += [
        "",
        "IMPORT VALIDATION: REVIEW REQUIRED",
        (
            "CSV and PostgreSQL counts "
            "do not match."
        ),
    ]


output = "\n".join(lines) + "\n"

EVIDENCE.write_text(
    output,
    encoding="utf-8",
)

print(output)

print(
    "Evidence saved to:",
    EVIDENCE,
)
