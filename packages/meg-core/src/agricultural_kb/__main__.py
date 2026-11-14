"""Print a serializable KB status. Invalid input exits nonzero with a structured error."""
import argparse
import json
from .loader import KBError, load_kb

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--kb", default=None)
parser.add_argument("--locality", default="sakha")
args = parser.parse_args()
try:
    print(json.dumps(load_kb(args.kb).get_status(locality=args.locality), indent=2, allow_nan=False))
except KBError as exc:
    print(json.dumps(exc.to_dict(), allow_nan=False))
    raise SystemExit(2)
