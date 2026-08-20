from __future__ import annotations

import ast
import asyncio
import importlib.util
import os
import sys
from pathlib import Path
from typing import Any


class ProjectValidator:
    """
    Phase 4 â€” Step 2

    Validates a generated Python/FastAPI project without
    asking Ollama to analyze the entire project.

    Checks:
    1. Project discovery
    2. Python syntax
    3. Required files
    4. Python imports
    5. FastAPI application
    6. requirements.txt
    """

    def __init__(
        self,
        project_root: str = "generated_code",
    ):
        self.project_root = Path(project_root)

    # ---------------------------------------------------------
    # Locate generated backend
    # ---------------------------------------------------------

    def find_backend(self) -> Path | None:

        possible_paths = [
            self.project_root / "backend",
            self.project_root,
        ]

        for path in possible_paths:

            main_file = path / "app" / "main.py"

            if main_file.exists():
                return path.resolve()

        return None

    # ---------------------------------------------------------
    # Find Python executable
    # ---------------------------------------------------------

    def get_python(self) -> str:

        backend_root = Path(__file__).resolve().parents[3]

        if os.name == "nt":

            python = (
                backend_root
                / ".venv"
                / "Scripts"
                / "python.exe"
            )

        else:

            python = (
                backend_root
                / ".venv"
                / "bin"
                / "python"
            )

        if python.exists():
            return str(python)

        return sys.executable

    # ---------------------------------------------------------
    # Check required files
    # ---------------------------------------------------------

    def check_required_files(
        self,
        backend: Path,
    ) -> list[str]:

        required = [
            "app/main.py",
            "requirements.txt",
        ]

        missing = []

        for relative_path in required:

            file_path = backend / relative_path

            if not file_path.exists():
                missing.append(relative_path)

        return missing

    # ---------------------------------------------------------
    # Find Python files
    # ---------------------------------------------------------

    def get_python_files(
        self,
        backend: Path,
    ) -> list[Path]:

        return list(
            backend.glob("app/**/*.py")
        )

    # ---------------------------------------------------------
    # Python syntax validation
    # ---------------------------------------------------------

    def check_syntax(
        self,
        backend: Path,
    ) -> list[dict[str, Any]]:

        errors = []

        for file_path in self.get_python_files(backend):

            try:

                source = file_path.read_text(
                    encoding="utf-8",
                    errors="replace",
                )

                ast.parse(
                    source,
                    filename=str(file_path),
                )

            except SyntaxError as exc:

                errors.append(
                    {
                        "type": "syntax_error",
                        "file": str(file_path),
                        "line": exc.lineno,
                        "column": exc.offset,
                        "message": exc.msg,
                    }
                )

            except Exception as exc:

                errors.append(
                    {
                        "type": "read_error",
                        "file": str(file_path),
                        "message": str(exc),
                    }
                )

        return errors

    # ---------------------------------------------------------
    # Import extraction
    # ---------------------------------------------------------

    def extract_imports(
        self,
        file_path: Path,
    ) -> list[str]:

        imports = []

        try:

            source = file_path.read_text(
                encoding="utf-8",
                errors="replace",
            )

            tree = ast.parse(source)

            for node in ast.walk(tree):

                if isinstance(
                    node,
                    ast.Import,
                ):

                    for alias in node.names:
                        imports.append(
                            alias.name.split(".")[0]
                        )

                elif isinstance(
                    node,
                    ast.ImportFrom,
                ):

                    if node.module:

                        imports.append(
                            node.module.split(".")[0]
                        )

        except Exception:
            pass

        return imports

    # ---------------------------------------------------------
    # Check common external dependencies
    # ---------------------------------------------------------

    def check_external_imports(
        self,
        backend: Path,
    ) -> list[dict[str, Any]]:

        errors = []

        standard_library = {
            "os",
            "sys",
            "json",
            "re",
            "math",
            "time",
            "datetime",
            "asyncio",
            "typing",
            "pathlib",
            "logging",
            "uuid",
            "enum",
            "dataclasses",
            "collections",
            "itertools",
            "functools",
            "hashlib",
            "secrets",
            "subprocess",
            "shutil",
            "tempfile",
            "traceback",
        }

        seen = set()

        for file_path in self.get_python_files(
            backend
        ):

            imports = self.extract_imports(
                file_path
            )

            for module in imports:

                if module in standard_library:
                    continue

                if module in seen:
                    continue

                seen.add(module)

                try:

                    available = (
                        importlib.util.find_spec(
                            module
                        )
                    )

                except Exception:
                    available = None

                if available is None:

                    errors.append(
                        {
                            "type": "missing_import",
                            "file": str(file_path),
                            "module": module,
                            "message": (
                                f"Python module "
                                f"'{module}' "
                                f"could not be found."
                            ),
                        }
                    )

        return errors

    # ---------------------------------------------------------
    # Validate FastAPI main.py
    # ---------------------------------------------------------

    def check_fastapi_app(
        self,
        backend: Path,
    ) -> list[dict[str, Any]]:

        errors = []

        main_file = (
            backend
            / "app"
            / "main.py"
        )

        if not main_file.exists():

            errors.append(
                {
                    "type": "missing_main",
                    "message": (
                        "app/main.py does not exist."
                    ),
                }
            )

            return errors

        try:

            source = main_file.read_text(
                encoding="utf-8",
                errors="replace",
            )

            tree = ast.parse(source)

            found_app = False

            for node in tree.body:

                if isinstance(
                    node,
                    ast.Assign,
                ):

                    for target in node.targets:

                        if (
                            isinstance(
                                target,
                                ast.Name,
                            )
                            and target.id == "app"
                        ):

                            found_app = True

            if not found_app:

                errors.append(
                    {
                        "type": "missing_fastapi_app",
                        "file": str(main_file),
                        "message": (
                            "No variable named "
                            "'app' was found in "
                            "app/main.py."
                        ),
                    }
                )

        except Exception as exc:

            errors.append(
                {
                    "type": "fastapi_check_error",
                    "file": str(main_file),
                    "message": str(exc),
                }
            )

        return errors

    # ---------------------------------------------------------
    # Requirements validation
    # ---------------------------------------------------------

    def check_requirements(
        self,
        backend: Path,
    ) -> list[dict[str, Any]]:

        errors = []

        requirements = (
            backend
            / "requirements.txt"
        )

        if not requirements.exists():

            errors.append(
                {
                    "type": "missing_requirements",
                    "message": (
                        "requirements.txt "
                        "does not exist."
                    ),
                }
            )

            return errors

        try:

            content = requirements.read_text(
                encoding="utf-8",
                errors="replace",
            ).lower()

            python_files = self.get_python_files(
                backend
            )

            uses_fastapi = False

            for file_path in python_files:

                try:

                    source = file_path.read_text(
                        encoding="utf-8",
                        errors="replace",
                    ).lower()

                    if "from fastapi" in source:
                        uses_fastapi = True
                        break

                    if "import fastapi" in source:
                        uses_fastapi = True
                        break

                except Exception:
                    continue

            if (
                uses_fastapi
                and "fastapi" not in content
            ):

                errors.append(
                    {
                        "type": "missing_dependency",
                        "module": "fastapi",
                        "message": (
                            "FastAPI is imported "
                            "but not listed in "
                            "requirements.txt."
                        ),
                    }
                )

            if (
                uses_fastapi
                and "uvicorn" not in content
            ):

                errors.append(
                    {
                        "type": "missing_dependency",
                        "module": "uvicorn",
                        "message": (
                            "Uvicorn is required "
                            "to run FastAPI but "
                            "is not listed in "
                            "requirements.txt."
                        ),
                    }
                )

        except Exception as exc:

            errors.append(
                {
                    "type": "requirements_error",
                    "message": str(exc),
                }
            )

        return errors

    # ---------------------------------------------------------
    # Complete validation
    # ---------------------------------------------------------

    async def validate(self) -> dict[str, Any]:

        print("=" * 60)
        print("ðŸ” PHASE 4 â€” PROJECT VALIDATOR")
        print("=" * 60)

        backend = self.find_backend()

        if backend is None:

            print("âŒ Generated backend not found.")

            return {
                "success": False,
                "stage": "discovery",
                "errors": [
                    {
                        "type": "backend_not_found",
                        "message": (
                            "Could not find "
                            "generated_code/backend."
                        ),
                    }
                ],
            }

        print(f"ðŸ“ Backend: {backend}")

        all_errors: list[dict[str, Any]] = []

        # -----------------------------------------------------
        # Required files
        # -----------------------------------------------------

        print("ðŸ“‹ Checking required files...")

        missing_files = (
            self.check_required_files(
                backend
            )
        )

        for file_name in missing_files:

            all_errors.append(
                {
                    "type": "missing_file",
                    "file": file_name,
                    "message": (
                        f"Required file "
                        f"'{file_name}' "
                        f"is missing."
                    ),
                }
            )

        if missing_files:

            print(
                f"âŒ Missing files: "
                f"{len(missing_files)}"
            )

        else:

            print("âœ… Required files OK")

        # -----------------------------------------------------
        # Syntax
        # -----------------------------------------------------

        print("ðŸ Checking Python syntax...")

        syntax_errors = self.check_syntax(
            backend
        )

        all_errors.extend(
            syntax_errors
        )

        if syntax_errors:

            print(
                f"âŒ Syntax errors: "
                f"{len(syntax_errors)}"
            )

        else:

            print("âœ… Python syntax OK")

        # -----------------------------------------------------
        # Imports
        # -----------------------------------------------------

        print("ðŸ“¦ Checking imports...")

        import_errors = (
            self.check_external_imports(
                backend
            )
        )

        all_errors.extend(
            import_errors
        )

        if import_errors:

            print(
                f"âŒ Import errors: "
                f"{len(import_errors)}"
            )

        else:

            print("âœ… Imports OK")

        # -----------------------------------------------------
        # FastAPI
        # -----------------------------------------------------

        print("âš¡ Checking FastAPI application...")

        fastapi_errors = (
            self.check_fastapi_app(
                backend
            )
        )

        all_errors.extend(
            fastapi_errors
        )

        if fastapi_errors:

            print("âŒ FastAPI check failed")

        else:

            print("âœ… FastAPI application OK")

        # -----------------------------------------------------
        # Requirements
        # -----------------------------------------------------

        print("ðŸ“¦ Checking requirements...")

        requirement_errors = (
            self.check_requirements(
                backend
            )
        )

        all_errors.extend(
            requirement_errors
        )

        if requirement_errors:

            print(
                f"âŒ Requirement errors: "
                f"{len(requirement_errors)}"
            )

        else:

            print("âœ… Requirements OK")

        # -----------------------------------------------------
        # Result
        # -----------------------------------------------------

        success = len(all_errors) == 0

        print()

        if success:

            print("ðŸŽ‰ PROJECT VALIDATION PASSED")

        else:

            print(
                f"âŒ PROJECT VALIDATION FAILED "
                f"({len(all_errors)} errors)"
            )

        print("=" * 60)

        return {
            "success": success,
            "stage": "validation",
            "project": str(backend),
            "error_count": len(all_errors),
            "errors": all_errors,
        }


# -------------------------------------------------------------
# Manual execution
# -------------------------------------------------------------

async def main():

    validator = ProjectValidator()

    result = await validator.validate()

    print()
    print("RESULT:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
