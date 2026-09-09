import secrets


ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def generate_booking_code(length: int = 8) -> str:
    random_part = "".join(
        secrets.choice(ALPHABET)
        for _ in range(length)
    )

    return f"SP-{random_part}"
