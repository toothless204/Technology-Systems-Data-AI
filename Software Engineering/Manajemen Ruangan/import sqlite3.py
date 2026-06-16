import sqlite3
import csv
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox

class DatabaseHandler:
    # ... (metode lain)

    def generate_report(self, period, start_date, end_date=None):
        try:
            with sqlite3.connect(self.db_name, timeout=10) as conn:
                cursor = conn.cursor()
                if period == "Harian":
                    query = """
                        SELECT 
                            j.ID_Jadwal,
                            r.Nama_Ruangan,
                            j.Waktu_Mulai,
                            j.Waktu_Selesai,
                            j.Status,
                            j.Pemesan,
                            j.Status_Approval
                        FROM 
                            Jadwal j
                        JOIN 
                            Ruangan r ON j.ID_Ruangan = r.ID_Ruangan
                        WHERE 
                            DATE(j.Waktu_Mulai) = DATE(?)
                        ORDER BY 
                            j.Waktu_Mulai;
                    """
                    cursor.execute(query, (start_date,))
                elif period == "Mingguan":
                    query = """
                        SELECT 
                            j.ID_Jadwal,
                            r.Nama_Ruangan,
                            j.Waktu_Mulai,
                            j.Waktu_Selesai,
                            j.Status,
                            j.Pemesan,
                            j.Status_Approval
                        FROM 
                            Jadwal j
                        JOIN 
                            Ruangan r ON j.ID_Ruangan = r.ID_Ruangan
                        WHERE 
                            DATE(j.Waktu_Mulai) BETWEEN DATE(?) AND DATE(?)
                        ORDER BY 
                            j.Waktu_Mulai;
                    """
                    cursor.execute(query, (start_date, end_date))
                elif period == "Bulanan":
                    query = """
                        SELECT 
                            j.ID_Jadwal,
                            r.Nama_Ruangan,
                            j.Waktu_Mulai,
                            j.Waktu_Selesai,
                            j.Status,
                            j.Pemesan,
                            j.Status_Approval
                        FROM 
                            Jadwal j
                        JOIN 
                            Ruangan r ON j.ID_Ruangan = r.ID_Ruangan
                        WHERE 
                            strftime('%Y-%m', j.Waktu_Mulai) = strftime('%Y-%m', DATE(?))
                        ORDER BY 
                            j.Waktu_Mulai;
                    """
                    cursor.execute(query, (start_date,))
                else:
                    logging.error("Periode laporan tidak valid.")
                    messagebox.showerror("Error", "Periode laporan tidak valid.")
                    return []
                
                report_data = cursor.fetchall()
                logging.info(f"Laporan {period} dari {start_date} sampai {end_date} berhasil dihasilkan.")
                return report_data
        except Exception as e:
            logging.error(f"Error saat menghasilkan laporan: {e}")
            messagebox.showerror("Error", f"Operasi database gagal: {e}")
            return []
    
    def export_to_csv(self, data, filename):
        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Menulis header
                writer.writerow(["ID Jadwal", "Nama Ruangan", "Waktu Mulai", "Waktu Selesai", "Status", "Pemesan", "Status Approval"])
                # Menulis data
                writer.writerows(data)
            logging.info(f"Laporan berhasil diekspor ke {filename}.")
            messagebox.showinfo("Sukses", f"Laporan berhasil diekspor ke {filename}.")
        except Exception as e:
            logging.error(f"Error saat mengekspor laporan ke CSV: {e}")
            messagebox.showerror("Error", f"Error saat mengekspor laporan ke CSV: {e}")
