# Level 4: Projects, Templates, and Time Tracking

Extend Level 3 by adding projects, task templates, tags, advanced search, and time logging/reporting.

New entities:
- `Project { id, name, description, owner_id, created_date }`
- `TaskTemplate { id, name, title_template, description_template, default_priority, estimated_hours? }`
- `TimeEntry { task_id, user_id, hours, date, description }`

Task additions:
- Extend Task with: `project_id: int | None`, `estimated_hours: float | None`, `tags: set[str]`.

New methods:
- `create_project(name, description, owner_id)` -> int
  - Return new project id. Must be able to retrieve via `get_project`.
- `get_project(project_id)` -> Project | None
- `assign_task_to_project(task_id, project_id)` -> bool
  - Return `True` if both exist and assignment updated; `False` otherwise.
- `get_project_tasks(project_id)` -> list[Task]
  - Ordered by priority (URGENT, HIGH, MEDIUM, LOW) then by due date (earliest first; tasks without due dates sort after those with dates), then by creation time.
- `create_task_template(name, title_template, description_template, default_priority, estimated_hours=None)` -> int
- `create_task_from_template(template_id, project_id=None)` -> int
  - Use template to create a new task. If `project_id` provided, set `project_id` and substitute `{project_name}` in title and description using the project's name.
- `add_task_tags(task_id, tags)` -> bool
  - Add all provided tags (normalized as-is); return `True` if task exists, else `False`.
- `remove_task_tags(task_id, tags)` -> bool
  - Remove provided tags; return `True` if task exists, else `False`.
- `get_tasks_by_tags(tags, match_all=True)` -> list[Task]
  - If `match_all=True`, only tasks containing all tags qualify; else tasks containing any of the tags.
  - Order by creation time (oldest first).
- `log_time(task_id, user_id, hours, description, log_date=None)` -> bool
  - Append a time entry (use `date.today()` if `log_date` None). Return `True` if task and user exist, else `False`.
- `get_task_time_entries(task_id)` -> list[TimeEntry]
  - Ordered by date (newest first), then insertion order for identical dates.
- `get_user_time_entries(user_id, start_date=None, end_date=None)` -> list[TimeEntry]
  - Filter by optional date range inclusive; ordered by date (newest first).
- `get_total_time_spent(task_id)` -> float
  - Sum of hours for that task (0.0 if none or task missing).
- `search_tasks(query, project_id=None, assignee_id=None, status=None)` -> list[Task]
  - Case-insensitive search in title and description.
  - Ranking: exact title match first; then title substring matches; then description substring matches. Within each tier, order by creation time (oldest first).
  - Apply optional filters if provided.
- `get_project_progress(project_id)` -> { "total": int, "done": int, "percent_complete": float }
  - `percent_complete` is `(done / total) * 100` (0.0 when total == 0).
- `bulk_update_task_status(task_ids, status)` -> int
  - Update status for each existing task; return count of tasks updated.
- `get_productivity_report(user_id, days)` -> { "tasks_completed": int, "hours_logged": float }
  - Tasks completed: number of tasks assigned to the user that transitioned to `DONE` in the last `days` days (assume "last N days" based on `date.today()` and task status/date tracking you implement).
  - Hours logged: sum of user's time entries within last `days` days.

Notes:
- Preserve all prior levels' behavior.
- Be careful with string templating and ordering requirements.
- For simplicity, if you do not track completion dates for tasks, count tasks currently `DONE` and hours logged within the window (tests will accept a reasonable approach based on available state).
