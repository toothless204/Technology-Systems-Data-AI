"""
Descriptive utilization analytics for CampusSpaceOps.

KPIs:
  - Utilization rate per room  (booked hours / available hours)
  - Peak hour heatmap          (day-of-week × hour)
  - Rejection rate             (rejected / total submitted)
  - Approval lead time         (avg hours from submission to review)
  - Idle capacity              (available seats × idle hours)
"""
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import fetchall

OPERATIONAL_HOURS_PER_DAY = 12   # 07:00 – 19:00
OPERATIONAL_DAYS_PER_WEEK = 5    # Mon–Fri


def _duration_hours(start: str, end: str) -> float:
    def t2m(t):
        h, m = t.split(":")
        return int(h) * 60 + int(m)
    return max(0.0, (t2m(end) - t2m(start)) / 60.0)


# ---- per-room utilization ------------------------------------------------

def room_utilization(period_days: int = 30) -> list[dict]:
    """
    Returns list of dicts: room_name, capacity, booked_hours, util_rate,
    idle_capacity_seat_hours, avg_attendees.
    """
    rows = fetchall(
        """SELECT r.name as room_name, r.capacity,
                  b.start_time, b.end_time, b.attendees
           FROM bookings b
           JOIN rooms r ON b.room_id = r.id
           WHERE b.status = 'approved'
             AND b.date >= date('now', ? || ' days')""",
        (f"-{period_days}",),
    )

    stats: dict[str, dict] = {}
    for row in rows:
        name = row["room_name"]
        if name not in stats:
            stats[name] = {
                "room_name": name,
                "capacity": row["capacity"],
                "booked_hours": 0.0,
                "total_attendees": 0,
                "booking_count": 0,
            }
        dur = _duration_hours(row["start_time"], row["end_time"])
        stats[name]["booked_hours"]     += dur
        stats[name]["total_attendees"]  += row["attendees"]
        stats[name]["booking_count"]    += 1

    available_hours = period_days * (OPERATIONAL_DAYS_PER_WEEK / 7) * OPERATIONAL_HOURS_PER_DAY
    available_hours = max(available_hours, 1.0)

    result = []
    for s in stats.values():
        bh = s["booked_hours"]
        util = min(bh / available_hours, 1.0)
        idle_seat_h = (available_hours - bh) * s["capacity"]
        avg_att = s["total_attendees"] / max(s["booking_count"], 1)
        result.append({
            "room_name":              s["room_name"],
            "capacity":               s["capacity"],
            "booked_hours":           round(bh, 1),
            "available_hours":        round(available_hours, 1),
            "utilization_rate":       round(util * 100, 1),
            "idle_capacity_seat_hrs": round(idle_seat_h, 1),
            "avg_attendees":          round(avg_att, 1),
            "booking_count":          s["booking_count"],
        })

    result.sort(key=lambda x: x["utilization_rate"], reverse=True)
    return result


# ---- peak hour heatmap ---------------------------------------------------

def peak_hour_heatmap() -> dict:
    """
    Returns {(day_abbr, hour_int): booking_count} for approved bookings.
    """
    rows = fetchall(
        """SELECT strftime('%w', date) as dow,
                  start_time, end_time
           FROM bookings
           WHERE status = 'approved'"""
    )
    DOW = {0: "Sun", 1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat"}
    heat: dict = defaultdict(int)
    for row in rows:
        dow = DOW[int(row["dow"])]
        sh = int(row["start_time"].split(":")[0])
        eh = int(row["end_time"].split(":")[0])
        for h in range(sh, eh):
            heat[(dow, h)] += 1
    return dict(heat)


def peak_hours_summary() -> list[dict]:
    """Top 10 busiest (day, hour) slots."""
    heat = peak_hour_heatmap()
    ranked = sorted(heat.items(), key=lambda x: x[1], reverse=True)[:10]
    return [{"day": k[0], "hour": f"{k[1]:02d}:00", "count": v} for k, v in ranked]


# ---- rejection rate ------------------------------------------------------

def rejection_stats() -> dict:
    rows = fetchall(
        """SELECT status, COUNT(*) as cnt FROM bookings GROUP BY status"""
    )
    counts = {r["status"]: r["cnt"] for r in rows}
    total = sum(counts.values())
    rejected = counts.get("rejected", 0)
    pending  = counts.get("pending", 0)
    approved = counts.get("approved", 0)
    return {
        "total":           total,
        "approved":        approved,
        "rejected":        rejected,
        "pending":         pending,
        "cancelled":       counts.get("cancelled", 0),
        "rejection_rate":  round(rejected / max(total, 1) * 100, 1),
        "approval_rate":   round(approved / max(total, 1) * 100, 1),
    }


# ---- approval lead time --------------------------------------------------

def approval_lead_time() -> dict:
    """Average hours from submission to review decision."""
    rows = fetchall(
        """SELECT submitted_at, reviewed_at
           FROM bookings
           WHERE status IN ('approved','rejected')
             AND reviewed_at IS NOT NULL"""
    )
    if not rows:
        return {"avg_lead_hours": 0.0, "min_lead_hours": 0.0, "max_lead_hours": 0.0}

    from datetime import datetime
    deltas = []
    for row in rows:
        try:
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
                try:
                    s = datetime.strptime(row["submitted_at"][:16], fmt[:len("%Y-%m-%d %H:%M")])
                    e = datetime.strptime(row["reviewed_at"][:16],  fmt[:len("%Y-%m-%d %H:%M")])
                    deltas.append((e - s).total_seconds() / 3600)
                    break
                except ValueError:
                    continue
        except Exception:
            pass

    if not deltas:
        return {"avg_lead_hours": 0.0, "min_lead_hours": 0.0, "max_lead_hours": 0.0}
    return {
        "avg_lead_hours": round(sum(deltas) / len(deltas), 1),
        "min_lead_hours": round(min(deltas), 1),
        "max_lead_hours": round(max(deltas), 1),
    }


def full_dashboard() -> dict:
    return {
        "utilization":    room_utilization(),
        "peak_hours":     peak_hours_summary(),
        "rejection_stats": rejection_stats(),
        "lead_time":      approval_lead_time(),
    }
