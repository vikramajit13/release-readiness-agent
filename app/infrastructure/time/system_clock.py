from datetime import datetime, timezone

from app.ports.services.clock_port import ClockPort


class SystemClock(ClockPort):
    def utcnow(self) -> datetime:
        return datetime.now(timezone.utc)