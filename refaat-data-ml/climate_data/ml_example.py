"""Read the training targets, inspect one eligible window, then score calendar-only predictions."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .climatology import SeasonalClimatology
from .evaluation import load_diagnostic_data, score_predictions, seasonal_predictions


def example(data_dir: Path) -> dict:
    data = load_diagnostic_data(data_dir)
    window, history = next(data.contexts())
    baseline = SeasonalClimatology.from_csv(data_dir / "fit_targets.csv")
    predictions = seasonal_predictions(baseline, data.windows)
    scored, scores = score_predictions(data, predictions)
    return {
        "training_rows":len(data.training), "validation_rows":len(data.validation),
        "origins":len(data.windows), "first_issue":str(window.issue),
        "first_context_start":str(history[0].day), "first_context_cutoff":str(history[-1].day),
        "context_days":len(history), "first_scored_dates":[str(d) for d in window.targets()],
        "prediction_rows":len(scored),
        "mae":{target:score["mae"] for target,score in scores.items()},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data",type=Path,default=Path("data"))
    print(json.dumps(example(parser.parse_args().data),indent=2,allow_nan=False))

