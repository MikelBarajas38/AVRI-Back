#!/usr/bin/env python3
import argparse, os, sys, json, datetime as dt
from typing import Dict, Any, List, Tuple, Optional
import requests

QUESTIONS = [f"q{i}" for i in range(1, 11)]

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Descarga encuestas de /api/feedback y calcula promedio/mínimo/máximo por pregunta."
    )
    p.add_argument("--base-url", default=os.getenv("BASE_URL", "http://localhost:8000"),
                   help="Base del backend (sin /api). Ej: http://localhost:8000")
    p.add_argument("--token", default=os.getenv("API_TOKEN"),
                   help="Token DRF. También puedes ponerlo en env API_TOKEN")
    p.add_argument("--path", default="/api/feedback/",
                   help="Path del endpoint. Por defecto /api/feedback/")
    p.add_argument("--start-date", help="Fecha mínima (ISO, ej. 2025-08-01)")
    p.add_argument("--end-date", help="Fecha máxima (ISO, ej. 2025-08-31)")
    p.add_argument("--output-csv", help="Ruta CSV de salida opcional")
    return p.parse_args()

def iso_or_none(s: Optional[str]) -> Optional[dt.datetime]:
    if not s: return None
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))

def within_range(ts_iso: str, start: Optional[dt.datetime], end: Optional[dt.datetime]) -> bool:
    ts = iso_or_none(ts_iso)
    if ts is None: return False
    if start and ts < start: return False
    if end and ts > end: return False
    return True

def fetch_all(base_url: str, path: str, headers: Dict[str, str]) -> List[Dict[str, Any]]:
    """Tolera lista directa o paginación DRF (results/next)."""
    url = base_url.rstrip("/") + path
    out: List[Dict[str, Any]] = []

    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()

    if isinstance(data, list):
        return data

    # DRF paginated
    if isinstance(data, dict):
        while True:
            results = data.get("results", [])
            if not isinstance(results, list):
                raise ValueError("Respuesta inesperada: no es lista ni paginada con 'results'.")
            out.extend(results)
            next_url = data.get("next")
            if not next_url:
                break
            r = requests.get(next_url, headers=headers, timeout=30)
            r.raise_for_status()
            data = r.json()
        return out

    raise ValueError("Formato de respuesta no reconocido.")

def coerce_survey(surv: Any) -> Dict[str, Any]:
    if isinstance(surv, dict):
        return surv
    if isinstance(surv, str):
        try:
            return json.loads(surv)
        except Exception:
            return {}
    return {}

def aggregate(rows: List[Dict[str, Any]],
              start: Optional[dt.datetime],
              end: Optional[dt.datetime]) -> Tuple[Dict[str, Dict[str, float]], int]:
    # Acumuladores por pregunta
    sums = {q: 0.0 for q in QUESTIONS}
    counts = {q: 0 for q in QUESTIONS}
    mins = {q: float("inf") for q in QUESTIONS}
    maxs = {q: float("-inf") for q in QUESTIONS}
    used = 0

    for item in rows:
        completed_at = item.get("completed_at")
        if (start or end) and not within_range(completed_at or "", start, end):
            continue

        survey = coerce_survey(item.get("survey"))
        ratings = survey.get("rating_items", {}) if isinstance(survey, dict) else {}
        if not isinstance(ratings, dict):
            continue

        used += 1
        for q in QUESTIONS:
            val = ratings.get(q)
            if val is None:  # tolerar ausencias
                continue
            try:
                x = float(val)
            except Exception:
                continue
            sums[q] += x
            counts[q] += 1
            mins[q] = min(mins[q], x)
            maxs[q] = max(maxs[q], x)

    stats = {}
    for q in QUESTIONS:
        n = counts[q]
        avg = (sums[q] / n) if n > 0 else float("nan")
        mn = mins[q] if mins[q] != float("inf") else float("nan")
        mx = maxs[q] if maxs[q] != float("-inf") else float("nan")
        stats[q] = {"n": n, "avg": avg, "min": mn, "max": mx}
    return stats, used

def print_table(stats: Dict[str, Dict[str, float]], used: int, total: int) -> None:
    print(f"\nEncuestas consideradas: {used} de {total}\n")
    print(f"{'Pregunta':<6} {'N':>5} {'Promedio':>10} {'Mín':>8} {'Máx':>8}")
    print("-" * 42)
    for q in QUESTIONS:
        s = stats[q]
        avg = f"{s['avg']:.3f}" if s['n'] > 0 else "NA"
        mn  = f"{s['min']:.0f}" if s['n'] > 0 else "NA"
        mx  = f"{s['max']:.0f}" if s['n'] > 0 else "NA"
        print(f"{q:<6} {s['n']:>5} {avg:>10} {mn:>8} {mx:>8}")

def save_csv(stats: Dict[str, Dict[str, float]], path: str) -> None:
    import csv
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["question", "n", "avg", "min", "max"])
        for q in QUESTIONS:
            s = stats[q]
            w.writerow([q, s["n"], f"{s['avg']:.6f}" if s["n"]>0 else "", s["min"] if s["n"]>0 else "", s["max"] if s["n"]>0 else ""])
    print(f"\nCSV escrito en: {path}")

def main():
    args = parse_args()
    if not args.token:
        print("ERROR: falta --token o variable de entorno API_TOKEN", file=sys.stderr)
        sys.exit(1)

    headers = {"Authorization": f"Token {args.token}", "Accept": "application/json"}
    try:
        rows = fetch_all(args.base_url, args.path, headers)
    except requests.HTTPError as e:
        print(f"HTTP error: {e} (respuesta: {getattr(e.response, 'text', '')[:300]})", file=sys.stderr)
        sys.exit(2)

    start = iso_or_none(args.start_date)
    end = iso_or_none(args.end_date)

    stats, used = aggregate(rows, start, end)
    print_table(stats, used, len(rows))

    if args.output_csv:
        save_csv(stats, args.output_csv)

if __name__ == "__main__":
    main()
