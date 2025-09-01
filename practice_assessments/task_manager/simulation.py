from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from copy import deepcopy
from graphlib import TopologicalSorter, CycleError
from datetime import date


class TaskStatus(Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    BLOCKED = "BLOCKED"
    OVERDUE = "OVERDUE"


class TaskPriority(IntEnum):
    LOW = 3
    # default
    MEDIUM = 2
    HIGH = 1
    URGENT = 0


@dataclass
class Task:
    title: str
    description: str
    status: TaskStatus
    id: int
    created_date: date | None = None
    dependencies: list[int] = field(default_factory=list)
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: int | None = None
    due_date: date | None = None


@dataclass
class User:
    name: str
    email: str
    id: int


class TaskManager:
    def __init__(self) -> None:
        # id -> Task
        self.tasks = {}
        # id -> User
        self.users = {}

    ###
    # BASIC TASK MANAGEMENT
    ###

    def create_task(self, title: str, description: str) -> int:
        if not title:
            raise ValueError("Title cannot be empty.")
        id = len(self.tasks) + 1
        self.tasks[id] = Task(title=title, description=description, id=id, status=TaskStatus.TODO)
        return id

    def get_task(self, task_id: str) -> int:
        if not task_id in self.tasks:
            return None
        return self.tasks[task_id]

    def get_all_tasks(self):
        task_list = []
        for task in self.tasks.items():
            task_list.append(deepcopy(task[1]))
        return task_list

    def delete_task(self, task_id: int):
        if not task_id in self.tasks:
            return False
        del self.tasks[task_id]
        for task in self.tasks.items():
            if task[1].dependencies:
                task[1].dependencies.remove(task_id)
        return True

    def assign_task(self, task_id: int, user_id: int) -> bool:
        if not task_id in self.tasks or not user_id in self.users:
            return False
        if self.tasks[task_id].status == TaskStatus.DONE:
            return False
        self.tasks[task_id].assignee_id = user_id
        return True

    def unassign_task(self, task_id: int) -> bool:
        if not task_id in self.tasks:
            return False
        self.tasks[task_id].assignee_id = None
        return True

    ###
    # TASK STATUS MANAGEMENT
    ###

    def update_task_status(self, task_id: int, status: str) -> bool:
        if not task_id in self.tasks:
            return False
        self.tasks[task_id].status = status
        return True

    def get_tasks_by_status(self, status: str):
        tasks_with_status = []
        for task in self.tasks.items():
            if task[1].status == status:
                tasks_with_status.append(deepcopy(task[1]))
        return tasks_with_status

    def get_available_tasks(self) -> list[Task]:
        available_tasks = []
        for task in self.tasks.items():
            if task[1].status == TaskStatus.TODO:
                if task[1].dependencies:
                    dependencies_done = True
                    for dependency in task[1].dependencies:
                        if self.tasks[dependency].status != TaskStatus.DONE: 
                            dependencies_done = False
                            break
                    if dependencies_done:
                        available_tasks.append(deepcopy(task[1]))
                else:
                    available_tasks.append(deepcopy(task[1]))
        available_tasks = sorted(available_tasks, key= lambda task: (task.priority, task.id))
        return available_tasks

    def get_blocked_tasks(self) -> list[Task]:
        blocked_tasks = []
        for task in self.tasks.items():
            if task[1].status in (TaskStatus.TODO, TaskStatus.BLOCKED) and task[1].dependencies:
                for dependency in task[1].dependencies:
                    if self.tasks[dependency].status != TaskStatus.DONE: 
                        dependencies_done = False
                        blocked_tasks.append(deepcopy(task[1]))
        blocked_tasks = sorted(blocked_tasks, key= lambda task: task.id)
        return blocked_tasks

    def auto_update_blocked_status(self) -> int:
        status_changed = 0
        for task in self.tasks.items():
            if not task[1].dependencies:
                continue
            if task[1].status == TaskStatus.TODO:
                for dependency in task[1].dependencies:
                    if self.tasks[dependency].status != TaskStatus.DONE:
                        self.tasks[task[0]].status = TaskStatus.BLOCKED
                        status_changed += 1
            if task[1].status == TaskStatus.BLOCKED:
                dependencies_done = True
                for dependency in task[1].dependencies:
                    if self.tasks[dependency].status != TaskStatus.DONE:
                        dependencies_done = False
                        break
                if dependencies_done:
                    self.tasks[task[0]].status = TaskStatus.TODO
                    status_changed += 1
        return status_changed

    def get_overdue_tasks(self) -> list[Task]:
        task_and_amount_overdue = []
        for task in self.tasks.values():
            if task.due_date < date.today() and task.status != TaskStatus.DONE:
                amount_overdue = date.today() - task.due_date
                task_and_amount_overdue.append((task, amount_overdue))
        task_and_amount_overdue = sorted(task_and_amount_overdue, key= lambda task: (task[1], task[0].id))
        sorted_overdue_tasks = []
        for task in task_and_amount_overdue:
            sorted_overdue_tasks.append(task[0])
        return sorted_overdue_tasks

    def update_overdue_status(self) -> int:
        overdue_tasks = self.get_overdue_tasks()
        status_changed = 0
        for task in overdue_tasks:
            self.tasks[task.id].status = TaskStatus.OVERDUE
            status_changed += 1
        return status_changed

    ###
    # TASK PRIORITY MANAGEMENT
    ###

    def create_task_with_priority(self, title: str, description: str, priority: str) -> int:
        if not title:
            raise ValueError("Title cannot be empty.")
        id = len(self.tasks) + 1
        self.tasks[id] = Task(title=title, description=description, id=id, status=TaskStatus.TODO, priority=priority)
        return id

    def update_task_priority(self, task_id: int, priority: str) -> bool:
        if not task_id in self.tasks:
            return False
        self.tasks[task_id].priority = priority
        return True
        
    ###
    # TASK DEPENDENCY MANAGEMENT
    ###

    def _circular(self):
        topological_sorter = TopologicalSorter()
        for idx, task in self.tasks.items():
            topological_sorter.add(idx, *(dep for dep in task.dependencies if dep in self.tasks))
        try:
            _ = list(topological_sorter.static_order())
            return False
        except CycleError as e:
            return True

    def add_dependency(self, task_id: int, depends_on_task_id: int) -> bool:
        if not task_id in self.tasks or not depends_on_task_id in self.tasks:
            return False
        if task_id == depends_on_task_id:
            return False
        if self.tasks[task_id].status == TaskStatus.DONE:
            return False
        old_tasks = deepcopy(self.tasks)
        self.tasks[task_id].dependencies.append(depends_on_task_id)
        if self._circular():
            self.tasks = deepcopy(old_tasks)
            return False
        return True

    def remove_dependency(self, task_id: str, depends_on_task_id: str) -> bool:
        if not task_id in self.tasks:
            return False
        if not self.tasks[task_id].dependencies:
            return False
        if not depends_on_task_id in self.tasks[task_id].dependencies:
            return False
        self.tasks[task_id].dependencies.remove(depends_on_task_id)
        return True

    ###
    # DUE DATE MANAGEMENT
    ###

    def set_due_date(self, task_id: int, due_date: date) -> bool:
        if not task_id in self.tasks:
            return False
        self.tasks[task_id].due_date = due_date
        return True
    
    def get_tasks_due_soon(self, days: int) -> list[Task]:
        due_soon = []
        for task in self.tasks.values():
            time_diff = date.today() - task.due_date
            if time_diff <= 

    ###
    # USER MANAGEMENT
    ###

    def create_user(self, name: str, email: str) -> int:
        if not name or not email:
            raise ValueError("Name and email must be populated.")
        id = len(self.users) + 1
        self.users[id] = User(name=name, email=name, id=id)
        return id

    def get_user(self, user_id: int) -> User | None:
        if not user_id in self.users:
            return None
        return self.users[user_id]

    def get_user_tasks(self, user_id: int) -> list[Task]:
        user_tasks = []
        for task in self.tasks.values():
            if task.assignee_id == user_id:
                user_tasks.append(task)
        user_tasks = sorted(user_tasks, key= lambda task: (task.due_date is None, task.due_date, task.priority, task.id))
        return user_tasks

    