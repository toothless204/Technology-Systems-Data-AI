CREATE TABLE IF NOT EXISTS Users (
    ID_User INTEGER PRIMARY KEY AUTOINCREMENT,
    Username TEXT UNIQUE NOT NULL,
    Password TEXT NOT NULL,
    Role TEXT NOT NULL,
    Email TEXT
);

CREATE TABLE IF NOT EXISTS Ruangan (
    ID_Ruangan INTEGER PRIMARY KEY AUTOINCREMENT,
    Nama_Ruangan TEXT NOT NULL,
    Kapasitas INTEGER,
    Lokasi TEXT,
    Fasilitas TEXT
);

CREATE TABLE IF NOT EXISTS Jadwal (
    ID_Jadwal INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_Ruangan INTEGER NOT NULL,
    Waktu_Mulai DATETIME NOT NULL,
    Waktu_Selesai DATETIME NOT NULL,
    Status TEXT DEFAULT 'Tersedia',
    Pemesan TEXT,
    Status_Approval TEXT DEFAULT 'Pending',
    FOREIGN KEY(ID_Ruangan) REFERENCES Ruangan(ID_Ruangan)
);

INSERT OR IGNORE INTO Users (Username, Password, Role, Email) VALUES
('admin', 'admin123', 'Operator', 'admin@test.com'),
('mahasiswa1', 'pass123', 'Mahasiswa', 'mhs@test.com'),
('dosen1', 'pass123', 'Dosen', 'dosen@test.com');

INSERT OR IGNORE INTO Ruangan (Nama_Ruangan, Kapasitas, Lokasi, Fasilitas) VALUES
('Ruang Kelas A', 50, 'Gedung 1', 'Proyektor, AC'),
('Ruang Kelas B', 40, 'Gedung 1', 'Proyektor, AC'),
('Lab Komputer', 30, 'Gedung 2', 'Komputer, AC'),
('Ruang Rapat', 20, 'Gedung 3', 'Meja Panjang, AC');
