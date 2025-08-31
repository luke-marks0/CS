from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List


class TaskStatus(Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class TaskPriority(Enum):
    LOW = "LOW"
    # default
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


@dataclass
class Task:
    title: str
    description: str
    status: TaskStatus
    id: int
    dependencies: List[int] | None = None
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskManager:
    """Minimal stub for the practice assessment.

    Implement all required methods in this class to pass the tests.
    """

    def __init__(self) -> None:
        # id -> Task
        self.tasks = {}

    def create_task(self, title: str, description: str) -> int:
        if not title:
            raise ValueError("Title cannot be empty.")
        id = len(self.tasks) + 1
        self.tasks[id] = Task(title=title, description=description, id=id, status=TaskStatus.TODO)
        return id

    def get_task(self, task_id: int) -> Task | None:
        if not task_id in self.tasks:
            return None
        return self.tasks[task_id]

    def get_all_tasks(self):
        task_list = []
        for task in self.tasks.items():
            task_list.append(task[1])
        return task_list

    def update_task_status(self, task_id: int, status: str) -> bool:
        if not task_id in self.tasks:
            return False
        self.tasks[task_id].status = status
        return True

    def delete_task(self, task_id: int):
        if not task_id in self.tasks:
            return False
        del self.tasks[task_id]
        return True

    def get_tasks_by_status(self, status: str):
        tasks_with_status = []
        for task in self.tasks.items():
            if task[1].status == status:
                tasks_with_status.append(task[1])
        return tasks_with_status