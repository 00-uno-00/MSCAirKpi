# --- Utility functions ---

def safe_int(val, default=0):
    try:
        return int(val)
    except (TypeError, ValueError):
        return default

def safe_float(val, default=0.0):
    try:
        return float(val)
    except (TypeError, ValueError):
        return default

def time_to_minutes(h, m):
    return safe_int(h) * 60 + safe_int(m)

def minutes_to_hhmm(minutes):
    hours = minutes // 60
    mins = minutes % 60
    return f"{str(round(hours)).zfill(2)}:{str(round(mins)).zfill(2)}"
