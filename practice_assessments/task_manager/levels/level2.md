# Level 2: Dependencies and Priorities

Extend Level 1 with priorities, dependencies, and smart status management.

Additions:
- `TaskPriority`: `LOW`, `MEDIUM` (default), `HIGH`, `URGENT`.
- Each task has a `priority` and a set of `dependencies` (task IDs it depends on).

New/Updated methods:
- `create_task_with_priority(title, description, priority)` -> int
  - Same validation as `create_task`. Sets initial status `TODO` and provided priority.
- `update_task_priority(task_id, priority)` -> bool
  - Return `True` if updated, `False` if task does not exist.
- `add_dependency(task_id, depends_on_task_id)` -> bool
  - Both tasks must exist; return `False` otherwise.
  - Cannot depend on self; return `False`.
  - Cannot create circular dependencies (directly or indirectly); return `False`.
  - Dependency can only be added if the target task (the one gaining the dependency) is not `DONE`; return `False` if it is `DONE`.
  - On success, add `depends_on_task_id` to the task's `dependencies` and return `True`.
- `remove_dependency(task_id, depends_on_task_id)` -> bool
  - Return `True` if the dependency existed and was removed; `False` otherwise.
- `get_available_tasks()` -> list[Task]
  - Tasks with status `TODO` whose dependencies are all `DONE`.
  - Sorted by priority (URGENT first, then HIGH, MEDIUM, LOW), then by creation time (oldest first) for same priority.
  - Return `[]` when no tasks meet this criterion; tasks with no dependencies are included as available.
- `get_blocked_tasks()` -> list[Task]
  - Tasks with status `TODO` or `BLOCKED` that have at least one incomplete dependency (not `DONE`).
  - Ordered by creation time (oldest first).
  - Return `[]` when no tasks meet this criterion (i.e., no tasks have incomplete dependencies).
- `auto_update_blocked_status()` -> int
  - If `TODO` and has incomplete deps, set to `BLOCKED`.
  - If `BLOCKED` and all deps complete, set to `TODO`.
  - Do not change `IN_PROGRESS` or `DONE` tasks.
  - Return the count of tasks whose status changed.

Notes:
- Preserve all Level 1 behavior.
- Implement cycle detection (DFS/BFS) to prevent circular dependencies.
- Deleting a task should remove that task's ID from other tasks' `dependencies` (see Level 2 tests).
- A `TODO` task with no dependencies is considered available and must not appear in `get_blocked_tasks()`.