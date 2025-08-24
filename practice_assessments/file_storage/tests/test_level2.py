import unittest
from simulation import FileStorage


class TestLevel2Search(unittest.TestCase):
    """Level 2 – FILE_SEARCH(prefix)
    Returns up to 10 file names starting with prefix, ordered by:
      1) size descending
      2) name ascending for ties
    """

    def setUp(self):
        self.store = FileStorage()

    def test_search_sorted_and_top10(self):
        # Add a variety of files, some matching prefix 'Ba'
        files = [
            ("Foo.txt", 100),
            ("Bar.csv", 200),
            ("Baz.pdf", 300),
            ("Bam.doc", 300),
            ("BaA.txt", 300),
            ("BaZ.txt", 250),
            ("BaY.txt", 250),
            ("BaX.txt", 250),
            ("BaW.txt", 250),
            ("BaV.txt", 250),
            ("BaU.txt", 250),
            ("BaT.txt", 250),
            ("BaS.txt", 250),  # ensures more than 10 matches
        ]
        for name, size in files:
            self.store.file_upload(name, size)

        result = self.store.file_search("Ba")

        # Expected: top 10 by size desc then name asc
        # First come all 300-size with names ascending
        top_expected = [
            "BaA.txt",  # 300
            "Bam.doc",  # 300
            "Baz.pdf",  # 300
        ]
        # Then 250-size names ascending, limited to fill to 10 total
        # Gather all 250 prefix 'Ba' names and sort
        size_250 = sorted([
            "BaS.txt", "BaT.txt", "BaU.txt", "BaV.txt", "BaW.txt", "BaX.txt", "BaY.txt", "BaZ.txt"
        ])
        # We already have 3, need 7 more to make 10
        top_expected.extend(size_250[:7])

        self.assertEqual(result, top_expected)

    def test_search_no_matches_returns_empty(self):
        self.store.file_upload("Alpha.txt", 1)
        self.assertEqual(self.store.file_search("Ba"), [])

    def test_copy_then_search_uses_destination_name(self):
        # Copy should update the stored name so search by destination prefix works
        self.store.file_upload("A.txt", 100)
        self.store.file_copy("A.txt", "B.txt")

        # Should find B.txt via prefix 'B' and not duplicate under 'A'
        self.assertEqual(self.store.file_search("B"), ["B.txt"])
        self.assertEqual(self.store.file_search("A"), ["A.txt"])

    def test_search_prefix_case_sensitivity(self):
        # Verify that matching is case-sensitive (per straightforward .startswith behavior)
        self.store.file_upload("Case.txt", 5)
        self.assertEqual(self.store.file_search("case"), [])
        self.assertEqual(self.store.file_search("Cas"), ["Case.txt"])

    def test_search_limits_to_top_10(self):
        for i in range(20):
            # Ensure all match prefix 'X'; sizes descending so first 10 are the largest
            self.store.file_upload(f"X{i:02d}.txt", 1000 - i)
        result = self.store.file_search("X")
        self.assertEqual(len(result), 10)
        # First element should be the largest size name (X00)
        self.assertEqual(result[0], "X00.txt")


if __name__ == "__main__":
    unittest.main()


