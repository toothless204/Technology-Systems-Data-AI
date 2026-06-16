"""
Integration tests for booking workflow using an in-memory SQLite database.
"""
import sys
import os
import sqlite3
import unittest
import tempfile

# Patch DB_PATH to an in-memory temp file before importing anything
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import config as _cfg
_cfg.DB_PATH = _tmp.name

from database.db import initialize_db, get_connection
from services.auth_service import create_user, authenticate
from services.room_service import create_room, get_all_rooms
from services.booking_service import (
    submit_booking, approve_booking, reject_booking,
    cancel_booking, get_all_bookings, check_conflict,
)


class TestBookingWorkflow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        initialize_db(seed=False)
        # Create test users
        cls.admin_id  = create_user("testadmin", "adminpass", "admin",  "Test Admin")
        cls.user1_id  = create_user("testuser1", "pass1",    "student","User One")
        cls.user2_id  = create_user("testuser2", "pass2",    "student","User Two")
        # Create test rooms
        cls.room_sm   = create_room("R-TEST-SM", 20, "Block A", "seminar")
        cls.room_lg   = create_room("R-TEST-LG", 80, "Block B", "lecture")

    def test_01_authenticate_success(self):
        user = authenticate("testadmin", "adminpass")
        self.assertIsNotNone(user)
        self.assertEqual(user["role"], "admin")

    def test_02_authenticate_wrong_password(self):
        user = authenticate("testadmin", "wrong")
        self.assertIsNone(user)

    def test_03_submit_booking_success(self):
        bid, err = submit_booking(
            self.user1_id, self.room_sm,
            "2026-07-01", "09:00", "11:00", "Team meeting", 15,
        )
        self.assertIsNotNone(bid, f"Submission failed: {err}")
        self.assertEqual(err, "")

    def test_04_submit_booking_conflict(self):
        # Submit a second booking that overlaps with the first
        bid, err = submit_booking(
            self.user2_id, self.room_sm,
            "2026-07-01", "10:00", "12:00", "Overlapping event", 10,
        )
        self.assertIsNone(bid, "Should have detected conflict")
        self.assertIn("conflict", err.lower())

    def test_05_submit_booking_capacity_exceeded(self):
        bid, err = submit_booking(
            self.user1_id, self.room_sm,
            "2026-07-02", "09:00", "11:00", "Too many people", 50,
        )
        self.assertIsNone(bid)
        self.assertIn("capacity", err.lower())

    def test_06_submit_adjacent_no_conflict(self):
        # 11:00–13:00 is adjacent to 09:00–11:00, should succeed
        bid, err = submit_booking(
            self.user2_id, self.room_sm,
            "2026-07-01", "11:00", "13:00", "Right after", 10,
        )
        self.assertIsNotNone(bid, f"Adjacent booking failed: {err}")

    def test_07_approve_booking(self):
        bid, _ = submit_booking(
            self.user1_id, self.room_lg,
            "2026-07-03", "09:00", "11:00", "Approval test", 30,
        )
        msg = approve_booking(bid, self.admin_id)
        self.assertIn("approved", msg.lower())
        bookings = get_all_bookings("approved")
        ids = [b["id"] for b in bookings]
        self.assertIn(bid, ids)

    def test_08_approve_already_approved_fails(self):
        bid, _ = submit_booking(
            self.user1_id, self.room_lg,
            "2026-07-04", "09:00", "11:00", "Double approve test", 30,
        )
        approve_booking(bid, self.admin_id)
        msg = approve_booking(bid, self.admin_id)
        self.assertIn("already", msg.lower())  # should say "already 'approved'"

    def test_09_reject_booking(self):
        bid, _ = submit_booking(
            self.user1_id, self.room_sm,
            "2026-07-05", "09:00", "11:00", "Reject test", 10,
        )
        msg = reject_booking(bid, self.admin_id, "Venue unavailable")
        self.assertIn("rejected", msg.lower())

    def test_10_cancel_own_booking(self):
        bid, _ = submit_booking(
            self.user1_id, self.room_sm,
            "2026-07-06", "09:00", "11:00", "Cancel test", 5,
        )
        msg = cancel_booking(bid, self.user1_id)
        self.assertIn("cancelled", msg.lower())

    def test_11_cancel_others_booking_denied(self):
        bid, _ = submit_booking(
            self.user1_id, self.room_sm,
            "2026-07-07", "09:00", "11:00", "Others cancel test", 5,
        )
        msg = cancel_booking(bid, self.user2_id)
        self.assertIn("not found", msg.lower())

    def test_12_check_conflict_returns_empty_for_free_slot(self):
        conflicts = check_conflict(self.room_lg, "2026-08-01", "07:00", "09:00")
        self.assertEqual(conflicts, [])

    @classmethod
    def tearDownClass(cls):
        try:
            os.unlink(_tmp.name)
        except Exception:
            pass


if __name__ == "__main__":
    unittest.main(verbosity=2)
