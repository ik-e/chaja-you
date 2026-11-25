"""Single-app-process dispatch/fence ordering, shared across Store instances.

Lock order: execution gate -> SQLite transaction. Never acquire this gate while
holding a DB transaction. Callback must synchronously finish browser I/O; merely
queuing work does not establish this boundary. Not a cross-process lock.
"""
from contextlib import contextmanager
from pathlib import Path
from threading import Lock, RLock
import os

_guard = Lock()
_entries = {}


@contextmanager
def execution_gate(db_path, registration_id):
    key = (os.path.normcase(str(Path(db_path).resolve())), registration_id)
    with _guard:
        entry = _entries.setdefault(key, [RLock(), 0])
        entry[1] += 1
    try:
        with entry[0]:
            yield
    finally:
        with _guard:
            entry[1] -= 1
            if entry[1] == 0:
                del _entries[key]
