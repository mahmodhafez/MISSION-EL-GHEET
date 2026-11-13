# MISSION EL GHEET

A crop-rotation planner for farmers near Sakha, Egypt, built for NASA Space Apps 2026. Farmers use it by
voice and pictures, in Egyptian Arabic or English.

The farmer says what must stay ("the berseem cut on 20 May"). A deterministic **Promise Test**
checks four seasons ahead, explains any conflict, offers at most two evidence-supported
alternatives, and compares them on historical NASA POWER weather. Forecasting is experimental and
kept separate: a fine-tuned Chronos-2 model was trained, and it **did not** beat seasonal
climatology.

## Status

Specs and design are done; application code has not started. Details are in
[docs/status/](docs/status/README.md).

## Where to start

- **People:** [docs/README.md](docs/README.md) indexes every doc. Then read [docs/team.md](docs/team.md)
  and [docs/rules/git.md](docs/rules/git.md).
- **AI agents (Claude, Codex, Antigravity):** [AGENTS.md](AGENTS.md).

## Repository layout

| Path | Purpose |
|---|---|
| `backend/` | FastAPI + Pydantic + SQLite (placeholder) |
| `frontend/` | React + TypeScript + Vite + Tailwind (placeholder) |
| `ml/` | Shared-release builder, ML experiments |
| `data/validation/` | NASA POWER / ET0 audit and regeneration scripts |
| `work/ux-phase-2/`, `work/ux-phase-3/` | Standalone HTML wireframes and the Fieldlight prototype; open them in a browser |
| `docs/` | Specs, status, decisions, rules, reports |
| `archive-snapshot/` | Frozen copies from the original validation archive |

## Running what exists

```sh
python -I -S -m unittest discover -s data/validation -p "test_*.py" -v
python -I -S -m unittest discover -s ml/tests -v
node work/ux-phase-2/check-wireframes-v3.cjs
node work/ux-phase-3/check-hybrid.cjs
```

The large evidence ZIP and model weights are not in git, so most evidence tests skip on a fresh
clone. See [docs/science/reproducing.md](docs/science/reproducing.md).
