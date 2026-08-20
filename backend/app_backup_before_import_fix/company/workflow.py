from app.company.ai_company import AICompany
from app.company.project_state import ProjectState

from app.planner.planner import ProjectPlanner
from app.planner.task_queue import TaskQueue
from app.planner.dependency_graph import DependencyGraph


class WorkflowEngine:

    def __init__(self):

        self.company = AICompany()

        self.state = ProjectState()

        self.planner = ProjectPlanner()

        self.queue = TaskQueue()

        self.graph = DependencyGraph()

    async def run(self, project):

        print("🏢 AI Software Company Started")

        self.state.start()

        tasks = self.planner.create_tasks(project)

        for task in tasks:

            self.queue.add(task)

            self.graph.add(task.id, task.depends_on)

        while True:

            pending = self.queue.pending()

            if not pending:
                break

            progress = False

            for task in pending:

                if self.graph.ready(task.id, self.queue):

                    self.queue.update_status(task.id, "Running")

                    self.state.set_task(task.title)

                    print(f"▶ {task.title}")

                    try:

                        await self.company.build_project(task.task if hasattr(task, "task") else task)

                        self.queue.update_status(
                            task.id,
                            "Completed"
                        )

                        self.state.completed += 1

                        print(f"✅ {task.title}")

                    except Exception as e:

                        self.queue.update_status(
                            task.id,
                            "Failed"
                        )

                        self.state.failed += 1

                        print(e)

                    progress = True

            if not progress:
                break

        self.state.finish()

        print("🎉 Project Finished")

        return self.queue.all()