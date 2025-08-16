from backend.db import db_session
from backend.models import AnalyticsEvent

def log_event(event_type: str, payload: dict | None = None):
    evt = AnalyticsEvent(event_type=event_type, payload=payload or {})
    db_session.add(evt)
    db_session.commit()
