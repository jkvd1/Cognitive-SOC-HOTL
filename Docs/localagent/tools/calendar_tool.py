"""ICS calendar tool — read/write events in workspace/calendar/."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import config

try:
    from icalendar import Calendar, Event
    from dateutil import parser as dateutil_parser
    _HAS_ICAL = True
except ImportError:
    _HAS_ICAL = False

_CAL_FILE = config.CALENDAR_DIR / "events.ics"


def _load_calendar() -> "Calendar":
    config.CALENDAR_DIR.mkdir(parents=True, exist_ok=True)
    if _CAL_FILE.exists() and _HAS_ICAL:
        try:
            return Calendar.from_ical(_CAL_FILE.read_bytes())
        except Exception:
            pass
    cal = Calendar()
    if _HAS_ICAL:
        cal.add("prodid", "-//LocalAgent//EN")
        cal.add("version", "2.0")
    return cal


def _save_calendar(cal: "Calendar") -> None:
    config.CALENDAR_DIR.mkdir(parents=True, exist_ok=True)
    _CAL_FILE.write_bytes(cal.to_ical())


def calendar_tool(
    operation: str,
    title: str | None = None,
    start: str | None = None,
    end: str | None = None,
    description: str | None = None,
    event_id: str | None = None,
    days_ahead: int = 7,
) -> str:
    if not _HAS_ICAL:
        return "[ERROR] icalendar / python-dateutil not installed."

    if operation == "list":
        cal = _load_calendar()
        now = datetime.now(timezone.utc)
        horizon = now + timedelta(days=days_ahead)
        events: list[str] = []
        for component in cal.walk():
            if component.name != "VEVENT":
                continue
            ev_start = component.get("dtstart")
            if ev_start is None:
                continue
            dt = ev_start.dt
            if not hasattr(dt, "tzinfo"):
                dt = datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc)
            elif dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if now <= dt <= horizon:
                summary = str(component.get("summary", "(no title)"))
                uid = str(component.get("uid", "?"))
                desc = str(component.get("description", ""))
                events.append(
                    f"📅 {dt.strftime('%Y-%m-%d %H:%M')} | [{uid[:8]}] {summary}"
                    + (f"\n   {desc}" if desc else "")
                )
        if not events:
            return f"No events in the next {days_ahead} days."
        return f"📅 **Upcoming Events ({days_ahead}d)**\n\n" + "\n\n".join(events)

    if operation == "add":
        if not title or not start:
            return "[ERROR] title and start are required for add."
        cal = _load_calendar()
        event = Event()
        event.add("uid", str(uuid.uuid4()))
        event.add("summary", title)
        try:
            dt_start = dateutil_parser.parse(start)
            dt_end = dateutil_parser.parse(end) if end else dt_start + timedelta(hours=1)
        except Exception as exc:
            return f"[ERROR] Date parse failed: {exc}"
        event.add("dtstart", dt_start)
        event.add("dtend", dt_end)
        if description:
            event.add("description", description)
        event.add("dtstamp", datetime.now(timezone.utc))
        cal.add_component(event)
        _save_calendar(cal)
        return f"[OK] Event added: {title!r} at {start}"

    if operation == "delete":
        if not event_id:
            return "[ERROR] event_id required for delete."
        cal = _load_calendar()
        new_cal = Calendar()
        new_cal.add("prodid", "-//LocalAgent//EN")
        new_cal.add("version", "2.0")
        deleted = False
        for component in cal.walk():
            if component.name == "VEVENT":
                uid = str(component.get("uid", ""))
                if uid.startswith(event_id):
                    deleted = True
                    continue
            if component.name != "VCALENDAR":
                new_cal.add_component(component)
        if not deleted:
            return f"[ERROR] Event not found: {event_id!r}"
        _save_calendar(new_cal)
        return f"[OK] Event deleted: {event_id!r}"

    return f"[ERROR] Unknown operation: {operation!r}"
