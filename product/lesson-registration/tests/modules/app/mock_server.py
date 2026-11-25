"""Explicit synthetic-provider launcher for local UI/API integration preparation."""
import argparse
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

from contracts.interfaces import Providers
from lesson_registration.app.coordinator import Coordinator
from lesson_registration.app.gateway import StoreGateway
from lesson_registration.app.knowledge import Knowledge
from lesson_registration.app.result import ResultEvaluator
from lesson_registration.app.service import serve
from lesson_registration.app.store import Store
from support import GatewayRuntime, SchemaPrep


def compose(db_path, platform):
    runtime = GatewayRuntime(platform)
    runtime.gateway = StoreGateway(Store(db_path))
    providers = Providers(Knowledge(), SchemaPrep(platform), runtime, ResultEvaluator())
    return Coordinator(Store(db_path), providers=providers)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", choices=("kmong", "soomgo"), required=True)
    parser.add_argument("--origin", action="append", default=[], help="exact UI origin; repeatable")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="r03-mock-api-") as directory:
        serve(compose(pathlib.Path(directory) / "app.sqlite3", args.platform),
              dev_owner_header=True, allowed_origins=tuple(args.origin))


if __name__ == "__main__":
    main()
