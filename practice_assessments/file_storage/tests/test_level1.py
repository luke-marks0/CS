import unittest
from simulation import FileStorage


class TestLevel1FileStorage(unittest.TestCase):
    """Level 1 – Initial Design & Basic Functions
    - FILE_UPLOAD(file_name, size)
    - FILE_GET(file_name) -> size or None
    - FILE_COPY(source, dest)
    """

    def setUp(self):
        self.store = FileStorage()

    def test_upload_then_get_returns_size(self):
        self.store.file_upload("Cars.txt", 200)
        self.assertEqual(self.store.file_get("Cars.txt"), 200)

    def test_upload_duplicate_raises_runtime_error(self):
        self.store.file_upload("Cars.txt", 200)
        with self.assertRaises(RuntimeError):
            self.store.file_upload("Cars.txt", 300)

    def test_get_missing_returns_none(self):
        self.assertIsNone(self.store.file_get("Missing.txt"))

    def test_copy_copies_size_to_destination(self):
        self.store.file_upload("A.txt", 123)
        self.store.file_copy("A.txt", "B.txt")
        self.assertEqual(self.store.file_get("B.txt"), 123)

    def test_copy_missing_source_raises_runtime_error(self):
        with self.assertRaises(RuntimeError):
            self.store.file_copy("Nope.txt", "B.txt")

    def test_copy_overwrites_existing_destination(self):
        self.store.file_upload("A.txt", 10)
        self.store.file_upload("B.txt", 99)
        self.store.file_copy("A.txt", "B.txt")
        self.assertEqual(self.store.file_get("B.txt"), 10)


if __name__ == "__main__":
    unittest.main()


