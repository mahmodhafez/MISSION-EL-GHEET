"""Manual-test CLI for the standalone planner (Milestones 1 and 2).

Runs the REAL meg_core planner: constraints.evaluate (Promise Test), scope.prepare_scope
and service.plan. No FastAPI, database, weather, forecast or ML dependency. It prints
what the planner returned; it never edits statuses or adds evidence.

    python -I tools/planner_cli.py check   tools/fixtures/uh001.json
    python -I tools/planner_cli.py preview tools/fixtures/uh001.json
    python -I tools/planner_cli.py plan    tools/fixtures/uh001.json [--json] [--details] [--all-checks] [--no-confirm]

Fixture JSON keys: "snapshot" (ScenarioSnapshot), "kb" (KnowledgeBase), optional
"exploration" {"choices": [...], "catalogue_choices": [...]}, optional
"confirm_exploration" (bool) and "policy" (SearchPolicy fields). Rules and choices carry a
"type" key naming the private class (e.g. "CalendarRule", "ExplorationChoice").
"confirm_exploration": true stands in for the farmer's explicit confirmation of the
previewed scope; it is a manual-test action, not something the planner infers.
"""

from __future__ import annotations

import argparse
from dataclasses import fields, is_dataclass, replace
from datetime import date
import json
from pathlib import Path
import sys
import types
import typing

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from meg_core.planner import _types, constraints  # noqa: E402
from meg_core.planner._types import ScopeRequest, SearchPolicy  # noqa: E402
from meg_core.planner._validation import InputValidationError  # noqa: E402
from meg_core.planner.scope import prepare_scope  # noqa: E402
from meg_core.planner.service import plan as plan_service  # noqa: E402

SYNTHETIC_SOURCE = "SYNTHETIC-ONLY"
DETAIL = {"level": "summary"}
TAGGED = (_types.Rule, _types.ExplorationChoice, _types.DateRangeChoice)


