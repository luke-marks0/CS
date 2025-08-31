# Level 3: Users, Assignments, and Deadlines

Build on Levels 1-2 by adding user management, assignments, and due dates.

New entities:
- `User { id, name, email }`

Task additions:
- New `TaskStatus`: `OVERDUE`.
- Task fields extended with: `assignee_id: int | None`, `due_date: date | None`, `created_date: date`.

New methods:
- `create_user(name, email)` -> int
  - Name and email must be non-empty; raise `ValueError` otherwise.
- `get_user(user_id)` -> User | None
- `assign_task(task_id, user_id)` -> bool
  - Both must exist; return `False` if either is missing.
  - Cannot assign tasks with status `DONE`; return `False`.
  - On success, set `assignee_id` and return `True`.
- `unassign_task(task_id)` -> bool
  - Return `True` if task existed (assignment is cleared if present), `False` if task missing.
- `get_user_tasks(user_id)` -> list[Task]
  - Tasks assigned to the user, ordered by:
    1) due date ascending (tasks without due dates sort after those with dates),
    2) priority (URGENT first, then HIGH, MEDIUM, LOW),
    3) creation time (oldest first).
- `set_due_date(task_id, due_date)` -> bool
  - Return `True` if task exists and date set, `False` otherwise.
- `get_overdue_tasks()` -> list[Task]
  - Tasks with a due date earlier than today and status not `DONE`.
  - Ordered by how overdue they are (most overdue first), breaking ties by creation time (oldest first).
- `update_overdue_status()` -> int
  - For tasks with due date before today and status not `DONE`, set status to `OVERDUE`.
  - Do not change `DONE` tasks.
  - Return number of tasks changed to `OVERDUE`.
- `get_tasks_due_soon(days)` -> list[Task]
  - Tasks due within the next `days` days inclusive (>= today and <= today+days), ordered by due date ascending.
- `bulk_assign_tasks(task_ids, user_id)` -> int
  - Assign multiple tasks; skip tasks that are missing or `DONE`.
  - Return the count successfully assigned.
- `get_task_summary_by_user()` -> dict[user_id, dict[str, int]]
  - Map each user to counts of tasks by status.
  - Include users with 0 tasks as empty dictionaries ({}).

Notes:
- Preserve all Level 1 & 2 functionality.
- Use `datetime.date.today()` to evaluate `overdue` and `due soon` conditions.
