"""Regenerate the manual-test JSON fixtures from the SAME builders the unit tests use.

    python -I tools/build_fixtures.py

No new agricultural values are introduced here: UH-001 comes from tests/test_constraints.uh001()
(recovered reference intentions + open review gates); everything else is SYNTHETIC-ONLY.
"""

from dataclasses import replace
from datetime import date, timedelta
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tools"))

from planner_cli import encode  # noqa: E402
from test_constraints import synthetic, uh001  # noqa: E402
from test_generation import date_choice, support_date  # noqa: E402
from meg_core.planner._types import ExplorationChoice, IndependentFact, SowingWindowRule  # noqa: E402

OUT = ROOT / "tools" / "fixtures"


def write(name, note, snapshot, kb, choices, confirm=True):
    data = {"_note": note, "confirm_exploration": confirm, "policy": {"raw_budget": 256},
            "exploration": {"choices": encode(choices), "catalogue_choices": []},
            "snapshot": encode(snapshot), "kb": encode(kb)}
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", OUT / name)


def widened(kb):
    # Same SYNTHETIC broadening as tests/test_generation.py GenerationTests.setUp.
    return replace(kb, rules=tuple(replace(r, start=r.start - timedelta(days=45), end=r.end + timedelta(days=45))
                                   if isinstance(r, SowingWindowRule) else r for r in kb.rules))


def main():
    _, snapshot, kb = uh001()
    independent = tuple(IndependentFact(f"s{i}", "preparation_days_after_release",
                                        ("crop_id", "profile_id", "next.crop_id", "next.profile_id")) for i in range(1, 4))
    snapshot = replace(snapshot, input=replace(snapshot.input, independent_facts=independent))
    write("uh001.json",
          "UH-001 reference (illustrative, docs/product/reference-scenario.md). The two S2 sowing dates are the "
          "documented farmer investigations, supplied as exploration input. Expect: current REJECTED "
          "(sowing_before_protected_cut), two NEEDS_REVIEW investigations, ZERO feasible. Not runtime agronomy.",
          snapshot, kb, (date_choice("2027-05-28", "2027-06-01"),
                         ExplorationChoice("s4-maize", "s4", "crop_id", ("grain_maize",))))

    current, snapshot, kb = synthetic()
    kb = widened(kb)
    write("synthetic-four-season.json",
          "SYNTHETIC-ONLY algorithm fixture. One-day sowing shifts permitted in all four seasons; exact "
          "endpoint mappings for shifted dates are absent, so endpoints stay unknown (NEEDS_REVIEW) or collide (REJECTED).",
          snapshot, kb, tuple(date_choice((s.sowing_date.value + timedelta(days=1)).isoformat(),
                                          sid=s.season_id, cid=s.season_id) for s in current))

    for day in (date(2031, 5, 29), date(2031, 5, 30)):
        kb = support_date(kb, current[1], day)
    write("synthetic-mixed.json",
          "SYNTHETIC-ONLY algorithm fixture. Exact synthetic calendars exist for S2 on 2031-05-29/30 only "
          "(FEASIBLE); 2031-06-03 lacks a mapping (NEEDS_REVIEW); S3 on 2031-05-19 collides (REJECTED); "
          "an S4 crop absent from the catalogue is blocked (search INCOMPLETE).",
          snapshot, kb, (date_choice("2031-05-29", "2031-05-30", "2031-06-03"),
                         date_choice("2031-05-19", sid="s3", cid="s3-early"),
                         ExplorationChoice("s4-absent", "s4", "crop_id", ("absent-crop",))))


if __name__ == "__main__":
    main()
