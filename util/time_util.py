import time as timepkg
from datetime import datetime

TWEET_CREATETIME_INPUTFORMAT = "%a %b %d %H:%M:%S  %Y"
TWEET_CREATETIME_OUTPUTFORMAT = "%Y-%m-%dT%H:%M:%SZ"
YYYYMMDDHHMMSS = "%Y%m%d%H%M%S"
YYYYMMDD = "%Y%m%d"
YYYYMMDDHHMM = "%Y%m%d%H%M"

YYYY_MM_DD_T_HH_MM_SS_SSS_Z = "%Y-%m-%dT%H:%M:%S.%fZ"
ISO_YMDTHMSSSSZ = "%Y-%m-%dT%H:%M:%S.%fZ"


def reformat_time(time_str: str, in_format: str, out_format: str) -> str:
    time_val: timepkg.struct_time = timepkg.strptime(time_str, in_format)
    return timepkg.strftime(out_format, time_val)


def format_time(time_val: timepkg.struct_time, out_format: str) -> str:
    return timepkg.strftime(out_format, time_val)


def format_datetime(dt: datetime, out_format: str) -> str:
    return dt.strftime(out_format)


def timestamp_now() -> int:
    return int(timepkg.time())
# TODO now timezone now utc
# diff sec minute hour day
# sec of day, mintue of day,hour of day
