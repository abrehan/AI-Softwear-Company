"""Workflow manager for coordinating AI Software Company managers."""

from __future__ import annotations

from typing import Any


class WorkflowManager:
    """Coordinate workflow execution across registered managers."""

    def __init__(self, manager: Any | None = None) -> None:
        self.manager = manager

    async def execute(
        self,
        task: Any,
        manager_name: str = "pm",
    ) -> dict[str, Any]:
        """Execute a task through the configured manager."""
        if self.manager is None:
            raise RuntimeError(
                "WorkflowManager has no manager configured."
            )

        execute_method = getattr(self.manager, "execute", None)

        if execute_method is None or not callable(execute_method):
            raise AttributeError(
                "Configured manager does not provide an execute() method."
            )

        result = await execute_method(manager_name, task)

        return {
            "manager": manager_name,
            "result": result,
        }

    async def execute_project_manager(
        self,
        task: Any,
    ) -> dict[str, Any]:
        """Execute a task through the Project Manager."""
        return await self.execute(task, manager_name="pm")
