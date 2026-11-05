"""Report scenarios that provably cannot be solved, using the necessary bounds of src/feasibility.py.

Usage: python scripts/check_feasibility.py LOCATION.json SCENARIO.json [SCENARIO.json ...]
       python scripts/check_feasibility.py LOCATION.json DIRECTORY
Exit status 1 when any scenario violates a bound.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from feasibility import check_servicing_bounds  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("location", type=Path)
    parser.add_argument("scenarios", type=Path, nargs="+", help="scenario files and/or directories of them")
    parser.add_argument(
        "--travel-allowance", type=int, default=0, help="seconds added to the single-train bound (default 0)"
    )
    args = parser.parse_args()

    location = json.loads(args.location.read_text())
    files = sorted(f for p in args.scenarios for f in (p.glob("*.json") if p.is_dir() else [p]))
    checked: Counter = Counter()
    failed: Counter = Counter()
    for file in files:
        scenario = json.loads(file.read_text())
        trains = len(scenario.get("in", []))
        checked[trains] += 1
        violations = check_servicing_bounds(scenario, location, args.travel_allowance)
        if violations:
            failed[trains] += 1
            print(f"{file.name}: INFEASIBLE")
            for v in violations:
                print(f"  {v.description}")
    print()
    for trains in sorted(checked):
        print(f"{trains} incoming trains: {failed[trains]} of {checked[trains]} violate a bound")
    print(f"total: {sum(failed.values())} of {sum(checked.values())}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
