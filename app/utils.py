import secrets
import string

ALPHABET = string.ascii_letters + string.digits


def generate_code(length: int = 7) -> str:
    """A fonction that generate unique code with 62**7 possible combination."""
    return "".join(secrets.choice(ALPHABET) for _ in range(length))