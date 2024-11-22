from datetime import timedelta, datetime


class TimeData:
    @staticmethod
    def get_tz_now(timezone):
        return datetime.now(timezone)

    @staticmethod
    def get_utc_now():
        return datetime.utcnow()

    @staticmethod
    def get_tomorrow(now):
        return now + timedelta(days=1)

    @staticmethod
    def get_yesterday(now):
        return now - timedelta(days=1)

    @classmethod
    def get_yesterday_tz(cls, timezone):
        return cls.get_yesterday(cls.get_tz_now(timezone))

    @classmethod
    def get_yesterday_utc(cls):
        return cls.get_yesterday(cls.get_utc_now())

    @classmethod
    def get_tomorrow_tz(cls, timezone):
        return cls.get_tomorrow(cls.get_tz_now(timezone))

    @classmethod
    def get_tomorrow_utc(cls):
        return cls.get_tomorrow(cls.get_utc_now())
