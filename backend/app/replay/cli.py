"""Command-line interface for Season Replay, climatology, and Uncle Hussein evaluation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .service import (
    create_evidence_card,
    evaluate_season_replay,
    get_climatology_profile,
    run_uncle_hussein_comparison,
)
from .uncle_hussein import build_uh001_plans


def cmd_replay(args: argparse.Namespace) -> int:
    if args.plans:
        with open(args.plans, encoding="utf-8") as f:
            plans = json.load(f)
    else:
        # Default to UH-001 plans
        uh_plans = build_uh001_plans()
        plans = [uh_plans["R1"], uh_plans["R2"]]

    anchors = [int(y.strip()) for y in args.anchors.split(",")] if args.anchors else None
    result = evaluate_season_replay(
        plans=plans,
        anchor_years=anchors,
        template_anchor_year=args.template_year,
        data_dir=args.data,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return 0


def cmd_compare_uh(args: argparse.Namespace) -> int:
    anchors = [int(y.strip()) for y in args.anchors.split(",")] if args.anchors else None
    result = run_uncle_hussein_comparison(anchor_years=anchors, data_dir=args.data)
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return 0


def cmd_climatology(args: argparse.Namespace) -> int:
    result = get_climatology_profile(
        target_date=args.date,
        reference=args.ref,
        data_dir=args.data,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return 0


def cmd_evidence_card(args: argparse.Namespace) -> int:
    uh_plans = build_uh001_plans()
    plan_key = args.plan.upper() if args.plan.upper() in uh_plans else "R1"
    chosen_plan = uh_plans[plan_key]

    anchors = [int(y.strip()) for y in args.anchors.split(",")] if args.anchors else [2015, 2016, 2020]
    replay_res = evaluate_season_replay(
        plans=[chosen_plan],
        anchor_years=anchors,
        template_anchor_year=2026,
        data_dir=args.data,
    )

    card = create_evidence_card(
        scenario_id="UH-001",
        scenario_revision=1,
        plan_id=chosen_plan["plan_id"],
        plan_version=int(chosen_plan["plan_version"]),
        planning_result_id="plan-result-uh001-r1",
        plan_status=chosen_plan["planner_status"],
        replay_result=replay_res,
    )
    print(json.dumps(card, indent=2, ensure_ascii=False, allow_nan=False))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m backend.app.replay.cli",
        description="Mission El Gheet - Season Replay & Climatology CLI",
    )
    parser.add_argument("--data", type=Path, help="Path to Sakha climate data directory")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Replay command
    replay_p = subparsers.add_parser("replay", help="Replay agricultural plans over historical weather")
    replay_p.add_argument("--plans", type=Path, help="Path to JSON file containing list of plans")
    replay_p.add_argument("--anchors", type=str, help="Comma-separated anchor years (e.g. 2015,2016,2020)")
    replay_p.add_argument("--template-year", type=int, default=2026, help="Template anchor year (default: 2026)")
    replay_p.set_defaults(func=cmd_replay)

    # Compare UH command
    compare_p = subparsers.add_parser("compare-uh", help="Compare Uncle Hussein May 28 (R1) vs June 1 (R2)")
    compare_p.add_argument("--anchors", type=str, help="Comma-separated anchor years (e.g. 2015,2016,2020)")
    compare_p.set_defaults(func=cmd_compare_uh)

    # Climatology command
    clim_p = subparsers.add_parser("climatology", help="Get seasonal climatology quantiles for a date")
    clim_p.add_argument("--date", type=str, required=True, help="Target date YYYY-MM-DD")
    clim_p.add_argument(
        "--ref",
        type=str,
        default="historical_2001_2025",
        choices=["historical_2001_2025", "ml_fit_2001_2018"],
        help="Climatology reference baseline",
    )
    clim_p.set_defaults(func=cmd_climatology)

    # Evidence Card command
    card_p = subparsers.add_parser("evidence-card", help="Generate Climate Evidence Card for Uncle Hussein")
    card_p.add_argument("--plan", type=str, default="R1", choices=["P0", "R1", "R2"], help="UH-001 plan key")
    card_p.add_argument("--anchors", type=str, help="Comma-separated anchor years")
    card_p.set_defaults(func=cmd_evidence_card)

    parsed = parser.parse_args(argv)
    return parsed.func(parsed)


if __name__ == "__main__":
    sys.exit(main())
