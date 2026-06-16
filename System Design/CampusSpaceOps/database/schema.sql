-- CampusSpaceOps Database Schema
-- Normalized relational design for campus room operations

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT    NOT NULL UNIQUE,
    password_hash TEXT  NOT NULL,
    role        TEXT    NOT NULL CHECK(role IN ('admin', 'staff', 'student')),
    full_name   TEXT    NOT NULL,
    email       TEXT,
    created_at  TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS rooms (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    capacity    INTEGER NOT NULL CHECK(capacity > 0),
    location    TEXT    NOT NULL,
    type        TEXT    NOT NULL CHECK(type IN ('lecture', 'lab', 'seminar', 'meeting')),
    is_active   INTEGER DEFAULT 1,
    created_at  TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS schedules (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id     INTEGER NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    day_of_week TEXT    NOT NULL CHECK(day_of_week IN ('Mon','Tue','Wed','Thu','Fri','Sat','Sun')),
    start_time  TEXT    NOT NULL,
    end_time    TEXT    NOT NULL,
    label       TEXT,
    created_at  TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS bookings (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL REFERENCES users(id),
    room_id       INTEGER NOT NULL REFERENCES rooms(id),
    date          TEXT    NOT NULL,
    start_time    TEXT    NOT NULL,
    end_time      TEXT    NOT NULL,
    purpose       TEXT    NOT NULL,
    attendees     INTEGER NOT NULL CHECK(attendees > 0),
    status        TEXT    NOT NULL DEFAULT 'pending'
                          CHECK(status IN ('pending','approved','rejected','cancelled')),
    reviewed_by   INTEGER REFERENCES users(id),
    reviewed_at   TEXT,
    reject_reason TEXT,
    submitted_at  TEXT    DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_bookings_room_date ON bookings(room_id, date);
CREATE INDEX IF NOT EXISTS idx_bookings_user      ON bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_status    ON bookings(status);
CREATE INDEX IF NOT EXISTS idx_schedules_room     ON schedules(room_id);
