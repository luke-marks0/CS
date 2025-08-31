import unittest
from datetime import date, timedelta
from simulation import TaskManager, TaskStatus, TaskPriority


class TestLevel4TaskManager(unittest.TestCase):
    def setUp(self):
        self.m = TaskManager()
        self.owner = self.m.create_user("Owner", "owner@org.com")
        self.member = self.m.create_user("Dev", "dev@org.com")

    def test_project_creation_and_assignment(self):
        pid = self.m.create_project("Proj", "Desc", self.owner)
        self.assertIsNotNone(self.m.get_project(pid))
        tid = self.m.create_task("A", "")
        ok = self.m.assign_task_to_project(tid, pid)
        self.assertTrue(ok)
        tasks = self.m.get_project_tasks(pid)
        self.assertEqual([t.id for t in tasks], [tid])

    def test_project_tasks_sorted_priority_then_due(self):
        pid = self.m.create_project("P", "", self.owner)
        t1 = self.m.create_task_with_priority("Low", "", TaskPriority.LOW)
        t2 = self.m.create_task_with_priority("Urgent", "", TaskPriority.URGENT)
        t3 = self.m.create_task_with_priority("High", "", TaskPriority.HIGH)
        self.m.assign_task_to_project(t1, pid)
        self.m.assign_task_to_project(t2, pid)
        self.m.assign_task_to_project(t3, pid)
        today = date.today()
        self.m.set_due_date(t1, today + timedelta(days=1))
        self.m.set_due_date(t2, today + timedelta(days=5))
        self.m.set_due_date(t3, today + timedelta(days=1))
        ordered = [t.id for t in self.m.get_project_tasks(pid)]
        # URGENT first regardless of due, then among remaining by due date
        self.assertEqual(ordered[0], t2)

    def test_templates_creation_and_instantiation(self):
        pid = self.m.create_project("Alpha", "", self.owner)
        tpl = self.m.create_task_template(
            name="BugFix",
            title_template="Fix in {project_name}",
            description_template="Investigate in {project_name}",
            default_priority=TaskPriority.HIGH,
            estimated_hours=3.5,
        )
        tid = self.m.create_task_from_template(tpl, project_id=pid)
        t = self.m.get_task(tid)
        self.assertIn("Alpha", t.title)
        self.assertEqual(t.priority, TaskPriority.HIGH)
        self.assertEqual(t.project_id, pid)

    def test_tags_and_search(self):
        t1 = self.m.create_task("Refactor", "Improve code quality")
        t2 = self.m.create_task("Ref", "Refactor module")
        self.m.add_task_tags(t1, ["tech-debt", "backend"])
        self.m.add_task_tags(t2, ["backend"])
        with_all = [t.id for t in self.m.get_tasks_by_tags(["backend", "tech-debt"], match_all=True)]
        self.assertEqual(with_all, [t1])
        with_any = [t.id for t in self.m.get_tasks_by_tags(["backend", "frontend"], match_all=False)]
        self.assertCountEqual(with_any, [t1, t2])
        # Search ranking: exact title match first
        results = [t.id for t in self.m.search_tasks("Refactor")]
        self.assertEqual(results[0], t1)

    def test_time_logging_and_reports(self):
        tid = self.m.create_task("Implement", "")
        self.m.assign_task(tid, self.member)
        self.m.log_time(tid, self.member, 2.0, "Initial work")
        self.m.log_time(tid, self.member, 1.0, "More work", log_date=date.today() - timedelta(days=1))
        entries = self.m.get_task_time_entries(tid)
        self.assertGreaterEqual(len(entries), 2)
        total = self.m.get_total_time_spent(tid)
        self.assertAlmostEqual(total, 3.0, places=4)
        user_entries = self.m.get_user_time_entries(self.member)
        self.assertGreaterEqual(len(user_entries), 2)
        # Productivity report last 7 days should count completed tasks and hours
        self.m.update_task_status(tid, TaskStatus.DONE)
        report = self.m.get_productivity_report(self.member, 7)
        self.assertIn("tasks_completed", report)
        self.assertIn("hours_logged", report)

    def test_bulk_update_task_status(self):
        ids = [self.m.create_task(f"T{i}", "") for i in range(5)]
        updated = self.m.bulk_update_task_status(ids, TaskStatus.IN_PROGRESS)
        self.assertEqual(updated, 5)
        for tid in ids:
            self.assertEqual(self.m.get_task(tid).status, TaskStatus.IN_PROGRESS)


if __name__ == "__main__":
    unittest.main()
