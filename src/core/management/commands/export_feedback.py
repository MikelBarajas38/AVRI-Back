from __future__ import annotations

import csv
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, Optional

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db.models import Q
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth

try:
    from zoneinfo import ZoneInfo  # py3.9+
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore

from core.models import SatisfactionSurveyResponse  # feedback model
# Fields: user(FK), version(str), survey(JSON), completed_at(datetime)  # noqa
# (See core/models.py)  # noqa


@dataclass
class Scores:
    q: Dict[str, Optional[int]]
    total: Optional[int]
    sus: Optional[float]


def _coerce_int(v: Any) -> Optional[int]:
    try:
        i = int(v)
        return i if 0 <= i <= 5 else None
    except Exception:
        return None


def _extract_scores(survey: Dict[str, Any]) -> Scores:
    """
    Accepts both shapes:
      A) {"q1":..,"q2":.., ... "q10":.., "comments": "..."}
      B) {"rating_items": {"q1":..,"q2":..,...,"q10":..}, "comments": "...", "meta": {...}}
    """
    rating = survey.get("rating_items") if isinstance(survey.get("rating_items"), dict) else survey
    qs = {}
    for i in range(1, 11):
        key = f"q{i}"
        qs[key] = _coerce_int(rating.get(key))

    # total (sum of answered) and SUS (0–100); compute only if all 10 present
    if all(qs[f"q{i}"] is not None for i in range(1, 11)):
        total = sum(qs.values())  # type: ignore[arg-type]
        # SUS: sum( (q_odd - 1) + (5 - q_even) ) * 2.5
        sus_raw = 0
        for i in range(1, 11):
            v = qs[f"q{i}"] or 0
            if i % 2 == 1:
                sus_raw += (v - 1)
            else:
                sus_raw += (5 - v)
        sus = round(sus_raw * 2.5, 1)
    else:
        total, sus = None, None

    return Scores(q=qs, total=total, sus=sus)


def _iter_rows(
    qs: Iterable[SatisfactionSurveyResponse],
    tzname: str,
) -> Iterable[Dict[str, Any]]:
    tz = ZoneInfo(tzname) if ZoneInfo else None
    for r in qs:
        # timestamps
        dt = r.completed_at
        if tz:
            dt = timezone.make_naive(dt, timezone.utc).replace(tzinfo=timezone.utc).astimezone(tz)
        iso_dt = dt.isoformat()

        survey = r.survey or {}
        scores = _extract_scores(survey)
        comments = survey.get("comments") or ""
        meta = survey.get("meta") if isinstance(survey.get("meta"), dict) else {}
        session_id = meta.get("session_id") or survey.get("session_id")
        locale = meta.get("locale") or survey.get("locale")

        user = getattr(r, "user", None)
        is_anon = bool(getattr(user, "is_anonymous", False))  # custom field in your User model

        yield {
            "id": r.id,
            "user_id": getattr(user, "id", None),
            "is_anonymous": is_anon,
            "version": r.version,
            "completed_at": iso_dt,
            "session_id": session_id,
            "locale": locale,
            **scores.q,  # q1..q10
            "total": scores.total,
            "sus": scores.sus,
            "comments": comments,
        }


