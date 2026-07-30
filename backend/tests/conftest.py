from __future__ import annotations

import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture(autouse=True)
def authoritative_xrpl_stub():
    from app.api.dependencies import get_xrpl_client
    from app.main import app
    from tests.xrpl_stub import ledger_stub

    ledger_stub.clear()
    app.dependency_overrides[get_xrpl_client] = lambda: ledger_stub
    yield ledger_stub
    app.dependency_overrides.pop(get_xrpl_client, None)
    ledger_stub.clear()
