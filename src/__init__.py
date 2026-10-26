import os
import tomllib
from pathlib import Path

BASE_DIR = str(Path(__file__).parent.parent)
REPO_DIR = str(Path(__file__).parent.parent.parent)
DATA_DIR = os.path.join(BASE_DIR, "data")

with open(os.path.join(BASE_DIR, "pyproject.toml"), "rb") as _f:
    VERSION = tomllib.load(_f)["project"]["version"]

# Time a serviced unit spends driving to its facility, reversing and driving back to the gateway,
# on top of the service itself. Measured on Kleine Binckhorst, where one visit to the cleaning
# platform took about 1850 s of movement; a conservative stand-in for a per-location figure.
DEFAULT_SERVICING_TRAVEL_ALLOWANCE = 1800
