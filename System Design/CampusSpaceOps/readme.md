# CampusSpaceOps
### Room Booking, Utilization Analytics, and Scheduling Optimization System

CampusSpaceOps is a decision-support system for managing campus room operations. The project combines room booking workflow, relational database design, role-based access control, schedule conflict detection, utilization analytics, and room assignment optimization.

---

## Problem Statement

Universities face limited rooms, fragmented booking processes, schedule conflicts, and weak visibility into actual space utilization. CampusSpaceOps addresses this by turning room-booking transactions into operational intelligence.

**Key decisions supported:**
- Which room should be assigned to each request?
- Which rooms are over- or underutilized?
- Which time slots generate the most conflicts?
- Should the campus add rooms or change policy?
- How much risk exists during peak demand?

---

## Technical Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Database | SQLite (via `sqlite3` stdlib) |
| GUI | Tkinter (dark-themed, tabbed interface) |
| Password security | `hashlib.pbkdf2_hmac` SHA-256, 260 000 iterations |
| Optimization | Greedy BIP (swap-in-ready for PuLP / scipy.milp) |
| Tests | `unittest` (12 integration + 9 unit tests) |

---

## Repository Structure

```
CampusSpaceOps/
├── database/
│   └── schema.sql              # Normalized DDL: users, rooms, schedules, bookings
├── data/
│   └── seed/seed_data.sql      # Reproducible demo data (6 users, 10 rooms, 24 bookings)
├── src/
│   ├── app.py                  # Entry point
│   ├── config.py               # Paths, constants, hash parameters
│   ├── database/db.py          # Connection factory, generic helpers
│   ├── services/
│   │   ├── auth_service.py     # PBKDF2 hashing, authenticate, create_user
│   │   ├── room_service.py     # CRUD for rooms and schedules
│   │   ├── booking_service.py  # Submit, approve, reject, cancel + conflict detection
│   │   └── analytics_service.py# Utilization, peak hours, rejection rate, lead time
│   ├── optimization/
│   │   └── room_assignment.py  # Greedy BIP solver for room assignment
│   └── ui/
│       ├── theme.py            # Dark-theme palette, ttk style configuration
│       ├── login_window.py     # Authentication screen
│       ├── admin_window.py     # Admin: bookings, rooms, users, analytics, optimization
│       └── user_window.py      # User: my bookings + new booking form
└── tests/
    ├── test_conflict.py        # Unit tests for interval-overlap logic (9 cases)
    └── test_booking.py         # Integration tests for full booking workflow (12 cases)
```

---

## Quick Start

```bash
# Clone and run — no pip installs required (stdlib only)
git clone <repo>
cd CampusSpaceOps
python src/app.py
```

The application seeds the database automatically on first run.

**Demo credentials:**

| Username | Password | Role |
|---|---|---|
| `admin` | `password123` | Admin |
| `operator` | `password123` | Admin |
| `staff01` | `password123` | Staff |
| `mhs001` | `password123` | Student |
| `mhs002` | `password123` | Student |

---

## Run Tests

```bash
python -m pytest tests/ -v
# or
python -m unittest discover tests/ -v
```

---

## Methodology

| # | Method | Operational Question |
|---|---|---|
| M1 | Relational Database Design | What data structure manages rooms, users, schedules, and requests? |
| M2 | Interval-Overlap Conflict Detection | Does a new request conflict with existing approved schedules? |
| M3 | Descriptive Utilization Analytics | Which rooms and time slots are over- or underused? |
| M4 | Demand Pattern Analysis | When does demand peak by day and hour? |
| M5 | BIP Room Assignment Optimization | Which assignment minimizes wasted capacity? |
| M6 | Rejection & Lead Time Monitoring | What is the system's operational throughput quality? |

### Conflict Detection — Interval Overlap Rule

```
Two bookings [s1, e1) and [s2, e2) conflict  iff  s1 < e2  AND  s2 < e1
```

### Optimization Model — Binary Integer Program

**Decision variable:**  `x[i][j]` = 1 if request `i` is assigned to room `j`, else 0

**Objective:** minimize total wasted seat-capacity
```
min  Σ_i Σ_j  x[i][j] * (capacity[j] - attendees[i])
```

**Constraints:**
1. Each request assigned at most once: `Σ_j x[i][j] ≤ 1  ∀i`
2. Capacity feasibility: `x[i][j] = 0  if attendees[i] > capacity[j]`
3. No time overlap in the same room: `x[i][j] + x[k][j] ≤ 1  if t_i ∩ t_k ≠ ∅`

---

## Analytics KPIs

| KPI | Formula |
|---|---|
| Utilization Rate | Booked hours / Available hours × 100% |
| Idle Capacity | (Available hours − Booked hours) × Room capacity |
| Rejection Rate | Rejected bookings / Total submitted × 100% |
| Approval Lead Time | Average hours from submission to admin review |

---

## Domain Coverage

| Domain | Capabilities Demonstrated |
|---|---|
| Technology | Python · SQLite · Tkinter · RBAC · Password hashing · Modular architecture |
| Mathematics | BIP optimization · Interval-overlap logic · Utilization rate computation |
| Economics | KPI dashboard · Idle capacity cost · Capacity planning evidence |

---

*CampusSpaceOps — ITB Industrial Engineering Portfolio Project · 2026*
