"""
Generate a CSV for the application, in base of the feedback answer of the users
"""
import csv
import json
import sys
from datetime import datetime, time
from typing import Dict, Any, Iterable

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils import timezone
from django.conf import settings

from core.models import SatisfactionSurveyResponse


def _parse_date(date_str: str, is_end: bool = False):
    """
    Parse ISO-like date strings:
      - 'YYYY-MM-DD' - make aware at start/end of day
      - 'YYYY-MM-DDTHH:MM[:SS]' - make aware as given
    """
    if not date_str:
        return None
    try:
        dt = datetime.fromisoformat(date_str)
    except ValueError:
        dt = datetime.fromisoformat(date_str[:10])
        if is_end:
            dt = datetime.combine(dt.date(), time(23, 59, 59))
    if timezone.is_naive(dt):
        tz = timezone.get_default_timezone()
        dt = timezone.make_aware(dt, tz)
    return dt


def _flatten_json(d: Any, parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    """
    Flatten arbitrarily nested JSON into a single dict with dotted keys.
    Arrays are JSON-serialized to keep one column per question key.
    """
    flat = {}
    if isinstance(d, dict):
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else str(k)
            flat.update(_flatten_json(v, new_key, sep=sep))
    elif isinstance(d, list):
        flat[parent_key] = json.dumps(d, ensure_ascii=False)
    else:
        flat[parent_key] = d
    return flat


class Command(BaseCommand):
    help = (
        "Export SatisfactionSurveyResponse data to CSV. "
        "Optionally compute simple per-question value counts (a second CSV)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--from",
            dest="date_from",
            help="Start datetime (inclusive). Accepts 'YYYY-MM-DD' or ISO 'YYYY-MM-DDTHH:MM[:SS]'.",
        )
        parser.add_argument(
            "--to",
            dest="date_to",
            help="End datetime (inclusive). Accepts 'YYYY-MM-DD' or ISO 'YYYY-MM-DDTHH:MM[:SS]'.",
        )
        parser.add_argument(
            "--survey-version",
            dest="survey_version",
            help="Filter by survey version (exact match).",
        )
        parser.add_argument(
            "--outfile",
            dest="outfile",
            help="Path to write the CSV. Defaults to stdout if omitted.",
        )
        parser.add_argument(
            "--delimiter",
            dest="delimiter",
            default=",",
            help="CSV delimiter (default ',').",
        )
        parser.add_argument(
            "--encoding",
            dest="encoding",
            default="utf-8",
            help="CSV encoding (default 'utf-8').",
        )
        parser.add_argument(
            "--summary",
            action="store_true",
            help="Also write per-question value counts to '<outfile>.summary.csv' (requires --outfile).",
        )
        parser.add_argument(
            "--limit-keys",
            dest="limit_keys",
            nargs="*",
            help="Optional list of survey keys to include (dotted notation). Others are ignored.",
        )

    def handle(self, *args, **options):
        date_from = _parse_date(options.get("date_from"))
        date_to = _parse_date(options.get("date_to"), is_end=True)
        version = options.get("version")
        outfile = options.get("outfile")
        delimiter = options.get("delimiter") or ","
        encoding = options.get("encoding") or "utf-8"
        do_summary = options.get("summary")
        limit_keys = set(options.get("limit_keys") or [])

        if do_summary and not outfile:
            raise CommandError("--summary requires --outfile so we can create a second CSV.")

        qs = SatisfactionSurveyResponse.objects.all().select_related("user")

        if date_from:
            qs = qs.filter(completed_at__gte=date_from)
        if date_to:
            qs = qs.filter(completed_at__lte=date_to)
        if version:
            qs = qs.filter(version=version)

        if not qs.exists():
            self.stdout.write(self.style.WARNING("No survey responses match the given filters."))
            return

        dynamic_keys = set()
        flattened_rows = []

        for resp in qs.iterator(chunk_size=1000):
            survey_json = resp.survey or {}
            flat = _flatten_json(survey_json)

            if limit_keys:
                flat = {k: v for k, v in flat.items() if k in limit_keys}
            dynamic_keys.update(flat.keys())

            row = {
                "response_id": resp.pk,
                "user_id": getattr(resp.user, "id", None),
                "user_email": getattr(resp.user, "email", "") or "",
                "version": resp.version,
                "completed_at": timezone.localtime(resp.completed_at).isoformat(),
                **flat,
            }
            flattened_rows.append(row)

        fixed_cols = ["response_id", "user_id", "user_email", "version", "completed_at"]
        dynamic_cols = sorted(dynamic_keys)
        headers = fixed_cols + dynamic_cols

        if outfile:
            out_stream = open(outfile, "w", newline="", encoding=encoding)
            close_after = True
        else:
            out_stream = sys.stdout
            close_after = False

        writer = csv.DictWriter(out_stream, fieldnames=headers, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for row in flattened_rows:
            for k in dynamic_cols:
                row.setdefault(k, "")
            writer.writerow(row)

        if close_after:
            out_stream.close()

        self.stdout.write(self.style.SUCCESS(f"Exported {len(flattened_rows)} responses."))

        if do_summary:
            summary_counts = {}  
            for row in flattened_rows:
                for k in dynamic_cols:
                    val = row.get(k, "")
                    if isinstance(val, (dict, list)):
                        val = json.dumps(val, ensure_ascii=False)
                    val = "" if val is None else str(val)
                    summary_counts.setdefault(k, {}).setdefault(val, 0)
                    summary_counts[k][val] += 1

            summary_path = outfile + ".summary.csv"
            with open(summary_path, "w", newline="", encoding=encoding) as sf:
                s_writer = csv.writer(sf, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
                s_writer.writerow(["question_key", "answer_value", "count"])
                for key in sorted(summary_counts.keys()):
                    for value, count in sorted(summary_counts[key].items(), key=lambda x: (-x[1], x[0])):
                        s_writer.writerow([key, value, count])

            self.stdout.write(self.style.SUCCESS(f"Wrote summary counts - {summary_path}"))
