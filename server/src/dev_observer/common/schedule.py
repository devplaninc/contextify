import datetime
from zoneinfo import ZoneInfo

from google.protobuf import timestamp_pb2, timestamp

from dev_observer.api.types.schedule_pb2 import Schedule, DayOfWeek, Frequency, Time


def pb_to_datetime(pb_dt: timestamp_pb2.Timestamp) -> datetime.datetime:
    return timestamp.to_datetime(pb_dt, datetime.timezone.utc)


def get_next_date(date: datetime.datetime, schedule: Schedule) -> datetime.datetime:
    """
    Compute the next date according to the provided schedule.
    
    Args:
        date: The reference date to compute the next occurrence from
        schedule: The schedule configuration containing frequency information
        
    Returns:
        The next datetime when the schedule should trigger
    """
    frequency = schedule.frequency
    freq_type = frequency.WhichOneof('type')

    if freq_type == 'daily':
        return _get_next_daily_date(date, frequency.daily)
    elif freq_type == 'weekly':
        return _get_next_weekly_date(date, frequency.weekly)
    else:
        raise ValueError(f"Unexpected frequency type [{freq_type}]")


def _get_next_daily_date(date: datetime.datetime, daily_schedule: Frequency.Daily) -> datetime.datetime:
    """Get the next occurrence for a daily schedule."""
    time_config = daily_schedule.time
    target_time = _create_target_datetime(date.date(), time_config)

    # If the target time today is in the future, return it
    if target_time > date:
        return target_time

    # Otherwise, return the same time tomorrow
    next_day = date.date() + datetime.timedelta(days=1)
    return _create_target_datetime(next_day, time_config)


def _get_next_weekly_date(date: datetime.datetime, weekly_schedule: Frequency.Weekly) -> datetime.datetime:
    """Get the next occurrence for a weekly schedule."""
    target_day_of_week = weekly_schedule.day_of_week
    time_config = weekly_schedule.time

    if target_day_of_week == DayOfWeek.DAY_OF_WEEK_UNSPECIFIED:
        raise ValueError(f"Invalid day of week: {target_day_of_week}")

    target_weekday = target_day_of_week - 1
    current_weekday = date.weekday()

    days_ahead = target_weekday - current_weekday
    if days_ahead < 0:  # Target day already happened this week
        days_ahead += 7
    elif days_ahead == 0:  # Target day is today
        # Check if the time has already passed today
        target_time_today = _create_target_datetime(date.date(), time_config)
        if target_time_today > date:
            return target_time_today
        else:
            days_ahead = 7  # Next week

    target_date = date.date() + datetime.timedelta(days=days_ahead)
    return _create_target_datetime(target_date, time_config)


def _create_target_datetime(target_date: datetime.date, time_config: Time) -> datetime.datetime:
    """Create a datetime from a date and time configuration."""
    time_of_day = time_config.time_of_day
    timezone_id = time_config.time_zone.id if time_config.time_zone.id else 'UTC'

    # Create timezone object
    try:
        tz = ZoneInfo(timezone_id)
    except Exception:
        # Fallback to UTC if timezone is invalid
        tz = ZoneInfo('UTC')

    # Create the target datetime
    seconds = time_of_day.seconds if hasattr(time_of_day, 'seconds') else 0
    microseconds = time_of_day.nanos // 1000 if hasattr(time_of_day, 'nanos') else 0
    
    target_datetime = datetime.datetime(
        year=target_date.year,
        month=target_date.month,
        day=target_date.day,
        hour=time_of_day.hours,
        minute=time_of_day.minutes,
        second=seconds,
        microsecond=microseconds,
        tzinfo=tz
    )
    target_datetime_utc = target_datetime.astimezone(datetime.timezone.utc)
    return target_datetime_utc
