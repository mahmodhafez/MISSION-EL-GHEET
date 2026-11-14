"""Command-line interface for Season Replay, planting-window comparison and climatology."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

from .service import (
    compare_sowing_windows,
    create_evidence_card,
    evaluate_season_replay,
    get_climatology_profile,
    run_uncle_hussein_comparison,
)

REPO = Path(__file__).resolve().parents[3]
PLANNER_FIXTURE = REPO / "packages" / "meg-core" / "tools" / "fixtures" / "uh001.json"


def _emit(result: dict, as_text: bool) -> None:
    if as_text and result.get("farmer_summary"):
        print(result["label"]["en"])
        print(result["label"]["ar"])
        for w in result["windows"]:
            print(f"- {w['window_id']} sow {w['sow_date']} window {w['planned_window'][0]}..{w['planned_window'][1]}"
                  f" planner status: {w['planner_status']}")
        a = result["layer_a_historical"]
        print(f"Historical years used: {len(a['years_used'])} ({a['years_used'][0]}-{a['years_used'][-1]}); "
              f"excluded: {len(a['years_excluded'])}")
        for item in result["farmer_summary"]:
            print(f"\n[{item['kind']}]\n{item['en']}\n{item['ar']}")
        return
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))


def _years(text: str | None) -> list[int] | None:
    return [int(y.strip()) for y in text.split(",")] if text else None


def uh001_planner_statuses() -> dict[str, str] | None:
    """Run the real Promise Test on the planner's UH-001 fixture; None if the planner is absent."""
    tools = REPO / "packages" / "meg-core" / "tools"
    if not PLANNER_FIXTURE.is_file():
        return None
    sys.path.insert(0, str(tools))
    try:
        import planner_cli  # type: ignore[import-not-found]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = planner_cli.main(["plan", str(PLANNER_FIXTURE), "--json"])
        if code != 0:
            return None
        result = json.loads(out.getvalue())["result"]
    finally:
        sys.path.remove(str(tools))
    statuses = {"2027-05-15": result["current"]["status"]}
    for group in ("feasible_alternatives", "review_investigations", "rejected_candidates"):
        for candidate in result[group]:
            statuses[candidate["plan"][1]["sowing_date"]["value"]] = candidate["evaluation"]["status"]
    return statuses


def cmd_replay(args: argparse.Namespace) -> int:
    with open(args.plans, encoding="utf-8") as f:
        plans = json.load(f)
    result = evaluate_season_replay(plans=plans, anchor_years=_years(args.anchors),
                                    template_anchor_year=args.template_year, data_dir=args.data)
    _emit(result, False)
    return 0


def cmd_windows(args: argparse.Namespace) -> int:
    result = compare_sowing_windows([d.strip() for d in args.dates.split(",")], window_days=args.days,
                                    years=_years(args.years), data_dir=args.data)
    _emit(result, args.text)
    return 0


def cmd_compare_uh(args: argparse.Namespace) -> int:
    statuses = uh001_planner_statuses()
    result = run_uncle_hussein_comparison(planner_statuses=statuses, years=_years(args.years), data_dir=args.data)
    _emit(result, args.text)
    return 0


def cmd_climatology(args: argparse.Namespace) -> int:
    _emit(get_climatology_profile(target_date=args.date, reference=args.ref, data_dir=args.data), False)
    return 0


def cmd_evidence_card(args: argparse.Namespace) -> int:
    statuses = uh001_planner_statuses() or {}
    if args.sow not in statuses:
        print(json.dumps({"error": "planner_status_unavailable", "sow_date": args.sow}))
        return 2
    comparison = run_uncle_hussein_comparison(planner_statuses=statuses, data_dir=args.data)
    window = next(w for w in comparison["windows"] if w["sow_date"] == args.sow)
    across = comparison["layer_a_historical"]["windows"][window["window_id"]]["across_years"]
    years = comparison["layer_a_historical"]["years_used"]
    summary = {"analysis_kind": comparison["analysis_kind"], "label": comparison["label"],
               "window": window["planned_window"], "years_used": len(years),
               "years_range": f"{years[0]}-{years[-1]}" if years else None,
               "tmax_mean_c": across["tmax_mean_c"], "et0_total_mm": across["et0_total_mm"],
               "climatology": comparison["layer_b_climatology"]["windows"][window["window_id"]]["summary"],
               "status": comparison["status"]}
    card = create_evidence_card(scenario_id="UH-001", scenario_revision=1, plan_id=f"UH001-sow-{args.sow}",
                                plan_version=1, planning_result_id="uh001-promise-test",
                                plan_status=statuses[args.sow], replay_result=None,
                                outstanding_checks=["Changed maize harvest, crop end and field release are unknown."])
    card["climate_evidence"] = summary
    _emit(card, False)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m backend.app.replay.cli",
                                     description="MISSION EL GHEET - Season Replay & Climatology CLI")
    parser.add_argument("--data", type=Path, help="Sakha climate release directory (or set MEG_CLIMATE_DATA_DIR)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("replay", help="Replay explicit planner season windows over historical years")
    p.add_argument("--plans", type=Path, required=True, help="JSON list of plans with explicit sow/crop-end dates")
    p.add_argument("--anchors", type=str, help="Comma-separated anchor years")
    p.add_argument("--template-year", type=int, default=2026)
    p.set_defaults(func=cmd_replay)

    p = sub.add_parser("windows", help="Compare equal-length windows starting at sow dates")
    p.add_argument("--dates", required=True, help="Comma-separated YYYY-MM-DD sow dates; first is the reference")
    p.add_argument("--days", type=int, default=14)
    p.add_argument("--years", type=str, help="Comma-separated historical years (default 2001-2025)")
    p.add_argument("--text", action="store_true", help="Readable bilingual summary instead of JSON")
    p.set_defaults(func=cmd_windows)

    p = sub.add_parser("compare-uh", help="UH-001: 28 May vs 1 June 14-day windows, real Promise Test statuses")
    p.add_argument("--years", type=str)
    p.add_argument("--text", action="store_true")
    p.set_defaults(func=cmd_compare_uh)

    p = sub.add_parser("climatology", help="Climatology quantiles for one date")
    p.add_argument("--date", required=True)
    p.add_argument("--ref", default="ml_fit_2001_2018", choices=["ml_fit_2001_2018", "historical_2001_2025"])
    p.set_defaults(func=cmd_climatology)

    p = sub.add_parser("evidence-card", help="Climate evidence card for one UH-001 sowing date")
    p.add_argument("--sow", default="2027-05-28")
    p.set_defaults(func=cmd_evidence_card)

    parsed = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252, which cannot print Arabic.
        sys.stdout.reconfigure(encoding="utf-8")
    return parsed.func(parsed)


if __name__ == "__main__":
    sys.exit(main())
