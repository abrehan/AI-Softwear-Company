from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class AutonomousEngineeringOrchestrator:
    """
    PHASE 9

    Autonomous engineering control loop:
        inspect ➔ backup ➔ repair ➔ QA ➔ rollback if necessary ➔ report
    """

    def __init__(
        self,
        backend_root: str = ".",
        generated_root: str = "generated_code",
        max_attempts: int = 3,
    ):
        self.backend_root = Path(backend_root).resolve()
        self.generated_root = self.backend_root / generated_root
        self.max_attempts = max_attempts

        self.report_root = self.backend_root / ".qa_orchestrator"
        self.report_root.mkdir(parents=True, exist_ok=True)

        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report_file = self.report_root / f"phase9_{self.timestamp}.json"
        self.backup_root = self.report_root / f"backup_{self.timestamp}"

    def log(self, message: str) -> None:
        """Print safely on Windows consoles."""
        text = str(message)
        try:
            print(text)
        except UnicodeEncodeError:
            print(text.encode("ascii", errors="replace").decode("ascii"))

    def inspect_project(self) -> dict[str, Any]:
        backend = self.generated_root / "backend"
        main_file = backend / "app" / "main.py"
        return {
            "generated_root": str(self.generated_root),
            "backend": str(backend),
            "main_file": str(main_file),
            "main_exists": main_file.exists(),
            "python": sys.executable,
        }

    def create_backup(self) -> dict[str, Any]:
        if not self.generated_root.exists():
            return {"success": False, "error": "generated_code directory does not exist."}
        if self.backup_root.exists():
            shutil.rmtree(self.backup_root)
        shutil.copytree(
            self.generated_root,
            self.backup_root,
            ignore=shutil.ignore_patterns(".qa", ".qa_orchestrator")
        )
        return {"success": True, "backup": str(self.backup_root)}

    def restore_backup(self) -> dict[str, Any]:
        if not self.backup_root.exists():
            return {"success": False, "error": "Backup does not exist."}
        if self.generated_root.exists():
            shutil.rmtree(self.generated_root)
        shutil.copytree(self.backup_root, self.generated_root)
        return {"success": True, "restored": str(self.generated_root)}

    def run_qa(self) -> dict[str, Any]:
        self.log("🧪 Running integrated Phase 6 QA...")
        command = [sys.executable, "-m", "app.engineering.qa.qa_runner"]
        try:
            # FIX: Explicitly inject complete UTF-8 variables into child environment context
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            env["PYTHONUTF8"] = "1"

            result = subprocess.run(
                command,
                cwd=str(self.backend_root),
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,
            )
            output = result.stdout + "\n" + result.stderr
            passed = result.returncode == 0
            return {
                "success": passed,
                "return_code": result.returncode,
                "output": output,
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def detect_failure(self, qa_result: dict[str, Any]) -> dict[str, Any]:
        if qa_result.get("success"):
            return {"failure": False, "reason": None, "raw_output": ""}
        return {
            "failure": True,
            "reason": qa_result.get("error") or "Phase 6 QA failed.",
            "raw_output": qa_result.get("output", "")
        }

    def repair(self, failure: dict[str, Any]) -> dict[str, Any]:
        """
        Extracts execution failures and writes an actionable context payload 
        for an engineering repair operation.
        """
        reason = failure.get("reason", "Unknown failure")
        raw_output = failure.get("raw_output", "")
        
        self.log("🔎 Failure detected. Analyzing logs...")
        
        error_lines = [line for line in raw_output.splitlines() if "Error:" in line or "Exception" in line or "Traceback" in line]
        hint = error_lines[-1] if error_lines else "Asset evaluation breakdown verified."
        
        self.log(f"   💡 Error Hint Located: {hint}")

        payload = {
            "timestamp": self.timestamp,
            "target_directory": str(self.generated_root),
            "failure_reason": reason,
            "error_log_summary": hint,
            "raw_context": raw_output[-4000:]
        }
        
        payload_path = self.report_root / f"repair_prompt_{self.timestamp}.json"
        payload_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.log(f"📦 Diagnostics written to: {payload_path}")

        return {
            "success": True, 
            "repaired": True,
            "payload_created": str(payload_path),
            "strategy": "Diagnostic analysis payload prepared for AI softwear pipeline."
        }

    def save_report(self, report: dict[str, Any]) -> None:
        self.report_file.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")

    def run(self) -> dict[str, Any]:
        self.log("=" * 60)
        self.log("🤖 PHASE 9 — AUTONOMOUS ENGINEERING ORCHESTRATOR")
        self.log("=" * 60)

        report: dict[str, Any] = {
            "phase": 9,
            "timestamp": self.timestamp,
            "success": False,
            "attempts": [],
        }

        inspection = self.inspect_project()
        report["inspection"] = inspection

        if not inspection["main_exists"]:
            report["error"] = "Generated FastAPI main.py was not found."
            self.save_report(report)
            return report

        self.log(f"📁 Generated backend: {inspection['backend']}")

        qa_result = self.run_qa()
        failure = self.detect_failure(qa_result)

        if not failure["failure"]:
            self.log("✅ Project is working correctly. No modifications needed.")
            report["success"] = True
            report["status"] = "stable"
            self.save_report(report)
            return report

        self.log("📦 Creating environment backup prior to optimization cycle...")
        backup_res = self.create_backup()
        if not backup_res["success"]:
            self.log(f"❌ Backup failed: {backup_res.get('error')}")
            report["error"] = "Backup step failed, halting loop."
            self.save_report(report)
            return report

        for attempt in range(1, self.max_attempts + 1):
            self.log(f"\n⚙️ Attempt {attempt}/{self.max_attempts} to repair...")
            
            repair_res = self.repair(failure)
            attempt_log = {"attempt": attempt, "repair": repair_res}

            post_qa_res = self.run_qa()
            attempt_log["post_qa"] = post_qa_res
            
            if post_qa_res["success"]:
                self.log("🎉 Repair successful! QA tests passed.")
                report["success"] = True
                report["status"] = "repaired"
                report["attempts"].append(attempt_log)
                break
            else:
                self.log("❌ QA metrics failed. Reverting to structural checkpoint...")
                self.restore_backup()
                attempt_log["status"] = "rolled_back"
                report["attempts"].append(attempt_log)

        if not report["success"]:
            self.log("🛑 Loop finished: Manual code optimization required for diagnostic payload.")
            report["status"] = "failed_retained"

        self.save_report(report)
        return report


if __name__ == "__main__":
    orchestrator = AutonomousEngineeringOrchestrator()
    orchestrator.run()
