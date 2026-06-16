import sqlite3
from datetime import datetime

class DatabaseHandler:
    def __init__(self, db_name="room_management.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize database with schema"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Create Users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Users (
                        ID_User INTEGER PRIMARY KEY AUTOINCREMENT,
                        Username TEXT UNIQUE NOT NULL,
                        Password TEXT NOT NULL,
                        Role TEXT NOT NULL,
                        Email TEXT
                    )
                """)
                
                # Create Ruangan table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Ruangan (
                        ID_Ruangan INTEGER PRIMARY KEY AUTOINCREMENT,
                        Nama_Ruangan TEXT NOT NULL,
                        Kapasitas INTEGER,
                        Lokasi TEXT,
                        Fasilitas TEXT
                    )
                """)
                
                # Create Jadwal table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Jadwal (
                        ID_Jadwal INTEGER PRIMARY KEY AUTOINCREMENT,
                        ID_Ruangan INTEGER NOT NULL,
                        Waktu_Mulai DATETIME NOT NULL,
                        Waktu_Selesai DATETIME NOT NULL,
                        Status TEXT DEFAULT 'Tersedia',
                        Pemesan TEXT,
                        Status_Approval TEXT DEFAULT 'Pending',
                        FOREIGN KEY(ID_Ruangan) REFERENCES Ruangan(ID_Ruangan)
                    )
                """)
                
                conn.commit()
                self.insert_default_data()
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    def insert_default_data(self):
        """Insert default data"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Insert default users
                cursor.execute("SELECT COUNT(*) FROM Users")
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO Users (Username, Password, Role, Email) VALUES
                        (?, ?, ?, ?), (?, ?, ?, ?), (?, ?, ?, ?)
                    """, (
                        'admin', 'admin123', 'Operator', 'admin@test.com',
                        'mahasiswa1', 'pass123', 'Mahasiswa', 'mhs@test.com',
                        'dosen1', 'pass123', 'Dosen', 'dosen@test.com'
                    ))
                
                # Insert default rooms
                cursor.execute("SELECT COUNT(*) FROM Ruangan")
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO Ruangan (Nama_Ruangan, Kapasitas, Lokasi, Fasilitas) VALUES
                        (?, ?, ?, ?), (?, ?, ?, ?), (?, ?, ?, ?), (?, ?, ?, ?)
                    """, (
                        'Ruang Kelas A', 50, 'Gedung 1', 'Proyektor, AC',
                        'Ruang Kelas B', 40, 'Gedung 1', 'Proyektor, AC',
                        'Lab Komputer', 30, 'Gedung 2', 'Komputer, AC',
                        'Ruang Rapat', 20, 'Gedung 3', 'Meja Panjang, AC'
                    ))
                
                conn.commit()
        except Exception as e:
            print(f"Insert default data error: {e}")
    
    def get_user(self, username):
        """Get user by username"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Users WHERE Username = ?", (username,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Get user error: {e}")
            return None
    
    def get_all_rooms(self):
        """Get all rooms"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Ruangan")
                return cursor.fetchall()
        except Exception as e:
            print(f"Get all rooms error: {e}")
            return []
    
    def get_schedules_by_room(self, room_id):
        """Get schedules for a room"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM Jadwal WHERE ID_Ruangan = ? ORDER BY Waktu_Mulai
                """, (room_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Get schedules error: {e}")
            return []
    
    def add_schedule(self, room_id, start_time, end_time, booker, approval_status="Pending"):
        """Add new schedule"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Jadwal (ID_Ruangan, Waktu_Mulai, Waktu_Selesai, Pemesan, Status_Approval)
                    VALUES (?, ?, ?, ?, ?)
                """, (room_id, start_time, end_time, booker, approval_status))
                conn.commit()
                return True
        except Exception as e:
            print(f"Add schedule error: {e}")
            return False
    
    def update_schedule_status(self, schedule_id, status):
        """Update schedule status"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE Jadwal SET Status_Approval = ? WHERE ID_Jadwal = ?
                """, (status, schedule_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Update schedule error: {e}")
            return False
