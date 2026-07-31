import os
import tomllib
from pathlib import Path

BASE_DIR = str(Path(__file__).parent.parent)
REPO_DIR = str(Path(__file__).parent.parent.parent)
DATA_DIR = os.path.join(BASE_DIR, "data")

with open(os.path.join(BASE_DIR, "pyproject.toml"), "rb") as _f:
    VERSION = tomllib.load(_f)["project"]["version"]
