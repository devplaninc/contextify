import datetime
from zoneinfo import ZoneInfo

import pytest

from dev_observer.api.types.schedule_pb2 import Schedule, DayOfWeek
from dev_observer.common.schedule import get_next_date


class TestGetNextDate:
    """Test cases for the get_next_date function."""

    def test_daily_schedule_future_time_today(self):
        """Test daily schedule when target time is later today."""
        # Current time: 2025-07-24 10:00:00 UTC
        current_time = datetime.datetime(2025, 7, 24, 10, 0, 0, tzinfo=ZoneInfo('UTC'))

        # Schedule for 15:30 UTC daily
        schedule = Schedule()
        schedule.frequency.daily.time.time_of_day.hours = 15
        schedule.frequency.daily.time.time_of_day.minutes = 30
        schedule.frequency.daily.time.time_zone.id = 'UTC'

        result = get_next_date(current_time, schedule)
        expected = datetime.datetime(2025, 7, 24, 15, 30, 0, tzinfo=ZoneInfo('UTC'))

        assert result == expected

    def test_daily_schedule_past_time_today(self):
        """Test daily schedule when target time has already passed today."""
        # Current time: 2025-07-24 16:00:00 UTC
        current_time = datetime.datetime(2025, 7, 24, 16, 0, 0, tzinfo=ZoneInfo('UTC'))

        # Schedule for 15:30 UTC daily
        schedule = Schedule()
        schedule.frequency.daily.time.time_of_day.hours = 15
        schedule.frequency.daily.time.time_of_day.minutes = 30
        schedule.frequency.daily.time.time_zone.id = 'UTC'

        result = get_next_date(current_time, schedule)
        expected = datetime.datetime(2025, 7, 25, 15, 30, 0, tzinfo=ZoneInfo('UTC'))

        assert result == expected

    def test_daily_schedule_with_timezone(self):
        """Test daily schedule with non-UTC timezone."""
        # Current time: 2025-07-24 10:00:00 EST
        current_time = datetime.datetime(2025, 7, 24, 10, 0, 0, tzinfo=ZoneInfo('America/New_York'))

        # Schedule for 15:30 EST daily
        schedule = Schedule()
        schedule.frequency.daily.time.time_of_day.hours = 15
        schedule.frequency.daily.time.time_of_day.minutes = 30
        schedule.frequency.daily.time.time_zone.id = 'America/New_York'

        result = get_next_date(current_time, schedule)
        expected = datetime.datetime(2025, 7, 24, 15, 30, 0, tzinfo=ZoneInfo('America/New_York'))

        assert result == expected

    def test_weekly_schedule_same_day_future_time(self):
        """Test weekly schedule when target day is today but time is in the future."""
        # Current time: Thursday 2025-07-24 10:00:00 UTC
        current_time = datetime.datetime(2025, 7, 24, 10, 0, 0, tzinfo=ZoneInfo('UTC'))

        # Schedule for Thursday 15:30 UTC weekly
        schedule = Schedule()
        schedule.frequency.weekly.day_of_week = DayOfWeek.THURSDAY
        schedule.frequency.weekly.time.time_of_day.hours = 15
        schedule.frequency.weekly.time.time_of_day.minutes = 30
        schedule.frequency.weekly.time.time_zone.id = 'UTC'

        result = get_next_date(current_time, schedule)
        expected = datetime.datetime(2025, 7, 24, 15, 30, 0, tzinfo=ZoneInfo('UTC'))

        assert result == expected

    def test_weekly_schedule_same_day_same_time(self):
        current_time = datetime.datetime(2025, 7, 24, 15, 30, 0, tzinfo=ZoneInfo('UTC'))

        # Schedule for Thursday 15:30 UTC weekly
        schedule = Schedule()
        schedule.frequency.weekly.day_of_week = DayOfWeek.THURSDAY
        schedule.frequency.weekly.time.time_of_day.hours = 15
        schedule.frequency.weekly.time.time_of_day.minutes = 30
        schedule.frequency.weekly.time.time_zone.id = 'UTC'

        result = get_next_date(current_time, schedule)
        expected = datetime.datetime(2025, 7, 31, 15, 30, 0, tzinfo=ZoneInfo('UTC'))

        assert result == expected

    def test_weekly_schedule_same_day_past_time(self):
        """Test weekly schedule when target day is today but time has passed."""
        # Current time: Thursday 2025-07-24 16:00:00 UTC
        current_time = datetime.datetime(2025, 7, 24, 16, 0, 0, tzinfo=ZoneInfo('UTC'))

        # Schedule for Thursday 15:30 UTC weekly
        schedule = Schedule()
        schedule.frequency.weekly.day_of_week = DayOfWeek.THURSDAY
        schedule.frequency.weekly.time.time_of_day.hours = 15
        schedule.frequency.weekly.time.time_of_day.minutes = 30
        schedule.frequency.weekly.time.time_zone.id = 'UTC'

        result = get_next_date(current_time, schedule)
        expected = datetime.datetime(2025, 7, 31, 15, 30, 0, tzinfo=ZoneInfo('UTC'))  # Next Thursday

        assert result == expected

    def test_weekly_schedule_future_day(self):
        """Test weekly schedule when target day is later this week."""
        # Current time: Thursday 2025-07-24 10:00:00 UTC
        current_time = datetime.datetime(2025, 7, 24, 10, 0, 0, tzinfo=ZoneInfo('UTC'))

        # Schedule for Saturday 15:30 UTC weekly
        schedule = Schedule()
        schedule.frequency.weekly.day_of_week = DayOfWeek.SATURDAY
        schedule.frequency.weekly.time.time_of_day.hours = 15
        schedule.frequency.weekly.time.time_of_day.minutes = 30
        schedule.frequency.weekly.time.time_zone.id = 'UTC'

        result = get_next_date(current_time, schedule)
        expected = datetime.datetime(2025, 7, 26, 15, 30, 0, tzinfo=ZoneInfo('UTC'))  # This Saturday

        assert result == expected

    def test_weekly_schedule_past_day(self):
        """Test weekly schedule when target day was earlier this week."""
        # Current time: Thursday 2025-07-24 10:00:00 UTC
        current_time = datetime.datetime(2025, 7, 24, 10, 0, 0, tzinfo=ZoneInfo('UTC'))

        # Schedule for Tuesday 15:30 UTC weekly
        schedule = Schedule()
        schedule.frequency.weekly.day_of_week = DayOfWeek.TUESDAY
        schedule.frequency.weekly.time.time_of_day.hours = 15
        schedule.frequency.weekly.time.time_of_day.minutes = 30
        schedule.frequency.weekly.time.time_zone.id = 'UTC'

        result = get_next_date(current_time, schedule)
        expected = datetime.datetime(2025, 7, 29, 15, 30, 0, tzinfo=ZoneInfo('UTC'))  # Next Tuesday

        assert result == expected

    def test_weekly_schedule_sunday(self):
        """Test weekly schedule for Sunday (edge case in weekday conversion)."""
        # Current time: Friday 2025-07-25 10:00:00 UTC
        current_time = datetime.datetime(2025, 7, 25, 10, 0, 0, tzinfo=ZoneInfo('UTC'))

        # Schedule for Sunday 15:30 UTC weekly
        schedule = Schedule()
        schedule.frequency.weekly.day_of_week = DayOfWeek.SUNDAY
        schedule.frequency.weekly.time.time_of_day.hours = 15
        schedule.frequency.weekly.time.time_of_day.minutes = 30
        schedule.frequency.weekly.time.time_zone.id = 'UTC'

        result = get_next_date(current_time, schedule)
        expected = datetime.datetime(2025, 7, 27, 15, 30, 0, tzinfo=ZoneInfo('UTC'))  # This Sunday

        assert result == expected

    def test_schedule_with_invalid_timezone_fallback(self):
        """Test schedule with invalid timezone falls back to UTC."""
        # Current time: 2025-07-24 10:00:00 UTC
        current_time = datetime.datetime(2025, 7, 24, 10, 0, 0, tzinfo=ZoneInfo('UTC'))

        # Schedule with invalid timezone
        schedule = Schedule()
        schedule.frequency.daily.time.time_of_day.hours = 15
        schedule.frequency.daily.time.time_of_day.minutes = 30
        schedule.frequency.daily.time.time_zone.id = 'Invalid/Timezone'

        result = get_next_date(current_time, schedule)
        expected = datetime.datetime(2025, 7, 24, 15, 30, 0, tzinfo=ZoneInfo('UTC'))

        assert result == expected

    def test_schedule_with_empty_timezone_defaults_to_utc(self):
        """Test schedule with empty timezone defaults to UTC."""
        # Current time: 2025-07-24 10:00:00 UTC
        current_time = datetime.datetime(2025, 7, 24, 10, 0, 0, tzinfo=ZoneInfo('UTC'))

        # Schedule with empty timezone
        schedule = Schedule()
        schedule.frequency.daily.time.time_of_day.hours = 15
        schedule.frequency.daily.time.time_of_day.minutes = 30
        schedule.frequency.daily.time.time_zone.id = ''

        result = get_next_date(current_time, schedule)
        expected = datetime.datetime(2025, 7, 24, 15, 30, 0, tzinfo=ZoneInfo('UTC'))

        assert result == expected

    def test_invalid_schedule_raises_error(self):
        """Test that invalid schedule (neither daily nor weekly) raises ValueError."""
        # Current time: 2025-07-24 10:00:00 UTC
        current_time = datetime.datetime(2025, 7, 24, 10, 0, 0, tzinfo=ZoneInfo('UTC'))

        # Empty schedule
        schedule = Schedule()

        with pytest.raises(ValueError):
            get_next_date(current_time, schedule)

    def test_invalid_day_of_week_raises_error(self):
        """Test that invalid day of week raises ValueError."""
        # Current time: 2025-07-24 10:00:00 UTC
        current_time = datetime.datetime(2025, 7, 24, 10, 0, 0, tzinfo=ZoneInfo('UTC'))

        # Schedule with invalid day of week
        schedule = Schedule()
        schedule.frequency.weekly.day_of_week = DayOfWeek.DAY_OF_WEEK_UNSPECIFIED
        schedule.frequency.weekly.time.time_of_day.hours = 15
        schedule.frequency.weekly.time.time_of_day.minutes = 30
        schedule.frequency.weekly.time.time_zone.id = 'UTC'

        with pytest.raises(ValueError):
            get_next_date(current_time, schedule)

    def test_cross_timezone_comparison(self):
        """Test that function works correctly when input and schedule have different timezones."""
        # Current time: 2025-07-24 10:00:00 EST (15:00 UTC)
        current_time = datetime.datetime(2025, 7, 24, 10, 0, 0, tzinfo=ZoneInfo('America/New_York'))

        # Schedule for 14:00 UTC daily (9:00 EST)
        schedule = Schedule()
        schedule.frequency.daily.time.time_of_day.hours = 14
        schedule.frequency.daily.time.time_of_day.minutes = 0
        schedule.frequency.daily.time.time_zone.id = 'UTC'

        result = get_next_date(current_time, schedule)
        expected = datetime.datetime(2025, 7, 25, 14, 0, 0, tzinfo=ZoneInfo('UTC'))  # Tomorrow in UTC

        assert result == expected
