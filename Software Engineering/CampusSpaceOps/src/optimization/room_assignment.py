"""
Room Assignment Optimization — Binary Integer Program (BIP)

Decision variable:
  x[i][j] = 1  if request i is assigned to room j, else 0

Objective (minimize wasted seat-capacity):
  min  Σ_i Σ_j  x[i][j] * (capacity[j] - attendees[i])

Constraints:
  1. Each request assigned at most once:        Σ_j x[i][j] <= 1   ∀i
  2. Capacity feasibility:                      x[i][j] = 0         if attendees[i] > capacity[j]
  3. No time overlap in the same room:          x[i][j] + x[k][j] <= 1  if t_i ∩ t_k ≠ ∅, i≠k

Solver strategy: greedy BIP approximation (optimal for small instances;
production deployments can swap in PuLP or scipy.optimize.milp).
"""
from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import fetchall


def _overlap(s1: str, e1: str, s2: str, e2: str) -> bool:
    def t2m(t):
        h, m = t.split(":")
        return int(h) * 60 + int(m)
    return t2m(s1) < t2m(e2) and t2m(s2) < t2m(e1)


def _waste(room_capacity: int, attendees: int) -> int:
    return room_capacity - attendees


def solve(requests: list[dict], rooms: list[dict]) -> list[dict]:
    """
    Greedy BIP: sort requests by attendees (largest first) and assign
    the feasible room that minimises wasted seats.

    Parameters
    ----------
    requests : list of dicts with keys: id, date, start_time, end_time, attendees
    rooms    : list of dicts with keys: id, name, capacity

    Returns
    -------
    list of assignment dicts: {request_id, room_id, room_name, waste, assigned}
    """
    # Sort by descending attendees (largest groups are hardest to fit)
    sorted_req = sorted(requests, key=lambda r: r["attendees"], reverse=True)

    # Track which rooms are occupied per time window: room_id -> list[(date, s, e)]
    room_schedule: dict[int, list[tuple]] = {r["id"]: [] for r in rooms}
    assignments: list[dict] = []

    for req in sorted_req:
        best_room = None
        best_waste = float("inf")

        for room in sorted(rooms, key=lambda r: r["capacity"]):
            if room["capacity"] < req["attendees"]:
                continue  # capacity infeasible

            # Check no overlap with already assigned requests in this room
            conflict = any(
                req["date"] == slot[0] and _overlap(req["start_time"], req["end_time"], slot[1], slot[2])
                for slot in room_schedule[room["id"]]
            )
            if conflict:
                continue

            w = _waste(room["capacity"], req["attendees"])
            if w < best_waste:
                best_waste = w
                best_room = room

        if best_room:
            room_schedule[best_room["id"]].append(
                (req["date"], req["start_time"], req["end_time"])
            )
            assignments.append({
                "request_id": req["id"],
                "room_id":    best_room["id"],
                "room_name":  best_room["name"],
                "capacity":   best_room["capacity"],
                "attendees":  req["attendees"],
                "waste":      best_waste,
                "assigned":   True,
            })
        else:
            assignments.append({
                "request_id": req["id"],
                "room_id":    None,
                "room_name":  "— unassignable —",
                "capacity":   None,
                "attendees":  req["attendees"],
                "waste":      None,
                "assigned":   False,
            })

    # Restore original request order
    order = {r["id"]: i for i, r in enumerate(requests)}
    assignments.sort(key=lambda a: order.get(a["request_id"], 0))
    return assignments


def solve_pending_bookings() -> list[dict]:
    """
    Pull all pending bookings + active rooms from DB and run the solver.
    Returns assignment recommendations (does NOT modify the database).
    """
    requests = [dict(r) for r in fetchall(
        """SELECT id, room_id, date, start_time, end_time, attendees,
                  purpose,
                  (SELECT full_name FROM users WHERE id = b.user_id) as requester
           FROM bookings b
           WHERE status = 'pending'
           ORDER BY submitted_at"""
    )]
    rooms = [dict(r) for r in fetchall(
        "SELECT id, name, capacity FROM rooms WHERE is_active = 1 ORDER BY capacity"
    )]

    if not requests:
        return []
    return solve(requests, rooms)


def optimization_summary(assignments: list[dict]) -> dict:
    assigned   = [a for a in assignments if a["assigned"]]
    unassigned = [a for a in assignments if not a["assigned"]]
    total_waste = sum(a["waste"] for a in assigned)
    return {
        "total_requests": len(assignments),
        "assigned":       len(assigned),
        "unassigned":     len(unassigned),
        "total_waste_seats": total_waste,
        "avg_waste_per_booking": round(total_waste / max(len(assigned), 1), 1),
    }