class Command(BaseCommand):
    help = (
        "Export satisfaction survey feedback to CSV.\n"
        "Raw export by default; use --summary to aggregate."
    )

    def add_arguments(self, parser):
        parser.add_argument("--from", dest="date_from", help="ISO date/time (UTC or --tz) e.g. 2025-08-01 or 2025-08-01T00:00:00")
        parser.add_argument("--to", dest="date_to", help="ISO date/time (UTC or --tz)")
        parser.add_argument("--tz", dest="tz", default=timezone.get_default_timezone_name(), help="Timezone name (default from settings)")
        parser.add_argument("--outfile", dest="outfile", help="Write CSV to this path (default: stdout)")
        parser.add_argument("--anonymous-only", action="store_true", help="Only include anonymous responses")
        parser.add_argument("--user-id", type=int, dest="user_id", help="Only include this user id")
        parser.add_argument("--summary", choices=["day", "week", "month"], help="Aggregate by period instead of raw rows")
        parser.add_argument("--delimiter", default=",", help="CSV delimiter (default ,)")
        parser.add_argument("--no-header", action="store_true", help="Do not write header row")

    def handle(self, *args, **opts):
        tzname: str = opts["tz"]
        delim: str = opts["delimiter"]

        # Parse date filters (assume tz of --tz)
        def parse_dt(s: Optional[str]) -> Optional[datetime]:
            if not s:
                return None
            try:
                # handle date-only
                if "T" not in s and " " not in s:
                    dt = datetime.fromisoformat(s + "T00:00:00")
                else:
                    dt = datetime.fromisoformat(s)
                if ZoneInfo:
                    dt = dt.replace(tzinfo=ZoneInfo(tzname))
                    return dt.astimezone(timezone.utc)
                else:  # fallback — treat as naive UTC
                    return dt
            except Exception as e:
                raise CommandError(f"Invalid date/time: {s}") from e

        dt_from_utc = parse_dt(opts["date_from"])
        dt_to_utc = parse_dt(opts["date_to"])

        qs = SatisfactionSurveyResponse.objects.all().order_by("completed_at")
        if dt_from_utc:
            qs = qs.filter(completed_at__gte=dt_from_utc)
        if dt_to_utc:
            qs = qs.filter(completed_at__lt=dt_to_utc)

        if opts["anonymous_only"]:
            qs = qs.filter(user__is_anonymous=True)
        if opts["user_id"]:
            qs = qs.filter(user_id=opts["user_id"])

        # Output file
        outfh = open(opts["outfile"], "w", newline="", encoding="utf-8") if opts["outfile"] else sys.stdout
        close_needed = outfh is not sys.stdout

        try:
            writer = csv.writer(outfh, delimiter=delim)

            if not opts["summary"]:
                headers = [
                    "id", "user_id", "is_anonymous", "version", "completed_at",
                    "session_id", "locale",
                    "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10",
                    "total", "sus", "comments",
                ]
                if not opts["no_header"]:
                    writer.writerow(headers)

                for row in _iter_rows(qs, tzname=tzname):
                    writer.writerow([row.get(h, "") for h in headers])
                return

            # ---- summary mode ----
            trunc = {"day": TruncDay, "week": TruncWeek, "month": TruncMonth}[opts["summary"]]
            tzinfo = ZoneInfo(tzname) if ZoneInfo else None

            # We’ll aggregate SUS only for complete responses (all q1..q10 present)
            raw_rows = list(_iter_rows(qs, tzname=tzname))
            # Group by period key
            def period_key(iso_str: str) -> str:
                dt = datetime.fromisoformat(iso_str)
                if opts["summary"] == "day":
                    return dt.date().isoformat()
                if opts["summary"] == "week":
                    # ISO week
                    y, w, _ = dt.isocalendar()
                    return f"{y}-W{w:02d}"
                # month
                return f"{dt.year}-{dt.month:02d}"

            buckets: Dict[str, list[Dict[str, Any]]] = {}
            for r in raw_rows:
                key = period_key(r["completed_at"])
                buckets.setdefault(key, []).append(r)

            headers = [
                "period", "count",
                "avg_q1","avg_q2","avg_q3","avg_q4","avg_q5",
                "avg_q6","avg_q7","avg_q8","avg_q9","avg_q10",
                "avg_total","avg_sus"
            ]
            if not opts["no_header"]:
                writer.writerow(headers)

            def avg(vals: Iterable[Optional[float]]) -> Optional[float]:
                nums = [float(v) for v in vals if isinstance(v, (int, float))]
                return round(sum(nums)/len(nums), 2) if nums else None

            for period, items in sorted(buckets.items()):
                row = [period, len(items)]
                for i in range(1, 11):
                    row.append(avg(r.get(f"q{i}") for r in items))
                row.append(avg(r.get("total") for r in items))
                row.append(avg(r.get("sus") for r in items))
                writer.writerow(row)

        finally:
            if close_needed:
                outfh.close()
