-- CampusSpaceOps Seed Data
-- Passwords are pbkdf2_hmac('sha256', b'password123', b'campsalt', 260000)
-- All demo users share the same password: password123
-- Hash: fdae1f7e5d7654e00e590af7c223ee783b9adf78cac45fac62beb8af1c1b9aa3

INSERT OR IGNORE INTO users (username, password_hash, role, full_name, email) VALUES
('admin',    'fdae1f7e5d7654e00e590af7c223ee783b9adf78cac45fac62beb8af1c1b9aa3', 'admin',   'System Admin',      'admin@campus.edu'),
('operator', 'fdae1f7e5d7654e00e590af7c223ee783b9adf78cac45fac62beb8af1c1b9aa3', 'admin',   'Room Operator',     'operator@campus.edu'),
('staff01',  'fdae1f7e5d7654e00e590af7c223ee783b9adf78cac45fac62beb8af1c1b9aa3', 'staff',   'Drs. Budi Santoso', 'budi@campus.edu'),
('mhs001',   'fdae1f7e5d7654e00e590af7c223ee783b9adf78cac45fac62beb8af1c1b9aa3', 'student', 'Andi Pratama',      'andi@student.edu'),
('mhs002',   'fdae1f7e5d7654e00e590af7c223ee783b9adf78cac45fac62beb8af1c1b9aa3', 'student', 'Sari Dewi',         'sari@student.edu'),
('mhs003',   'fdae1f7e5d7654e00e590af7c223ee783b9adf78cac45fac62beb8af1c1b9aa3', 'student', 'Rizky Aulia',       'rizky@student.edu');

INSERT OR IGNORE INTO rooms (name, capacity, location, type) VALUES
('R-101', 40,  'Gedung A Lt.1', 'lecture'),
('R-102', 40,  'Gedung A Lt.1', 'lecture'),
('R-201', 60,  'Gedung A Lt.2', 'lecture'),
('R-202', 60,  'Gedung A Lt.2', 'lecture'),
('R-301', 80,  'Gedung A Lt.3', 'lecture'),
('LAB-1', 30,  'Gedung B Lt.1', 'lab'),
('LAB-2', 30,  'Gedung B Lt.1', 'lab'),
('SEM-1', 20,  'Gedung C Lt.1', 'seminar'),
('SEM-2', 20,  'Gedung C Lt.1', 'seminar'),
('MTG-1', 12,  'Gedung D Lt.1', 'meeting');

INSERT OR IGNORE INTO schedules (room_id, day_of_week, start_time, end_time, label) VALUES
(1, 'Mon', '07:00', '09:00', 'IE2101 Pengantar TI'),
(1, 'Mon', '13:00', '15:00', 'IE3201 Riset Operasi'),
(1, 'Wed', '07:00', '09:00', 'IE2101 Pengantar TI'),
(2, 'Tue', '09:00', '11:00', 'IE4101 Manajemen Mutu'),
(2, 'Thu', '09:00', '11:00', 'IE4101 Manajemen Mutu'),
(3, 'Mon', '09:00', '11:00', 'IE3301 Simulasi'),
(3, 'Wed', '13:00', '15:00', 'IE3301 Simulasi'),
(4, 'Tue', '07:00', '09:00', 'IE2201 Statistika Industri'),
(5, 'Fri', '07:00', '11:00', 'IE4901 Seminar TA');

