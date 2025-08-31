import unittest
from datetime import date, timedelta
from simulation import TaskManager, TaskStatus, TaskPriority


class TestLevel3TaskManager(unittest.TestCase):
    def setUp(self):
        self.m = TaskManager()

    def test_create_and_get_user(self):
        uid = self.m.create_user("Alice", "alice@example.com")
        user = self.m.get_user(uid)
        self.assertIsNotNone(user)
        self.assertEqual(user.name, "Alice")

    def test_create_user_validation(self):
        with self.assertRaises(ValueError):
            self.m.create_user("", "x@example.com")
        with self.assertRaises(ValueError):
            self.m.create_user("Bob", "")

    def test_assign_and_unassign_task(self):
        uid = self.m.create_user("Alice", "alice@example.com")
        tid = self.m.create_task("A", "")
        ok = self.m.assign_task(tid, uid)
        self.assertTrue(ok)
        self.assertEqual(self.m.get_task(tid).assignee_id, uid)
        ok2 = self.m.unassign_task(tid)
        self.assertTrue(ok2)
        self.assertIsNone(self.m.get_task(tid).assignee_id)

    def test_cannot_assign_done_task(self):
        uid = self.m.create_user("Alice", "alice@example.com")
        tid = self.m.create_task("A", "")
        self.m.update_task_status(tid, TaskStatus.DONE)
        self.assertFalse(self.m.assign_task(tid, uid))

    def test_get_user_tasks_sorted(self):
        uid = self.m.create_user("U", "u@e.com")
        t1 = self.m.create_task("T1", "")
        t2 = self.m.create_task_with_priority("T2", "", TaskPriority.URGENT)
        t3 = self.m.create_task_with_priority("T3", "", TaskPriority.LOW)
        today = date.today()
        self.m.assign_task(t1, uid)
        self.m.assign_task(t2, uid)
        self.m.assign_task(t3, uid)
        self.m.set_due_date(t1, today + timedelta(days=5))
        self.m.set_due_date(t2, today + timedelta(days=5))
        self.m.set_due_date(t3, today + timedelta(days=1))
        # Expected order: t3 (earliest due), then among t1/t2 with same due, URGENT first
        ordered_ids = [t.id for t in self.m.get_user_tasks(uid)]
        self.assertEqual(ordered_ids, [t3, t2, t1])

    def test_overdue_detection_and_update(self):
        uid = self.m.create_user("U", "u@e.com")
        t1 = self.m.create_task("T1", "")
        self.m.assign_task(t1, uid)
        yesterday = date.today() - timedelta(days=1)
        self.m.set_due_date(t1, yesterday)
        overdue = self.m.get_overdue_tasks()
        self.assertIn(t1, [t.id for t in overdue])
        changes = self.m.update_overdue_status()
        self.assertGreaterEqual(changes, 1)
        self.assertEqual(self.m.get_task(t1).status, TaskStatus.OVERDUE)

    def test_get_tasks_due_soon(self):
        t1 = self.m.create_task("Soon", "")
        t2 = self.m.create_task("Later", "")
        self.m.set_due_date(t1, date.today() + timedelta(days=2))
        self.m.set_due_date(t2, date.today() + timedelta(days=10))
        soon = [t.id for t in self.m.get_tasks_due_soon(5)]
        self.assertIn(t1, soon)
        self.assertNotIn(t2, soon)

    def test_bulk_assign_and_summary_by_user(self):
        u1 = self.m.create_user("A", "a@e.com")
        u2 = self.m.create_user("B", "b@e.com")
        ids = [self.m.create_task(f"T{i}", "") for i in range(3)]
        assigned = self.m.bulk_assign_tasks(ids, u1)
        self.assertEqual(assigned, 3)
        summary = self.m.get_task_summary_by_user()
        self.assertIn(u1, summary)
        # Counts may vary by status, but u2 should be present with empty or zeroed dict
        self.assertIn(u2, summary)


if __name__ == "__main__":
    unittest.main()