# ---------------------------------------------------------------- JSON <-> private types
def encode(value):
    if is_dataclass(value):
        out = {"type": type(value).__name__} if isinstance(value, TAGGED) else {}
        out.update({f.name: encode(getattr(value, f.name)) for f in fields(value) if f.init})
        return out
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, typing.Mapping):
        return {k: encode(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [encode(v) for v in value]
    return value


def decode(hint, data, path="$", typevars=None):
    typevars = typevars or {}
    if isinstance(hint, typing.TypeVar):
        hint = typevars.get(hint, typing.Any)
    if hint is typing.Any:
        return data
    origin, args = typing.get_origin(hint), typing.get_args(hint)
    if origin in (typing.Union, types.UnionType):
        if data is None:
            return None
        if isinstance(data, dict) and "type" in data:
            return decode(getattr(_types, data["type"]), data, path)
        options = [a for a in args if a is not type(None)]
        resolved = [typevars.get(a, a) if isinstance(a, typing.TypeVar) else a for a in options]
        return decode(resolved[0], data, path, typevars) if len(resolved) == 1 else data
    if origin is typing.Literal:
        return data
    if origin is tuple:
        if isinstance(data, dict):  # {"key": Fact} shorthand for (key, Fact) pairs
            data = list(data.items())
        if not isinstance(data, list):
            raise ValueError(f"{path}: expected a list")
        if len(args) == 2 and args[1] is Ellipsis:
            return tuple(decode(args[0], v, f"{path}[{i}]", typevars) for i, v in enumerate(data))
        return tuple(decode(a, v, f"{path}[{i}]", typevars) for i, (a, v) in enumerate(zip(args, data)))
    if origin is not None and is_dataclass(origin):
        params = getattr(origin, "__parameters__", ())
        return decode(origin, data, path, dict(zip(params, args)))
    if hint is date:
        return date.fromisoformat(data) if isinstance(data, str) else data
    if isinstance(hint, type) and is_dataclass(hint):
        if not isinstance(data, dict):
            raise ValueError(f"{path}: expected an object for {hint.__name__}")
        cls = getattr(_types, data["type"]) if "type" in data else hint
        hints = typing.get_type_hints(cls, vars(_types))
        names = {f.name for f in fields(cls) if f.init}
        unknown = set(data) - names - {"type"}
        if unknown:
            raise ValueError(f"{path}: unknown field(s) {sorted(unknown)} for {cls.__name__}")
        kwargs = {k: decode(hints[k], v, f"{path}.{k}", typevars) for k, v in data.items() if k != "type"}
        try:
            return cls(**kwargs)
        except TypeError as error:
            raise ValueError(f"{path}: {cls.__name__}: {error}") from None
    return data


def load(path):
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    snapshot = decode(_types.ScenarioSnapshot, raw["snapshot"], "$.snapshot")
    kb = decode(_types.KnowledgeBase, raw["kb"], "$.kb")
    exploration = raw.get("exploration", {})
    hint = tuple[_types.ExplorationChoice | _types.DateRangeChoice, ...]
    choices = decode(hint, exploration.get("choices", []), "$.exploration.choices")
    catalogue = decode(tuple[_types.CatalogueChoice, ...], exploration.get("catalogue_choices", []),
                       "$.exploration.catalogue_choices")
    policy = SearchPolicy(**raw.get("policy", {}))
    return raw, snapshot, kb, choices, catalogue, policy, bool(raw.get("confirm_exploration", False))


# ---------------------------------------------------------------- readable output
def is_synthetic(*objects):
    return SYNTHETIC_SOURCE in json.dumps([encode(o) for o in objects])


def status_label(status):
    return {"needs_review": "NEEDS_REVIEW", "rejected": "REJECTED", "feasible": "FEASIBLE"}.get(status, status)


def refs_text(refs):
    return ", ".join(f"{r.source_id} [{r.locator}]" for r in refs) or "(none)"


def fact_text(fact):
    value = fact.value.isoformat() if isinstance(fact.value, date) else fact.value
    shown = f"{value}{' ' + fact.unit if fact.unit and value is not None else ''}" if value is not None \
        else f"UNKNOWN ({fact.unknown_reason})"
    return f"{shown}  <{fact.origin}; evidence={fact.evidence_status}; {fact.confirmation_status}>"


def print_evaluation(evaluation, indent, all_checks):
    pad = " " * indent
    print(f"{pad}Status: {status_label(evaluation.status)}")
    print(f"{pad}Preserved commitments: {', '.join(evaluation.preserved_commitment_ids) or '(none)'}")
    level = DETAIL["level"]
    if level == "summary":
        counts = {}
        for c in evaluation.checks:
            counts[c.outcome] = counts.get(c.outcome, 0) + 1
        print(f"{pad}Checks: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
        unknown_codes = sorted({c.explanation.code for c in evaluation.checks if c.outcome == "unknown"})
        if unknown_codes:
            print(f"{pad}  unknown (NEEDS_REVIEW drivers, use --details): {', '.join(unknown_codes)}")
    shown = [c for c in evaluation.checks if all_checks or c.outcome == "fail" or
             (level == "details" and c.outcome != "pass")]
    hidden = len(evaluation.checks) - len(shown)
    print(f"{pad}Listed checks ({len(shown)} of {len(evaluation.checks)}; {hidden} hidden):")
    for c in shown:
        params = ", ".join(f"{k}={v}" for k, v in c.explanation.params.items())
        print(f"{pad}  - [{c.outcome.upper()}/{c.effect}/{c.required_for}] {c.explanation.code}"
              f"  seasons={','.join(c.season_ids) or '-'}  rule={c.rule_id}@{c.rule_version}")
        if params:
            print(f"{pad}      params: {params}")
        if c.missing_input_paths:
            print(f"{pad}      missing: {', '.join(c.missing_input_paths)}")
        print(f"{pad}      sources: {refs_text(c.explanation.source_refs)}")
    if level == "summary" and evaluation.assumptions:
        print(f"{pad}Declared-fact assumptions: {len(evaluation.assumptions)} (use --details)")
    for a in (evaluation.assumptions if level != "summary" else ()):
        print(f"{pad}  assumption: {a.code} {dict(a.params)}  sources: {refs_text(a.source_refs)}")


def print_plan(seasons, indent=2):
    pad = " " * indent
    for s in seasons:
        print(f"{pad}{s.season_id} {s.season_label}: crop={s.crop_id.value} purpose={s.purpose.value} profile={s.profile_id.value}")
        for name in ("sowing_date", "harvest_or_cut_date", "crop_end_exclusive", "release_date",
                     "preparation_days_after_release"):
            print(f"{pad}    {name}: {fact_text(getattr(s, name))}")


def print_preview(preview):
    print(f"Scope preview (data release {preview.data_release}; preview does NOT authorize search)")
    print(f"  scope_hash: {preview.scope_hash}")
    print(f"  catalogue crops: {', '.join(preview.available_crop_ids) or '(none)'}")
    print(f"  protected commitments: " + (", ".join(
        f"{c.commitment_id}({c.season_id}.{c.kind}={c.protected_value.value})" for c in preview.protected_commitments) or "(none)"))
    for c in preview.choices:
        if isinstance(c, _types.DateRangeChoice):
            print(f"  choice {c.choice_id}: {c.season_id}.sowing_date in [{c.start}..{c.end}] step {c.step_days}d")
        else:
            print(f"  choice {c.choice_id}: {c.season_id}.{c.field} in {list(c.allowed_values)}")
    for i in preview.issues:
        print(f"  issue [{i.kind.upper()}] {i.code}: choices={list(i.choice_ids)} seasons={list(i.season_ids)}"
              f" missing={list(i.missing_input_paths)}")
    if preview.missing_input_paths:
        print("  missing/unconfirmed inputs: " + ", ".join(preview.missing_input_paths))


def print_candidate(c, all_checks):
    print(f"  * {c.candidate_id}")
    print(f"    kind={c.kind}  directly edited seasons={','.join(c.direct_season_ids)}  choice_ids={','.join(c.choice_ids)}")
    print_evaluation(c.evaluation, 4, all_checks)
    print("    Changes vs current plan:")
    for ch in c.changes:
        print(f"      {ch.season_id}.{ch.field} [{'direct edit' if ch.direct else 'dependent'}]:")
        print(f"         before: {fact_text(ch.before)}")
        print(f"         after:  {fact_text(ch.after)}")
    if c.template_ids:
        print(f"    templates: {', '.join(c.template_ids)}")
    for t in c.tradeoffs:
        print(f"    note: {t.code} {dict(t.params)}")
    print(f"    sources: {refs_text(c.source_refs)}")


def print_result(result, all_checks):
    s = result.search
    print("Current plan (Promise Test):")
    print_evaluation(result.current, 2, all_checks)
    print()
    print(f"Search: {s.status.upper()}  limit_reason={s.limit_reason}")
    print(f"  raw={s.raw_count} evaluated={s.evaluated_count} duplicates={s.duplicate_count} "
          f"excluded={s.excluded_count} blocked={s.blocked_count}")
    print(f"  feasible={s.feasible_count} needs_review={s.needs_review_count} rejected={s.rejected_count}")
    print(f"  scope choices={list(s.scope_choice_ids)} uninstantiated={list(s.uninstantiated_choice_ids)}")
    print(f"  ordering policy={s.policy_version} approval={s.policy_approval}")
    if s.status == "complete" and not result.feasible_alternatives:
        print("  Zero feasible alternatives in the searched scope.")
    for title, group in (("Feasible alternatives (display max 2)", result.feasible_alternatives),
                         ("NEEDS_REVIEW investigations", result.review_investigations),
                         ("Rejected candidates", result.rejected_candidates)):
        print(f"\n{title}: {len(group)}")
        for c in group:
            print_candidate(c, all_checks)
    if result.exclusions:
        print(f"\nExclusions / blocked branches: {len(result.exclusions)}")
        for e in result.exclusions:
            print(f"  [{e.kind.upper()}] {e.code}: choices={list(e.choice_ids)} seasons={list(e.season_ids)}"
                  f" missing={list(e.missing_input_paths)}")


# ---------------------------------------------------------------- commands
def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=("check", "preview", "plan"))
    parser.add_argument("fixture")
    parser.add_argument("--json", action="store_true", help="print exact result fields as JSON")
    parser.add_argument("--details", action="store_true", help="list every non-passing check")
    parser.add_argument("--all-checks", action="store_true", help="list every check, including passes")
    parser.add_argument("--no-confirm", action="store_true", help="ignore confirm_exploration (expect refusal)")
    args = parser.parse_args(argv)

    raw, snapshot, kb, choices, catalogue, policy, confirm = load(args.fixture)
    confirm = confirm and not args.no_confirm
    DETAIL["level"] = "details" if (args.details or args.all_checks) else "summary"
    synthetic = is_synthetic(snapshot, kb)
    if not args.json:
        print("=== MISSION EL GHEET planner manual test: real meg_core planner ===")
        print(f"Fixture: {args.fixture}")
        if raw.get("_note"):
            print(f"Note: {raw['_note']}")
        if synthetic:
            print("*** SYNTHETIC: contains SYNTHETIC-ONLY evidence. Algorithm test only, NOT agronomy. ***")
        print(f"Data release: {snapshot.data_release}\n")

    try:
        if args.command == "check":
            evaluation = constraints.evaluate(snapshot.input.seasons, snapshot, kb)
            if args.json:
                print(json.dumps({"synthetic": synthetic, "evaluation": encode(evaluation)}, indent=2))
            else:
                print("Current plan:")
                print_plan(snapshot.input.seasons)
                print()
                print_evaluation(evaluation, 0, args.all_checks)
            return 0

        draft = replace(snapshot, input=replace(snapshot.input, journey="explore")) if (choices or catalogue) else snapshot
        preview = prepare_scope(ScopeRequest(snapshot=draft, choices=choices, catalogue_choices=catalogue), kb)
        if args.command == "preview":
            print(json.dumps({"synthetic": synthetic, "preview": encode(preview)}, indent=2)) if args.json \
                else print_preview(preview)
            return 0

        bound = draft
        if confirm and (preview.choices or preview.issues):
            bound = replace(draft, input=replace(draft.input, exploration=preview.choices,
                                                 pending_scope_issues=preview.issues,
                                                 scope_hash=preview.scope_hash, exploration_confirmed=True))
        elif preview.choices or preview.issues:
            bound = replace(draft, input=replace(draft.input, exploration=preview.choices,
                                                 pending_scope_issues=preview.issues))
        result = plan_service(bound, kb, policy)
        if args.json:
            print(json.dumps({"synthetic": synthetic, "exploration_confirmed": confirm, "result": encode(result)}, indent=2))
        else:
            print_preview(preview)
            print(f"\nExploration confirmed by tester: {'YES' if confirm else 'NO'}\n")
            print_result(result, args.all_checks)
        return 0
    except InputValidationError as error:
        message = {"error": "InputValidationError", "code": error.code, "field_paths": list(error.field_paths)}
        print(json.dumps(message, indent=2) if args.json else
              f"PLANNER REFUSED INPUT: {error.code} at {', '.join(error.field_paths)}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
