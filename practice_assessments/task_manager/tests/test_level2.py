import unittest
from simulation import TaskManager, TaskStatus, TaskPriority


class TestLevel2TaskManager(unittest.TestCase):
    def setUp(self):
        self.m = TaskManager()

    def test_level1_defaults_still_work(self):
        a = self.m.create_task("Task 1", "First task")
        b = self.m.create_task("Task 2", "Second task")
        t1 = self.m.get_task(a)
        self.assertEqual(t1.priority, TaskPriority.MEDIUM)
        self.assertEqual(len(t1.dependencies), 0)

    def test_create_with_custom_priority(self):
        tid = self.m.create_task_with_priority("Urgent", "Very important", TaskPriority.URGENT)
        t = self.m.get_task(tid)
        self.assertEqual(t.priority, TaskPriority.URGENT)

    def test_update_priority(self):
        tid = self.m.create_task("A", "")
        ok = self.m.update_task_priority(tid, TaskPriority.HIGH)
        self.assertTrue(ok)
        self.assertEqual(self.m.get_task(tid).priority, TaskPriority.HIGH)

    def test_add_valid_dependency(self):
        t1 = self.m.create_task("A", "")
        t2 = self.m.create_task("B", "")
        ok = self.m.add_dependency(t2, t1)
        self.assertTrue(ok)
        self.assertIn(t1, self.m.get_task(t2).dependencies)

    def test_prevent_self_dependency(self):
        t1 = self.m.create_task("A", "")
        self.assertFalse(self.m.add_dependency(t1, t1))

    def test_prevent_circular_dependency(self):
        t1 = self.m.create_task("A", "")
        t2 = self.m.create_task("B", "")
        self.assertTrue(self.m.add_dependency(t2, t1))
        self.assertFalse(self.m.add_dependency(t1, t2))

    def test_add_dependency_missing_task(self):
        t1 = self.m.create_task("A", "")
        self.assertFalse(self.m.add_dependency(999, t1))
        self.assertFalse(self.m.add_dependency(t1, 999))

    def test_cannot_add_dependency_if_target_task_done(self):
        t1 = self.m.create_task("A", "")
        t2 = self.m.create_task("B", "")
        self.m.update_task_status(t2, TaskStatus.DONE)
        self.assertFalse(self.m.add_dependency(t2, t1))

    def test_get_available_tasks_sorted(self):
        a = self.m.create_task("A", "")
        b = self.m.create_task("B", "")
        c = self.m.create_task_with_priority("C", "", TaskPriority.URGENT)
        # B depends on A -> blocked until A done
        self.m.add_dependency(b, a)
        available = self.m.get_available_tasks()
        ids = [t.id for t in available]
        self.assertIn(a, ids)
        self.assertIn(c, ids)
        self.assertNotIn(b, ids)
        # URGENT first
        self.assertEqual(available[0].id, c)

    def test_get_blocked_tasks(self):
        a = self.m.create_task("A", "")
        b = self.m.create_task("B", "")
        self.m.add_dependency(b, a)
        blocked_ids = [t.id for t in self.m.get_blocked_tasks()]
        self.assertIn(b, blocked_ids)
        self.assertNotIn(a, blocked_ids)

    def test_auto_update_blocked_status(self):
        a = self.m.create_task("A", "")
        b = self.m.create_task("B", "")
        self.m.add_dependency(b, a)
        changes = self.m.auto_update_blocked_status()
        self.assertEqual(changes, 1)
        self.assertEqual(self.m.get_task(b).status, TaskStatus.BLOCKED)
        self.m.update_task_status(a, TaskStatus.DONE)
        changes = self.m.auto_update_blocked_status()
        self.assertEqual(changes, 1)
        self.assertEqual(self.m.get_task(b).status, TaskStatus.TODO)

    def test_remove_dependency(self):
        a = self.m.create_task("A", "")
        b = self.m.create_task("B", "")
        self.m.add_dependency(b, a)
        self.assertTrue(self.m.remove_dependency(b, a))
        self.assertFalse(self.m.remove_dependency(b, a))

    def test_delete_task_removes_from_other_dependencies(self):
        x = self.m.create_task("X", "")
        y = self.m.create_task("Y", "")
        self.m.add_dependency(y, x)
        self.m.delete_task(x)
        self.assertNotIn(x, self.m.get_task(y).dependencies)

    def test_complex_chain_availability(self):
        t4 = self.m.create_task("T4", "")
        t5 = self.m.create_task_with_priority("T5", "", TaskPriority.LOW)
        t6 = self.m.create_task_with_priority("T6", "", TaskPriority.HIGH)
        self.m.add_dependency(t6, t5)
        self.m.add_dependency(t5, t4)
        ids = [t.id for t in self.m.get_available_tasks()]
        self.assertIn(t4, ids)
        self.assertNotIn(t5, ids)
        self.assertNotIn(t6, ids)


if __name__ == "__main__":
    unittest.main()
