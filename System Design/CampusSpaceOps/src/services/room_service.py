import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import fetchall, fetchone, execute


def get_all_rooms(active_only: bool = True) -> list:
    sql = "SELECT * FROM rooms"
    if active_only:
        sql += " WHERE is_active = 1"
    sql += " ORDER BY name"
    return [dict(r) for r in fetchall(sql)]


def get_room(room_id: int) -> dict | None:
    row = fetchone("SELECT * FROM rooms WHERE id = ?", (room_id,))
    return dict(row) if row else None


def create_room(name: str, capacity: int, location: str, room_type: str) -> int:
    return execute(
        "INSERT INTO rooms (name, capacity, location, type) VALUES (?,?,?,?)",
        (name, capacity, location, room_type),
    )


def update_room(room_id: int, name: str, capacity: int, location: str, room_type: str) -> None:
    execute(
        "UPDATE rooms SET name=?, capacity=?, location=?, type=? WHERE id=?",
        (name, capacity, location, room_type, room_id),
    )


def deactivate_room(room_id: int) -> None:
    execute("UPDATE rooms SET is_active = 0 WHERE id = ?", (room_id,))


def get_schedules(room_id: int) -> list:
    return [dict(r) for r in fetchall(
        "SELECT * FROM schedules WHERE room_id = ? ORDER BY day_of_week, start_time",
        (room_id,),
    )]
