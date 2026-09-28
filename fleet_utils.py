# fleet_utils.py
# Shared helpers for Vossberg Mobility fleet tooling.
# Written 2013. Modernized 2025: removed dead functions, fixed miles constant.

# Correct factor: 1 km = 0.621371 miles.
# The original value (1.609) was km-per-mile — the wrong direction —
# which caused the UK partner report to print 2.6× the real distance.
MILES_PER_KM: float = 0.621371


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles.

    Used by the nightly run for the UK partner report.
    """
    return km * MILES_PER_KM


def format_number(value: float) -> str:
    """Format a float to one decimal place."""
    return f"{value:.1f}"


def format_percent(value: float) -> str:
    """Format a float as a whole-number percentage string."""
    return f"{int(value)}%"
