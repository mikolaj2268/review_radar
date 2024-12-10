# tests/conftest.py

import sys
from pathlib import Path

# Add the `src` directory to sys.path for module imports
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))