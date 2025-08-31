# Level 1: Basic Task Management

Implement a basic in-memory task manager that supports CRUD and status filtering.

Requirements:
- Task has fields: `id`, `title`, `description`, `status`.
- `TaskStatus` values: `TODO`, `IN_PROGRESS`, `DONE`.
- IDs start at 1 and increment by 1. IDs are never reused and are never renumbered after deletions.

Methods:
- `create_task(title, description)` -> int
  - Title must be non-empty; raise `ValueError` on empty/None.
  - New task starts with status `TODO`.
  - Returns the new task id.
- `get_task(task_id)` -> Task | None
  - Return `None` if `task_id` is not found.
- `get_all_tasks()` -> list[Task]
  - Ordered by creation time (oldest first) using the original creation order/IDs.
- `update_task_status(task_id, status)` -> bool
  - Return `True` if the task exists and its status was updated.
  - Return `False` if the task does not exist. Do not raise.
- `delete_task(task_id)` -> bool
  - Return `True` if the task existed and was removed; `False` otherwise.
  - Do not decrement or shift other task IDs. The remaining tasks keep their original IDs.
- `get_tasks_by_status(status)` -> list[Task]
  - Tasks with the specified status, ordered by creation time (oldest first).

Notes:
- Keep implementation simple; focus on passing tests.
- Do not mutate task IDs after creation.
