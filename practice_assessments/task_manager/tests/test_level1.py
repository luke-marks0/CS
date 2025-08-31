import unittest
from simulation import TaskManager, TaskStatus


class TestLevel1TaskManager(unittest.TestCase):
    def setUp(self):
        self.manager = TaskManager()

    def test_level_1(self):
        # Test 1: Basic task creation
        task_id = self.manager.create_task("Buy groceries", "Milk, eggs, bread")
        self.assertEqual(task_id, 1)

        # Test 2: Task retrieval
        task = self.manager.get_task(1)
        self.assertIsNotNone(task)
        self.assertEqual(task.id, 1)
        self.assertEqual(task.title, "Buy groceries")
        self.assertEqual(task.description, "Milk, eggs, bread")
        self.assertEqual(task.status, TaskStatus.TODO)

        # Test 3: Multiple task creation with incrementing IDs
        task_id_2 = self.manager.create_task("Walk dog", "Take Max to the park")
        task_id_3 = self.manager.create_task("Finish report", "")
        self.assertEqual(task_id_2, 2)
        self.assertEqual(task_id_3, 3)

        # Test 4: Get all tasks
        all_tasks = self.manager.get_all_tasks()
        self.assertEqual(len(all_tasks), 3)
        self.assertEqual(all_tasks[0].id, 1)
        self.assertEqual(all_tasks[1].id, 2)
        self.assertEqual(all_tasks[2].id, 3)

        # Test 5: Status update
        success = self.manager.update_task_status(2, TaskStatus.IN_PROGRESS)
        self.assertTrue(success)
        updated_task = self.manager.get_task(2)
        self.assertEqual(updated_task.status, TaskStatus.IN_PROGRESS)

        # Test 6: Status update on non-existent task
        success = self.manager.update_task_status(999, TaskStatus.DONE)
        self.assertFalse(success)

        # Test 7: Get tasks by status
        todo_tasks = self.manager.get_tasks_by_status(TaskStatus.TODO)
        self.assertEqual(len(todo_tasks), 2)
        in_progress_tasks = self.manager.get_tasks_by_status(TaskStatus.IN_PROGRESS)
        self.assertEqual(len(in_progress_tasks), 1)
        self.assertEqual(in_progress_tasks[0].id, 2)
        done_tasks = self.manager.get_tasks_by_status(TaskStatus.DONE)
        self.assertEqual(len(done_tasks), 0)

        # Test 8: Task deletion
        success = self.manager.delete_task(1)
        self.assertTrue(success)
        deleted_task = self.manager.get_task(1)
        self.assertIsNone(deleted_task)

        # Test 9: Delete non-existent task
        success = self.manager.delete_task(999)
        self.assertFalse(success)

        # Test 10: Verify state after deletion
        remaining_tasks = self.manager.get_all_tasks()
        self.assertEqual(len(remaining_tasks), 2)
        self.assertEqual(remaining_tasks[0].id, 2)
        self.assertEqual(remaining_tasks[1].id, 3)

        # Test 11: Empty title validation
        with self.assertRaises(ValueError):
            self.manager.create_task("", "Some description")
        with self.assertRaises(ValueError):
            self.manager.create_task(None, "Some description")  # type: ignore

        # Test 12: Get non-existent task
        non_existent = self.manager.get_task(999)
        self.assertIsNone(non_existent)


if __name__ == "__main__":
    unittest.main()
