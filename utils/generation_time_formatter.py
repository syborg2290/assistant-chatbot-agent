def format_generation_time(seconds: float) -> str:
    """Convert raw seconds to human-readable time format
    Examples:
        0.5 → "500ms"
        45 → "45.00s"
        164.59 → "2m 44.59s"
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    if seconds < 60:
        return f"{seconds:.2f}s"
    minutes, secs = divmod(seconds, 60)
    return f"{int(minutes)}m {secs:.2f}s"
