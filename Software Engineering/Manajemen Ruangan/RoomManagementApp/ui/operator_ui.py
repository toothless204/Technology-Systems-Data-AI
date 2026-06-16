import tkinter as tk
from tkinter import messagebox, ttk

class OperatorUI:
    def __init__(self, root, user, auth_handler):
        self.root = root
        self.user = user
        self.auth_handler = auth_handler
        self.db_handler = auth_handler.db_handler
        
        self.root.title(f"Room Management - {user['username']} ({user['role']})")
        self.root.geometry("700x600")
        
        self.show_main_ui()
    
    def show_main_ui(self):
        """Show main UI"""
        # Header
        header = ttk.Frame(self.root)
        header.pack(fill="x", padx=10, pady=10)
        
        user_label = ttk.Label(header, text=f"Welcome {self.user['username']} ({self.user['role']})", 
                               font=("Arial", 12, "bold"))
        user_label.pack(side="left")
        
        logout_btn = ttk.Button(header, text="Logout", command=self.logout)
        logout_btn.pack(side="right")
        
        # Notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab 1: Manage Rooms
        rooms_tab = ttk.Frame(notebook)
        notebook.add(rooms_tab, text="Manage Rooms")
        self.show_rooms_tab(rooms_tab)
        
        # Tab 2: Manage Schedules
        schedules_tab = ttk.Frame(notebook)
        notebook.add(schedules_tab, text="Manage Schedules")
        self.show_schedules_tab(schedules_tab)
        
        # Tab 3: Approve Bookings
        approve_tab = ttk.Frame(notebook)
        notebook.add(approve_tab, text="Approve Bookings")
        self.show_approve_tab(approve_tab)
    
    def show_rooms_tab(self, tab):
        """Show rooms management tab"""
        # Rooms list
        ttk.Label(tab, text="Rooms List:", font=("Arial", 11, "bold")).pack(anchor="w", padx=10, pady=5)
        
        tree_frame = ttk.Frame(tab)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("ID", "Name", "Capacity", "Location", "Facilities")
        tree = ttk.Treeview(tree_frame, columns=columns, height=10, show="headings")
        
        for col in columns:
            tree.column(col, width=120)
            tree.heading(col, text=col)
        
        rooms = self.db_handler.get_all_rooms()
        for room in rooms:
            tree.insert("", "end", values=room)
        
        tree.pack(fill="both", expand=True)
    
    def show_schedules_tab(self, tab):
        """Show schedules management tab"""
        # Room selection
        select_frame = ttk.Frame(tab)
        select_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(select_frame, text="Select Room:").pack(side="left", padx=5)
        
        room_var = tk.StringVar()
        rooms = self.db_handler.get_all_rooms()
        room_options = [f"{r[0]} - {r[1]}" for r in rooms]
        
        room_combo = ttk.Combobox(select_frame, textvariable=room_var, values=room_options, width=30)
        room_combo.pack(side="left", padx=5)
        
        # Schedules list
        ttk.Label(tab, text="Schedules:", font=("Arial", 11, "bold")).pack(anchor="w", padx=10, pady=5)
        
        tree_frame = ttk.Frame(tab)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("ID", "Room", "Start", "End", "Status", "Booker", "Approval")
        tree = ttk.Treeview(tree_frame, columns=columns, height=10, show="headings")
        
        for col in columns:
            tree.column(col, width=100)
            tree.heading(col, text=col)
        
        def on_room_select(event=None):
            tree.delete(*tree.get_children())
            if room_var.get():
                room_id = int(room_var.get().split()[0])
                schedules = self.db_handler.get_schedules_by_room(room_id)
                for schedule in schedules:
                    tree.insert("", "end", values=schedule)
        
        room_combo.bind("<<ComboboxSelected>>", on_room_select)
        tree.pack(fill="both", expand=True)
    
    def show_approve_tab(self, tab):
        """Show booking approval tab"""
        ttk.Label(tab, text="Pending Bookings:", font=("Arial", 11, "bold")).pack(anchor="w", padx=10, pady=5)
        
        tree_frame = ttk.Frame(tab)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("ID", "Room", "Start", "End", "Booker", "Status")
        tree = ttk.Treeview(tree_frame, columns=columns, height=10, show="headings")
        
        for col in columns:
            tree.column(col, width=100)
            tree.heading(col, text=col)
        
        # Load data
        def load_pending():
            tree.delete(*tree.get_children())
            # Simple query for all schedules with Pending status
            import sqlite3
            try:
                with sqlite3.connect(self.db_handler.db_name) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT j.ID_Jadwal, r.Nama_Ruangan, j.Waktu_Mulai, j.Waktu_Selesai, j.Pemesan, j.Status_Approval
                        FROM Jadwal j
                        JOIN Ruangan r ON j.ID_Ruangan = r.ID_Ruangan
                        WHERE j.Status_Approval = 'Pending'
                    """)
                    for row in cursor.fetchall():
                        tree.insert("", "end", values=row)
            except Exception as e:
                print(f"Error: {e}")
        
        load_pending()
        tree.pack(fill="both", expand=True)
        
        # Action buttons
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        def approve():
            selected = tree.selection()
            if not selected:
                messagebox.showerror("Error", "Select a booking")
                return
            
            item = selected[0]
            schedule_id = tree.item(item)['values'][0]
            self.db_handler.update_schedule_status(schedule_id, "Approved")
            messagebox.showinfo("Success", "Booking approved!")
            load_pending()
        
        def reject():
            selected = tree.selection()
            if not selected:
                messagebox.showerror("Error", "Select a booking")
                return
            
            item = selected[0]
            schedule_id = tree.item(item)['values'][0]
            self.db_handler.update_schedule_status(schedule_id, "Rejected")
            messagebox.showinfo("Success", "Booking rejected!")
            load_pending()
        
        ttk.Button(button_frame, text="Approve", command=approve).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Reject", command=reject).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Refresh", command=load_pending).pack(side="left", padx=5)
    
    def logout(self):
        """Logout user"""
        from ui.login_ui import LoginUI
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.geometry("400x300")
        login_ui = LoginUI(self.root, self.auth_handler, lambda role: None)
