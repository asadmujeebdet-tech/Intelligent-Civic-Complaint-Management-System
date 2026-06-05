from datetime import datetime


def system_now() -> datetime:
    """Return current local system time."""
    return datetime.now()
