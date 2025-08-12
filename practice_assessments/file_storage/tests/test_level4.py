import unittest
from simulation import FileStorage


class TestLevel4Rollback(unittest.TestCase):
    """Level 4 – ROLLBACK(timestamp)
    Roll back the entire storage state to the given timestamp. TTLS should be
    recalculated relative to that timestamp.
    """

    def setUp(self):
        self.store = FileStorage()

    def test_rollback_restores_state_and_ttls(self):
        # Upload infinite TTL at t0
        self.store.file_upload_at("2021-07-01T12:00:00", "Initial.txt", 100)
        # Upload with ttl 3600 at t1
        self.store.file_upload_at("2021-07-01T12:05:00", "Ephemeral.txt", 150, ttl=3600)
        # At t2, both exist
        self.assertEqual(self.store.file_get_at("2021-07-01T12:10:00", "Initial.txt"), 100)
        self.assertEqual(self.store.file_get_at("2021-07-01T12:10:00", "Ephemeral.txt"), 150)

        # Upload another with short ttl and copy something
        self.store.file_upload_at("2021-07-01T12:20:00", "Short.txt", 200, ttl=1800)
        self.store.file_copy_at("2021-07-01T12:15:00", "Ephemeral.txt", "EphemeralCopy.txt")
        # Now rollback to 12:10:00
        self.store.rollback("2021-07-01T12:10:00")

        # After rollback, state is as-of 12:10:00. Short.txt shouldn't exist yet
        self.assertIsNone(self.store.file_get_at("2021-07-01T12:10:00", "Short.txt"))
        # Ephemeral still alive at 12:10:00; copy performed after rollback point should not exist
        self.assertIsNone(self.store.file_get_at("2021-07-01T12:10:00", "EphemeralCopy.txt"))

        # TTLs recalculated relative to rollback time: at 12:25:00 (15m after rollback point),
        # Ephemeral (ttl=3600) is still alive; Initial is infinite
        self.assertEqual(self.store.file_get_at("2021-07-01T12:25:00", "Ephemeral.txt"), 150)
        self.assertEqual(self.store.file_get_at("2021-07-01T12:25:00", "Initial.txt"), 100)


if __name__ == "__main__":
    unittest.main()


