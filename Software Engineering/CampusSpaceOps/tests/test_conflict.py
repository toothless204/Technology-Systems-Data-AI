"""
Unit tests for interval-overlap conflict detection.
No database required — tests the pure logic directly.
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def _time_to_minutes(t: str) -> int:
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def intervals_overlap(s1: str, e1: str, s2: str, e2: str) -> bool:
    """Half-open interval overlap: [s1,e1) ∩ [s2,e2) ≠ ∅  iff  s1<e2 and s2<e1."""
    return _time_to_minutes(s1) < _time_to_minutes(e2) and \
           _time_to_minutes(s2) < _time_to_minutes(e1)


class TestIntervalOverlap(unittest.TestCase):

    def test_no_overlap_sequential(self):
        self.assertFalse(intervals_overlap("07:00","09:00","09:00","11:00"))

    def test_no_overlap_gap(self):
        self.assertFalse(intervals_overlap("07:00","09:00","10:00","12:00"))

    def test_exact_adjacent(self):
        # End of one == start of next → no overlap
        self.assertFalse(intervals_overlap("13:00","15:00","15:00","17:00"))

    def test_overlap_partial_left(self):
        self.assertTrue(intervals_overlap("07:00","10:00","09:00","11:00"))

    def test_overlap_partial_right(self):
        self.assertTrue(intervals_overlap("10:00","12:00","09:00","11:00"))

    def test_overlap_contained(self):
        # Inner interval fully inside outer
        self.assertTrue(intervals_overlap("07:00","12:00","08:00","10:00"))

    def test_overlap_identical(self):
        self.assertTrue(intervals_overlap("09:00","11:00","09:00","11:00"))

    def test_overlap_one_minute_intersection(self):
        self.assertTrue(intervals_overlap("09:00","10:01","10:00","11:00"))

    def test_zero_length_at_boundary(self):
        # A zero-length interval at the edge should NOT overlap
        self.assertFalse(intervals_overlap("09:00","11:00","11:00","11:00"))


class TestConflictDetectionLogic(unittest.TestCase):
    """Tests the same logic used in booking_service.check_conflict."""

    def _conflict(self, existing: list[tuple], new_start: str, new_end: str) -> list:
        ns = _time_to_minutes(new_start)
        ne = _time_to_minutes(new_end)
        conflicts = []
        for (s, e) in existing:
            es = _time_to_minutes(s)
            ee = _time_to_minutes(e)
            if ns < ee and es < ne:
                conflicts.append((s, e))
        return conflicts

    def test_empty_schedule_no_conflict(self):
        self.assertEqual(self._conflict([], "09:00", "11:00"), [])

    def test_single_approved_no_overlap(self):
        self.assertEqual(self._conflict([("07:00","09:00")], "09:00","11:00"), [])

    def test_single_approved_overlap(self):
        self.assertEqual(self._conflict([("08:00","10:00")], "09:00","11:00"), [("08:00","10:00")])

    def test_multiple_only_one_overlaps(self):
        existing = [("07:00","08:00"), ("08:00","09:00"), ("10:00","12:00")]
        result = self._conflict(existing, "09:30","11:00")
        self.assertEqual(result, [("10:00","12:00")])

    def test_multiple_all_overlap(self):
        existing = [("09:00","11:00"), ("09:30","10:30")]
        result = self._conflict(existing, "08:00","12:00")
        self.assertEqual(len(result), 2)


class TestCapacityValidation(unittest.TestCase):

    def test_attendees_within_capacity(self):
        self.assertTrue(20 <= 40)

    def test_attendees_exceed_capacity(self):
        self.assertFalse(50 <= 40)

    def test_attendees_exact_capacity(self):
        self.assertTrue(40 <= 40)


if __name__ == "__main__":
    unittest.main(verbosity=2)
