"""Regenerate the example scenario output checked into data/.

data/example_scenario.json and data/scenarios/scenario_trains_{given,random}.json
are generated output, committed so they're browsable without running anything.
Nothing enforces that they stay in sync with the generator, so CI regenerates
them here and diffs against what's checked in (see .github/workflows/python.yml).
Run this yourself after a change that affects generator output:

    python3 scripts/regenerate_examples.py

This only covers the self-contained examples (src/example.py's
self_contained_examples()) — the ones that read from the sibling
robust-rail-general repo are out of scope for CI since that repo isn't
checked out here.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from example import self_contained_examples

if __name__ == "__main__":
    self_contained_examples()
