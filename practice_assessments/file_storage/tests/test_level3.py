import unittest
from simulation import FileStorage


class TestLevel3TimeBasedOps(unittest.TestCase):
    """Level 3 – time-based variants and TTL handling.
    Methods expected on FileStorage:
      - file_upload_at(timestamp_ms: int, name: str, size: int, ttl_ms: int | None = None)
      - file_get_at(timestamp_ms: int, name: str) -> int | None
      - file_copy_at(timestamp_ms: int, src: str, dest: str)
      - file_search_at(timestamp_ms: int, prefix: str) -> list[str]
    Notes:
      - Timestamps are UNIX epoch milliseconds (UTC). TTL values are in milliseconds.
      - Only alive files at the given timestamp should be visible.
    """

    def setUp(self):
        self.store = FileStorage()

    def test_upload_at_and_get_at_with_ttl(self):
        # Base time: 2021-07-01T12:00:00Z -> 1625140800000 ms
        # ttl 2000 ms, alive at t=+1s, expired by t=+3s
        t0 = 1625140800000
        self.store.file_upload_at(t0, "Temp.txt", 100, ttl=2000)
        self.assertEqual(self.store.file_get_at(t0 + 1000, "Temp.txt"), 100)
        self.assertIsNone(self.store.file_get_at(t0 + 3000, "Temp.txt"))

    def test_copy_at_requires_alive_source(self):
        t0 = 1625140800000
        self.store.file_upload_at(t0, "Src.txt", 10, ttl=1000)
        # At upload time it's alive; copying later when expired should raise
        with self.assertRaises(RuntimeError):
            self.store.file_copy_at(t0 + 2000, "Src.txt", "Dst.txt")
        # Copying at a valid time should succeed
        self.store.file_copy_at(t0, "Src.txt", "Dst.txt")
        self.assertEqual(self.store.file_get_at(t0, "Dst.txt"), 10)

    def test_search_at_only_returns_alive_sorted(self):
        t0 = 1625140800000
        self.store.file_upload_at(t0, "AliveA.txt", 300)
        self.store.file_upload_at(t0, "AliveB.txt", 200)
        self.store.file_upload_at(t0, "Dead.txt", 999, ttl=1000)

        # At t0+2s, Dead.txt expired; search prefix 'A' should include AliveA and AliveB only
        result = self.store.file_search_at(t0 + 2000, "A")
        # Order by size desc then name asc
        self.assertEqual(result, ["AliveA.txt", "AliveB.txt"])  # 300 then 200

    def test_get_at_on_non_timed_upload_is_safe(self):
        # Files uploaded without _at should be visible to time-based queries and treated as infinite TTL
        self.store.file_upload("NonTimed.txt", 42)
        t0 = 1625140800000
        self.assertEqual(self.store.file_get_at(t0, "NonTimed.txt"), 42)

    def test_copy_at_sets_destination_name_and_timestamp(self):
        t0 = 1625140800000
        self.store.file_upload_at(t0, "Src.txt", 10, ttl=5000)

        # Copy at t0+1000 should be alive at that moment and should carry the destination name
        self.store.file_copy_at(t0 + 1000, "Src.txt", "Dst.txt")
        # Search by destination prefix; ensure name is Dst.txt
        self.assertEqual(self.store.file_search_at(t0 + 1000, "D"), ["Dst.txt"])

        # If copy timestamp anchors lifetime, Dst.txt should expire at t0+1000+5000, but be gone by +6001
        self.assertEqual(self.store.file_get_at(t0 + 1000 + 4999, "Dst.txt"), 10)
        self.assertIsNone(self.store.file_get_at(t0 + 1000 + 6000, "Dst.txt"))

    def test_expiration_edge_at_exact_boundary(self):
        t0 = 1625140800000
        # ttl=2000ms: alive up to t0+1999, not alive at t0+2000
        self.store.file_upload_at(t0, "Edge.txt", 1, ttl=2000)
        self.assertEqual(self.store.file_get_at(t0 + 1999, "Edge.txt"), 1)
        self.assertIsNone(self.store.file_get_at(t0 + 2000, "Edge.txt"))

    def test_search_at_ignores_expired_and_sorts_ties_by_name(self):
        t0 = 1625140800000
        self.store.file_upload_at(t0, "A.txt", 10)
        self.store.file_upload_at(t0, "B.txt", 10, ttl=1)
        # At t0+2, B expired; only A remains. Tie-breaking by name is implicit in single result
        self.assertEqual(self.store.file_search_at(t0 + 2, ""), ["A.txt"])  # empty prefix matches all


if __name__ == "__main__":
    unittest.main()


