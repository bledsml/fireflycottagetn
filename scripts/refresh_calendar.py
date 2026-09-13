"""Rebuild calendar.json (availability + per-date minimum stay) from the Hospitable Public API.

Runs in GitHub Actions before each deploy (see ops/deploy-workflow.yml), or locally. Needs the HOSPITABLE_TOKEN repository secret
(read-only scope is enough). If the secret is missing, the committed calendar.json is left
as-is; the website ignores calendar data older than 72 hours, so guests never see stale
bookings presented as fact.
"""
import datetime as dt
import json
import os
import sys
import urllib.request

PROPERTY = os.environ.get("HOSPITABLE_PROPERTY", "6eaa277a-efec-4ea9-b063-38fb417c8491")
TOKEN = os.environ.get("HOSPITABLE_TOKEN", "").strip()
OUT = os.path.join(os.path.dirname(__file__), "..", "calendar.json")


def main() -> int:
    if not TOKEN:
        print("::warning::HOSPITABLE_TOKEN secret is not set; keeping the existing calendar.json")
        return 0
    start = dt.date.today()
    end = start + dt.timedelta(days=365)
    url = (f"https://public.api.hospitable.com/v2/properties/{PROPERTY}/calendar"
           f"?start_date={start}&end_date={end}")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}",
                                               "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = json.load(r)
    except Exception as exc:  # keep the last good file rather than publishing an empty calendar
        print(f"::warning::Hospitable calendar fetch failed ({exc}); keeping the existing calendar.json")
        return 0
    data = body.get("data")
    raw = data.get("days", []) if isinstance(data, dict) else (data or [])
    days = [{"date": d["date"],
             "open": bool((d.get("status") or {}).get("available")),
             "min": d.get("min_stay") or 1,
             "noCheckIn": bool(d.get("closed_for_checkin"))} for d in raw]
    if not days:
        print("::warning::Hospitable returned no days; keeping the existing calendar.json")
        return 0
    payload = {"configured": True,
               "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
               "days": days}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, separators=(",", ":"))
    print(f"calendar.json rebuilt: {len(days)} days, {sum(d['open'] for d in days)} open")
    return 0


if __name__ == "__main__":
    sys.exit(main())
