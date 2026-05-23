"""Internal helpers."""

import sys

ON_WINDOWS = sys.platform.startswith("win")
ON_DARWIN = sys.platform == "darwin"
ON_PY3 = sys.version_info[0] >= 3
