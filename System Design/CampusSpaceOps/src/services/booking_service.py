"""
Booking service — includes interval-overlap conflict detection.

Conflict rule (half-open intervals):
  Two bookings [s1, e1) and [s2, e2) overlap iff  s1 < e2  AND  s2 < e1
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import fetchall, fetchone, execute


def _time_to_minutes(t: str) -> int:
    """'HH:MM' -> minutes since midnight."""
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def check_conflict(room_id: int, date: str, start_time: str, end_time: str,
                   exclude_booking_id: int | None = None) -> list:
    """
    Returns list of conflicting approved/pending bookings.
    Uses interval-overlap logic: conflict iff start1 < end2 AND start2 < end1.
    """
    s1 = _time_to_minutes(start_time)
    e1 = _time_to_minutes(end_time)

    rows = fetchall(
        """SELECT b.*, u.full_name as requester_name
           FROM bookings b
           JOIN users u ON b.user_id = u.id
           WHERE b.room_id = ?
             AND b.date = ?
             AND b.status IN ('approved', 'pending')""",
        (room_id, date),
    )

    conflicts = []
    for row in rows:
        if exclude_booking_id and row["id"] == exclude_booking_id:
            continue
        s2 = _time_to_minutes(row["start_time"])
        e2 = _time_to_minutes(row["end_time"])
        if s1 < e2 and s2 < e1:
            conflicts.append(dict(row))
    return conflicts


def submit_booking(user_id: int, room_id: int, date: str,
                   start_time: str, end_time: str,
                   purpose: str, attendees: int) -> tuple[int | None, str]:
    """
    Returns (booking_id, error_message).
    booking_id is None on failure.
    """
    conflicts = check_conflict(room_id, date, start_time, end_time)
    if conflicts:
        c = conflicts[0]
        return None, (f"Time conflict with existing booking by {c['requester_name']} "
                      f"({c['start_time']}–{c['end_time']}, status={c['status']})")

    room = fetchone("SELECT capacity FROM rooms WHERE id = ?", (room_id,))
    if room and attendees > room["capacity"]:
        return None, (f"Attendees ({attendees}) exceed room capacity ({room['capacity']})")

    booking_id = execute(
        """INSERT INTO bookings
           (user_id, room_id, date, start_time, end_time, purpose, attendees, status)
           VALUES (?,?,?,?,?,?,?,'pending')""",
        (user_id, room_id, date, start_time, end_time, purpose, attendees),
    )
    return booking_id, ""


def approve_booking(booking_id: int, admin_id: int) -> str:
    booking = fetchone("SELECT * FROM bookings WHERE id = ?", (booking_id,))
    if not booking:
        return "Booking not found."
    if booking["status"] != "pending":
        return f"Cannot approve: booking is already '{booking['status']}'."

    # Re-check conflict (another booking may have been approved since submission)
    conflicts = check_conflict(
        booking["room_id"], booking["date"],
        booking["start_time"], booking["end_time"],
        exclude_booking_id=booking_id,
    )
    if conflicts:
        c = conflicts[0]
        execute(
            "UPDATE bookings SET status='rejected', reviewed_by=?, reviewed_at=datetime('now'), "
            "reject_reason=? WHERE id=?",
            (admin_id, f"Auto-rejected: conflict with booking #{c['id']}", booking_id),
        )
        return f"Auto-rejected due to conflict with booking #{c['id']}."

    execute(
        "UPDATE bookings SET status='approved', reviewed_by=?, reviewed_at=datetime('now') WHERE id=?",
        (admin_id, booking_id),
    )
    return "Booking approved."


def reject_booking(booking_id: int, admin_id: int, reason: str = "") -> str:
    booking = fetchone("SELECT * FROM bookings WHERE id = ?", (booking_id,))
    if not booking:
        return "Booking not found."
    if booking["status"] != "pending":
        return f"Cannot reject: booking is already '{booking['status']}'."
    execute(
        "UPDATE bookings SET status='rejected', reviewed_by=?, reviewed_at=datetime('now'), "
        "reject_reason=? WHERE id=?",
        (admin_id, reason, booking_id),
    )
    return "Booking rejected."


def cancel_booking(booking_id: int, user_id: int) -> str:
    booking = fetchone("SELECT * FROM bookings WHERE id = ? AND user_id = ?", (booking_id, user_id))
    if not booking:
        return "Booking not found or not yours."
    if booking["status"] not in ("pending",):
        return f"Cannot cancel: booking is '{booking['status']}'."
    execute("UPDATE bookings SET status='cancelled' WHERE id=?", (booking_id,))
    return "Booking cancelled."


def get_all_bookings(status_filter: str | None = None) -> list:
    sql = """SELECT b.*, u.full_name as requester_name, u.username,
                    r.name as room_name, r.capacity as room_capacity
             FROM bookings b
             JOIN users u ON b.user_id = u.id
             JOIN rooms r ON b.room_id = r.id"""
    params: tuple = ()
    if status_filter:
        sql += " WHERE b.status = ?"
        params = (status_filter,)
    sql += " ORDER BY b.submitted_at DESC"
    return [dict(r) for r in fetchall(sql, params)]


def get_user_bookings(user_id: int) -> list:
    return [dict(r) for r in fetchall(
        """SELECT b.*, r.name as room_name, r.capacity as room_capacity
           FROM bookings b
           JOIN rooms r ON b.room_id = r.id
           WHERE b.user_id = ?
           ORDER BY b.submitted_at DESC""",
        (user_id,),
    )]