-- Historical bookings for analytics (dates in 2025-06)
INSERT OR IGNORE INTO bookings (user_id, room_id, date, start_time, end_time, purpose, attendees, status, reviewed_by, reviewed_at, submitted_at) VALUES
(4, 1, '2025-06-02', '09:00', '11:00', 'Rapat Panitia Ospek',        25, 'approved', 1, '2025-06-01 08:00', '2025-05-31 20:00'),
(5, 2, '2025-06-02', '13:00', '15:00', 'Diskusi Kelompok Tugas',     10, 'approved', 1, '2025-06-01 09:00', '2025-05-31 21:00'),
(6, 3, '2025-06-03', '09:00', '11:00', 'Presentasi Proyek Akhir',    35, 'approved', 2, '2025-06-02 07:00', '2025-06-01 15:00'),
(4, 1, '2025-06-03', '13:00', '15:00', 'Latihan Debat',              20, 'approved', 2, '2025-06-02 08:00', '2025-06-01 16:00'),
(5, 6, '2025-06-04', '07:00', '09:00', 'Praktikum Komputer',         28, 'approved', 1, '2025-06-03 07:00', '2025-06-02 18:00'),
(6, 4, '2025-06-04', '13:00', '15:00', 'Rapat Himpunan',             15, 'approved', 2, '2025-06-03 08:00', '2025-06-02 19:00'),
(4, 2, '2025-06-05', '09:00', '11:00', 'Workshop Desain Produk',     30, 'approved', 1, '2025-06-04 07:00', '2025-06-03 14:00'),
(5, 5, '2025-06-05', '13:00', '17:00', 'Seminar Nasional',           75, 'approved', 2, '2025-06-04 09:00', '2025-06-03 15:00'),
(6, 8, '2025-06-06', '09:00', '11:00', 'Coaching UKM',               15, 'approved', 1, '2025-06-05 07:00', '2025-06-04 20:00'),
(4, 1, '2025-06-09', '09:00', '11:00', 'Rapat HMTI',                 25, 'approved', 1, '2025-06-08 08:00', '2025-06-07 18:00'),
(5, 3, '2025-06-09', '13:00', '15:00', 'Studium Generale',           55, 'approved', 2, '2025-06-08 09:00', '2025-06-07 19:00'),
(6, 6, '2025-06-10', '07:00', '09:00', 'Praktikum Pemrograman',      29, 'approved', 1, '2025-06-09 07:00', '2025-06-08 14:00'),
(4, 2, '2025-06-10', '13:00', '15:00', 'Kelas Tambahan IE3201',      35, 'rejected', 2, '2025-06-09 08:00', '2025-06-08 15:00'),
(5, 1, '2025-06-11', '09:00', '11:00', 'Focus Group Discussion',     18, 'approved', 1, '2025-06-10 07:00', '2025-06-09 20:00'),
(6, 4, '2025-06-11', '13:00', '15:00', 'Rapat Koordinasi',           12, 'approved', 2, '2025-06-10 08:00', '2025-06-09 21:00'),
(4, 3, '2025-06-12', '09:00', '11:00', 'Presentasi KP',              45, 'approved', 1, '2025-06-11 07:00', '2025-06-10 16:00'),
(5, 5, '2025-06-12', '13:00', '17:00', 'Wisuda Akbar',               78, 'approved', 2, '2025-06-11 09:00', '2025-06-10 17:00'),
(6, 7, '2025-06-13', '07:00', '11:00', 'Pelatihan Data Analytics',   27, 'approved', 1, '2025-06-12 07:00', '2025-06-11 14:00'),
(4, 9, '2025-06-13', '13:00', '15:00', 'Diskusi Tesis',              18, 'rejected', 2, '2025-06-12 09:00', '2025-06-11 15:00'),
(5, 2, '2025-06-16', '09:00', '11:00', 'Kelas Pengganti',            38, 'approved', 1, '2025-06-15 08:00', '2025-06-14 18:00'),
(6, 1, '2025-06-16', '13:00', '15:00', 'Rapat Panitia Wisuda',       22, 'approved', 2, '2025-06-15 09:00', '2025-06-14 19:00'),
(4, 6, '2025-06-17', '07:00', '09:00', 'Praktikum ERP',              30, 'pending',  NULL, NULL, '2025-06-16 20:00'),
(5, 3, '2025-06-17', '13:00', '15:00', 'Seminar Karir',              52, 'pending',  NULL, NULL, '2025-06-16 21:00'),
(6, 1, '2025-06-18', '09:00', '11:00', 'Kuliah Umum',                38, 'pending',  NULL, NULL, '2025-06-17 08:00');
