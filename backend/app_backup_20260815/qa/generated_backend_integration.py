import sys
import importlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
GENERATED_ROOT = PROJECT_ROOT / "generated_code"

sys.path.insert(0, str(GENERATED_ROOT))

MODULES = [
    "backend.app.database",
    "backend.app.main",
    "backend.app.api.routes.auth",
    "backend.app.api.routes.projects",
    "backend.app.api.routes.users",
    "backend.app.core.config",
    "backend.app.core.security",
    "backend.app.models.project",
    "backend.app.models.user",
    "backend.app.schemas.project",
    "backend.app.schemas.user",
    "backend.app.services.auth_service",
    "backend.app.services.project_service",
    "backend.app.services.user_service",
    "backend.app.utils.helpers",
]


def check_module(module_name: str) -> bool:
    print()
    print("=" * 70)
    print(f"IMPORTING: {module_name}")
    print("=" * 70)

    try:
        importlib.import_module(module_name)
        print(f"IMPORT_OK: {module_name}")
        return True
    except Exception as exc:
        print(f"IMPORT_FAILED: {module_name}")
        print(f"{type(exc).__name__}: {exc}")
        return False


def main():
    print("=" * 70)
    print("GENERATED BACKEND INTEGRATION TEST")
    print("=" * 70)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Generated root: {GENERATED_ROOT}")

    if not GENERATED_ROOT.exists():
        print("ERROR: generated_code directory does not exist.")
        sys.exit(1)

    failures = []

    for module in MODULES:
        if not check_module(module):
            failures.append(module)

    print()
    print("=" * 70)

    if failures:
        print("BACKEND INTEGRATION FAILED")
        print("=" * 70)

        for module in failures:
            print(f"FAIL: {module}")

        sys.exit(1)

    print("ALL GENERATED BACKEND MODULES IMPORT SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()