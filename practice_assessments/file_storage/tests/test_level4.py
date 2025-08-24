import unittest
from simulation import FileStorage


class TestLevel4Rollback(unittest.TestCase):
    """Level 4 – ROLLBACK(timestamp_ms)
    Roll back the entire storage state to the given timestamp in UNIX epoch milliseconds (UTC).
    TTLs should be recalculated relative to that timestamp. All timestamps and TTLs in these tests are in ms.
    """

    def setUp(self):
        self.store = FileStorage()

    def test_rollback_restores_state_and_ttls(self):
        # Base: 2021-07-01T12:00:00Z -> 1625140800000 ms
        t0 = 1625140800000
        t_12_05 = t0 + 300_000
        t_12_10 = t0 + 600_000
        t_12_15 = t0 + 900_000
        t_12_20 = t0 + 1_200_000
        t_12_25 = t0 + 1_500_000

        # Upload infinite TTL at t0
        self.store.file_upload_at(t0, "Initial.txt", 100)
        # Upload with ttl 3_600_000 ms (1 hour) at t1
        self.store.file_upload_at(t_12_05, "Ephemeral.txt", 150, ttl=3_600_000)
        # At t2, both exist
        self.assertEqual(self.store.file_get_at(t_12_10, "Initial.txt"), 100)
        self.assertEqual(self.store.file_get_at(t_12_10, "Ephemeral.txt"), 150)

        # Upload another with short ttl and copy something
        self.store.file_upload_at(t_12_20, "Short.txt", 200, ttl=1_800_000)
        self.store.file_copy_at(t_12_15, "Ephemeral.txt", "EphemeralCopy.txt")
        # Now rollback to 12:10:00
        self.store.rollback(t_12_10)

        # After rollback, state is as-of 12:10:00. Short.txt shouldn't exist yet
        self.assertIsNone(self.store.file_get_at(t_12_10, "Short.txt"))
        # Ephemeral still alive at 12:10:00; copy performed after rollback point should not exist
        self.assertIsNone(self.store.file_get_at(t_12_10, "EphemeralCopy.txt"))

        # TTLs recalculated relative to rollback time: at 12:25:00 (15m after rollback point),
        # Ephemeral (ttl=3_600_000 ms) is still alive; Initial is infinite
        self.assertEqual(self.store.file_get_at(t_12_25, "Ephemeral.txt"), 150)
        self.assertEqual(self.store.file_get_at(t_12_25, "Initial.txt"), 100)

    def test_rollback_before_first_snapshot_resets_to_empty(self):
        # No time-based operations yet; rolling back before any backups should reset to empty (Option B)
        self.store.file_upload("A.txt", 1)
        t0 = 1625140800000
        self.store.rollback(t0)
        self.assertIsNone(self.store.file_get("A.txt"))

    def test_multiple_rollbacks_choose_latest_at_or_before(self):
        t0 = 1625140800000
        t1 = t0 + 1000
        t2 = t0 + 2000
        t3 = t0 + 3000

        self.store.file_upload_at(t0, "A.txt", 10)
        self.store.file_upload_at(t1, "B.txt", 20)
        self.store.file_upload_at(t2, "C.txt", 30)

        # Roll back to just after t1: expect A and B, not C
        self.store.rollback(t1 + 1)
        self.assertEqual(self.store.file_get_at(t1 + 1, "A.txt"), 10)
        self.assertEqual(self.store.file_get_at(t1 + 1, "B.txt"), 20)
        self.assertIsNone(self.store.file_get_at(t1 + 1, "C.txt"))

        # Roll forward (another rollback) to just after t2: expect A, B, C
        self.store.rollback(t2 + 1)
        self.assertEqual(self.store.file_get_at(t2 + 1, "C.txt"), 30)

    def test_rollback_resets_timestamps_for_ttl_calculation(self):
        t0 = 1625140800000
        t1 = t0 + 1000
        t2 = t0 + 2000
        # Upload with ttl 3000ms at t1
        self.store.file_upload_at(t1, "TTL.txt", 1, ttl=3000)
        # Rollback to t0 should still keep TTL.txt out (it didn't exist yet)
        self.store.rollback(t0)
        self.assertIsNone(self.store.file_get_at(t0, "TTL.txt"))

        # Now roll forward to t2 (after redoing upload and backup)
        self.store.file_upload_at(t1, "TTL.txt", 1, ttl=3000)
        self.store.rollback(t2)
        # After rollback to t2, timestamp should be t2; so expiration should be at t2+3000
        self.assertEqual(self.store.file_get_at(t2 + 2999, "TTL.txt"), 1)
        self.assertIsNone(self.store.file_get_at(t2 + 3000, "TTL.txt"))


if __name__ == "__main__":
    unittest.main()


