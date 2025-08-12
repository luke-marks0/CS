import unittest
from simulation import FileStorage


class TestLevel3TimeBasedOps(unittest.TestCase):
    """Level 3 – time-based variants and TTL handling.
    Methods expected on FileStorage:
      - file_upload_at(timestamp: str, name: str, size: int, ttl: int | None = None)
      - file_get_at(timestamp: str, name: str) -> int | None
      - file_copy_at(timestamp: str, src: str, dest: str)
      - file_search_at(timestamp: str, prefix: str) -> list[str]
    Notes:
      - Only alive files at given timestamp should be visible.
    """

    def setUp(self):
        self.store = FileStorage()

    def test_upload_at_and_get_at_with_ttl(self):
        # ttl 2 seconds, alive at t=+1, expired at t=+3
        self.store.file_upload_at("2021-07-01T12:00:00", "Temp.txt", 100, ttl=2)
        self.assertEqual(self.store.file_get_at("2021-07-01T12:00:01", "Temp.txt"), 100)
        self.assertIsNone(self.store.file_get_at("2021-07-01T12:00:03", "Temp.txt"))

    def test_copy_at_requires_alive_source(self):
        self.store.file_upload_at("2021-07-01T12:00:00", "Src.txt", 10, ttl=1)
        # At upload time it's alive; copying later when expired should raise
        with self.assertRaises(RuntimeError):
            self.store.file_copy_at("2021-07-01T12:00:02", "Src.txt", "Dst.txt")
        # Copying at a valid time should succeed
        self.store.file_copy_at("2021-07-01T12:00:00", "Src.txt", "Dst.txt")
        self.assertEqual(self.store.file_get_at("2021-07-01T12:00:00", "Dst.txt"), 10)

    def test_search_at_only_returns_alive_sorted(self):
        self.store.file_upload_at("2021-07-01T12:00:00", "AliveA.txt", 300)
        self.store.file_upload_at("2021-07-01T12:00:00", "AliveB.txt", 200)
        self.store.file_upload_at("2021-07-01T12:00:00", "Dead.txt", 999, ttl=1)

        # At 12:00:02, Dead.txt expired; search prefix 'A' should include AliveA and AliveB only
        result = self.store.file_search_at("2021-07-01T12:00:02", "A")
        # Order by size desc then name asc
        self.assertEqual(result, ["AliveA.txt", "AliveB.txt"])  # 300 then 200


if __name__ == "__main__":
    unittest.main()


