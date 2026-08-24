"""Keep this skill's local ``scripts`` package ahead of other skill paths."""

from __future__ import annotations

import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
if str(SKILL_ROOT) in sys.path:
    sys.path.remove(str(SKILL_ROOT))
sys.path.insert(0, str(SKILL_ROOT))
