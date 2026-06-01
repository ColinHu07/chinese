import unittest

from captions import CaptionDeduper


class CaptionDeduperTests(unittest.TestCase):
    def test_repeated_caption_is_skipped(self):
        deduper = CaptionDeduper()
        self.assertEqual(deduper.filter("Where is the subway station?"), "Where is the subway station?")
        self.assertIsNone(deduper.filter("Where is the subway station?"))

    def test_started_with_old_caption_prints_suffix(self):
        deduper = CaptionDeduper()
        self.assertEqual(deduper.filter("I want two tickets"), "I want two tickets")
        self.assertEqual(deduper.filter("I want two tickets to Shanghai"), "to Shanghai")

    def test_word_overlap_prints_new_suffix(self):
        deduper = CaptionDeduper(similarity_threshold=99)
        self.assertEqual(deduper.filter("where is line ten"), "where is line ten")
        self.assertEqual(deduper.filter("line ten is downstairs"), "is downstairs")


if __name__ == "__main__":
    unittest.main()
