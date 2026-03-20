from datetime import datetime, timezone
from zoneinfo import ZoneInfo

def utc_to_msk_string(dt: datetime) -> str:
    if dt.tzinfo is None:
       dt = dt.replace(tzinfo=timezone.utc)

    return utc_to_msk_datetime(dt).strftime("%Y-%m-%d %H:%M:%S")

def utc_to_msk_datetime(dt: datetime) -> datetime:
    if dt.tzinfo is None:
       dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(ZoneInfo("Europe/Moscow"))