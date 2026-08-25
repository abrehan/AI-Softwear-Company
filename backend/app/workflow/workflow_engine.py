import asyncio
import json
from datetime import datetime, timezone
from typing import Any

from app.managers.agent_manager import AgentManager
from app.workflow.dependency_graph import DEPENDENCIES
from app.workspace.workspace import workspace
CORE_RELEASE_PIPELINE = {
    "ceo",
    "pm",
    "cto",
    "file_planner",
    "uiux",
    "backend",
    "frontend",
    "database",
    "qa",
    "security",
    "devops",
}


class WorkflowEngine:
    """
    Canonical dependency-aware workflow engine for the Virtual AI Office.
    """

    def __init__(self):
        self.manager = AgentManager()

        self.completed: set[str] = set()
        self.failed: set[str] = set()
        self.blocked: set[str] = set()

        self.results: dict[str, Any] = {}
        self.errors: dict[str, str] = {}

        self.status: dict[str, str] = {
            agent: "PENDING"
            for agent in DEPENDENCIES
        }

        self.started_at: dict[str, str] = {}
        self.completed_at: dict[str, str] = {}

        self.workflow_started_at = ""
        self.workflow_completed_at = ""

    async def execute(self, project: str):

        self._reset()

        self.workflow_started_at = self._now()

        print("=" * 70)
        print("AI SOFTWARE COMPANY WORKFLOW STARTED")
        print("=" * 70)
        print()

        while (
            len(self.completed)
            + len(self.failed)
            + len(self.blocked)
            < len(DEPENDENCIES)
        ):

            self._mark_blocked_agents()

            runnable = []

            for agent_name, deps in DEPENDENCIES.items():

                if agent_name in self.completed:
                    continue

                if agent_name in self.failed:
                    continue

                if agent_name in self.blocked:
                    continue

                if all(
                    dep in self.completed
                    for dep in deps
                ):
                    runnable.append(agent_name)

            if not runnable:
                remaining = [
                    name
                    for name in DEPENDENCIES
                    if name not in self.completed
                    and name not in self.failed
                    and name not in self.blocked
                ]

                if remaining:
                    print(
                        "No runnable agents remaining:",
                        remaining,
                    )

                break

            print()
            print("=" * 70)
            print(
                "RUNNING:",
                ", ".join(runnable),
            )
            print("=" * 70)

            # Run one Ollama-backed agent at a time.
            # Local Ollama generation is resource constrained, and
            # parallel requests can cause long generation timeouts.
            for agent_name in runnable:
                await self.run_agent(
                    agent_name,
                    project,
                )

        self._mark_blocked_agents(force=True)

        self.workflow_completed_at = self._now()

        report = self._build_report(project)

        self._persist_report(report)

        print()
        print("=" * 70)
        print("WORKFLOW FINISHED")
        print("=" * 70)
        print(
            f"Completed: {len(self.completed)}"
        )
        print(
            f"Failed: {len(self.failed)}"
        )
        print(
            f"Blocked: {len(self.blocked)}"
        )

        if self.failed:
            print()
            print("FAILED AGENTS:")
            for name in sorted(self.failed):
                print(
                    f"  - {name}: {self.errors.get(name, '')}"
                )

        if self.blocked:
            print()
            print("BLOCKED AGENTS:")
            for name in sorted(self.blocked):
                print(
                    f"  - {name}: {self.errors.get(name, '')}"
                )

        overall_status = self._overall_status()

        print()
        print(
            f"OVERALL STATUS: {overall_status}"
        )

        return report

    async def run_agent(
        self,
        agent_name: str,
        project: str,
    ):

        self.status[agent_name] = "RUNNING"
        self.started_at[agent_name] = self._now()

        print(
            f"Starting {agent_name.upper()} Agent..."
        )

        try:

            dependency_outputs = []

            for dependency in DEPENDENCIES.get(
                agent_name,
                [],
            ):

                output = self.results.get(
                    dependency
                )

                if output:
                    dependency_outputs.append(
                        (
                            f"\n--- {dependency.upper()} OUTPUT ---\n"
                            f"{output}\n"
                            f"--- END {dependency.upper()} OUTPUT ---\n"
                        )
                    )

            context = "\n".join(
                dependency_outputs
            )

            task = f"""
ORIGINAL PROJECT REQUEST:
{project}

UPSTREAM AGENT RESULTS:
{context if context else "No upstream agent results yet."}

YOUR ROLE:
You are the {agent_name} agent.

Complete your responsibility for this project.

Use upstream results as planning input.

Do not invent completed work.

Clearly distinguish:
- confirmed facts
- decisions
- recommendations
- unknowns

Return the result appropriate for your role.
"""

            result = await self.manager.execute(
                agent_name,
                task,
            )

            self.results[agent_name] = result

            self.completed.add(
                agent_name
            )

            self.status[agent_name] = "SUCCESS"
            self.completed_at[agent_name] = self._now()

            print(
                f"{agent_name.upper()} completed."
            )

        except Exception as exc:

            self.failed.add(
                agent_name
            )

            self.status[agent_name] = "FAILED"

            self.errors[agent_name] = (
                f"{type(exc).__name__}: {exc}"
            )

            self.completed_at[agent_name] = self._now()

            print(
                f"{agent_name.upper()} FAILED: "
                f"{type(exc).__name__}: {exc}"
            )

    def _mark_blocked_agents(
        self,
        force: bool = False,
    ):

        changed = True

        while changed:

            changed = False

            for agent_name, deps in DEPENDENCIES.items():

                if agent_name in self.completed:
                    continue

                if agent_name in self.failed:
                    continue

                if agent_name in self.blocked:
                    continue

                failed_dependencies = [
                    dep
                    for dep in deps
                    if dep in self.failed
                    or dep in self.blocked
                ]

                if failed_dependencies:

                    self.blocked.add(
                        agent_name
                    )

                    self.status[agent_name] = (
                        "SKIPPED"
                    )

                    self.errors[agent_name] = (
                        "Blocked by failed dependency: "
                        + ", ".join(
                            failed_dependencies
                        )
                    )

                    self.completed_at[agent_name] = (
                        self._now()
                    )

                    print(
                        f"{agent_name.upper()} SKIPPED: "
                        f"{self.errors[agent_name]}"
                    )

                    changed = True

        if force:
            for agent_name, deps in DEPENDENCIES.items():

                if agent_name in self.completed:
                    continue

                if agent_name in self.failed:
                    continue

                if agent_name in self.blocked:
                    continue

                self.blocked.add(
                    agent_name
                )

                self.status[agent_name] = (
                    "SKIPPED"
                )

                self.errors[agent_name] = (
                    "No runnable path remained."
                )

                self.completed_at[agent_name] = (
                    self._now()
                )

    def _reset(self):

        self.manager.reset()

        self.completed.clear()
        self.failed.clear()
        self.blocked.clear()

        self.results.clear()
        self.errors.clear()

        self.status = {
            agent: "PENDING"
            for agent in DEPENDENCIES
        }

        self.started_at.clear()
        self.completed_at.clear()

        self.workflow_started_at = ""
        self.workflow_completed_at = ""

    def _overall_status(self) -> str:

        core_failed = [
            agent
            for agent in CORE_RELEASE_PIPELINE
            if agent in self.failed
        ]

        core_blocked = [
            agent
            for agent in CORE_RELEASE_PIPELINE
            if agent in self.blocked
        ]

        core_pending = [
            agent
            for agent in CORE_RELEASE_PIPELINE
            if self.status.get(agent) not in {
                "SUCCESS",
                "FAILED",
                "SKIPPED",
            }
        ]

        if core_failed:
            return "RELEASE_BLOCKED"

        if core_blocked:
            return "RELEASE_BLOCKED"

        if core_pending:
            return "RUNNING"

        optional_failed = [
            agent
            for agent in DEPENDENCIES
            if agent not in CORE_RELEASE_PIPELINE
            and agent in self.failed
        ]

        optional_blocked = [
            agent
            for agent in DEPENDENCIES
            if agent not in CORE_RELEASE_PIPELINE
            and agent in self.blocked
        ]

        if optional_failed or optional_blocked:
            return "RELEASE_READY_WITH_OPTIONAL_FAILURES"

        if CORE_RELEASE_PIPELINE.issubset(
            self.completed
        ):
            return "RELEASE_READY"

        return "PARTIAL"
    def _build_report(
        self,
        project: str,
    ) -> dict[str, Any]:

        return {
            "status": self._overall_status(),

            "release_gate": {
                "ready": (
                    self._overall_status()
                    in {
                        "RELEASE_READY",
                        "RELEASE_READY_WITH_OPTIONAL_FAILURES",
                    }
                ),
                "core_pipeline": sorted(
                    CORE_RELEASE_PIPELINE
                ),
                "core_completed": sorted(
                    agent
                    for agent in CORE_RELEASE_PIPELINE
                    if agent in self.completed
                ),
                "core_failed": sorted(
                    agent
                    for agent in CORE_RELEASE_PIPELINE
                    if agent in self.failed
                ),
                "core_blocked": sorted(
                    agent
                    for agent in CORE_RELEASE_PIPELINE
                    if agent in self.blocked
                ),
            },

            "workflow": {
                "started_at": self.workflow_started_at,
                "completed_at": self.workflow_completed_at,
                "agent_count": len(
                    DEPENDENCIES
                ),
            },

            "project": project,

            "agents": {
                name: {
                    "status": self.status.get(
                        name,
                        "PENDING",
                    ),
                    "required_for_release": (
                        name
                        in CORE_RELEASE_PIPELINE
                    ),
                    "dependencies": DEPENDENCIES.get(
                        name,
                        [],
                    ),
                    "started_at": self.started_at.get(
                        name
                    ),
                    "completed_at": self.completed_at.get(
                        name
                    ),
                    "result": self.results.get(
                        name
                    ),
                    "error": self.errors.get(
                        name
                    ),
                }
                for name in DEPENDENCIES
            },

            "completed": sorted(
                self.completed
            ),

            "failed": {
                name: self.errors.get(
                    name,
                    "",
                )
                for name in sorted(
                    self.failed
                )
            },

            "blocked": {
                name: self.errors.get(
                    name,
                    "",
                )
                for name in sorted(
                    self.blocked
                )
            },

            "results": self.results,
        }
    def _persist_report(
        self,
        report: dict[str, Any],
    ):

        status_json = json.dumps(
            report,
            indent=2,
            default=str,
        )

        workspace.save(
            "workflow/latest_workflow_status.json",
            status_json,
        )

        markdown = self._markdown_report(
            report
        )

        workspace.save(
            "workflow/latest_workflow_report.md",
            markdown,
        )

    @staticmethod
    def _markdown_report(
        report: dict[str, Any],
    ) -> str:

        lines = [
            "# Virtual AI Office Workflow Report",
            "",
            f"## Overall Status",
            report["status"],
            "",
            "## Agent Status",
            "",
            "| Agent | Status | Dependencies | Error |",
            "|---|---|---|---|",
        ]

        for agent, data in report[
            "agents"
        ].items():

            dependencies = ", ".join(
                data["dependencies"]
            )

            error = (
                data["error"]
                or ""
            ).replace("|", "/")

            lines.append(
                f"| {agent} | "
                f"{data['status']} | "
                f"{dependencies} | "
                f"{error} |"
            )

        lines.extend(
            [
                "",
                "## Completed Agents",
                "",
            ]
        )

        for agent in report["completed"]:
            lines.append(
                f"- {agent}"
            )

        if report["failed"]:

            lines.extend(
                [
                    "",
                    "## Failed Agents",
                    "",
                ]
            )

            for agent, error in report[
                "failed"
            ].items():

                lines.append(
                    f"- {agent}: {error}"
                )

        if report["blocked"]:

            lines.extend(
                [
                    "",
                    "## Blocked Agents",
                    "",
                ]
            )

            for agent, error in report[
                "blocked"
            ].items():

                lines.append(
                    f"- {agent}: {error}"
                )

        return "\n".join(
            lines
        )

    @staticmethod
    def _now() -> str:
        return datetime.now(
            timezone.utc
        ).isoformat()




