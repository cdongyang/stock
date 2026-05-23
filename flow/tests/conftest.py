import sys
from unittest.mock import MagicMock

# Mock futu SDK before any test imports it (futu tries to write log files at import time)
if 'futu' not in sys.modules:
    _futu = MagicMock()
    _futu.RET_OK = 0
    sys.modules['futu'] = _futu
