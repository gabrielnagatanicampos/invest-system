import importlib
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))


@pytest.fixture
def banco(tmp_path, monkeypatch):
    """Recarrega o módulo database apontando para um banco.db temporário."""
    monkeypatch.chdir(tmp_path)
    import database
    importlib.reload(database)
    yield database
    database.conexao.close()
