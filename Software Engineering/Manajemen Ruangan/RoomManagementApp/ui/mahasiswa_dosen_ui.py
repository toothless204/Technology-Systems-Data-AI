import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

class MahasiswaDoseninUI:
    def __init__(self, root, user, auth_handler):
        self.root = root
        self.user = user
        self.auth_handler = auth_handler
        self.db_handler = auth_handler.db_handler
        
        self.root.title(f"Room Management - {user['username']} ({user['role']})")
        self.root.geometry("600x500")
        
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
        
        # Main content
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Rooms section
        ttk.Label(main_frame, text="Available Rooms:", font=("Arial", 11, "bold")).pack(anchor="w", pady=5)
        
        # Treeview for rooms
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill="both", expand=True, pady=5)
        
        columns = ("ID", "Room Name", "Capacity", "Location", "Facilities")
        tree = ttk.Treeview(tree_frame, columns=columns, height=8, show="headings")
        
        for col in columns:
            tree.column(col, width=100)
            tree.heading(col, text=col)
        
        rooms = self.db_handler.get_all_rooms()
        for room in rooms:
            tree.insert("", "end", values=room)
        
        tree.pack(fill="both", expand=True)
        
        # Booking section
        booking_frame = ttk.LabelFrame(main_frame, text="Book Room")
        booking_frame.pack(fill="x", pady=10)
        
        ttk.Label(booking_frame, text="Room ID:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        room_id_entry = ttk.Entry(booking_frame, width=15)
        room_id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(booking_frame, text="Start Time (YYYY-MM-DD HH:MM):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        start_entry = ttk.Entry(booking_frame, width=25)
        start_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(booking_frame, text="End Time (YYYY-MM-DD HH:MM):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        end_entry = ttk.Entry(booking_frame, width=25)
        end_entry.grid(row=2, column=1, padx=5, pady=5)
        
        def book_room():
            try:
                room_id = int(room_id_entry.get())
                start_time = start_entry.get()
                end_time = end_entry.get()
                
                if not room_id or not start_time or not end_time:
                    messagebox.showerror("Error", "All fields required")
                    return
                
                # Validate datetime format
                datetime.strptime(start_time, "%Y-%m-%d %H:%M")
                datetime.strptime(end_time, "%Y-%m-%d %H:%M")
                
                success = self.db_handler.add_schedule(room_id, start_time, end_time, self.user['username'])
                if success:
                    messagebox.showinfo("Success", "Room booked successfully! Waiting for approval.")
                    room_id_entry.delete(0, tk.END)
                    start_entry.delete(0, tk.END)
                    end_entry.delete(0, tk.END)
                else:
                    messagebox.showerror("Error", "Failed to book room")
            except ValueError as e:
                messagebox.showerror("Error", "Invalid input format")
        
        book_btn = ttk.Button(booking_frame, text="Book Room", command=book_room)
        book_btn.grid(row=3, column=0, columnspan=2, pady=10)
    
    def logout(self):
        """Logout user"""
        from ui.login_ui import LoginUI
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.geometry("400x300")
        login_ui = LoginUI(self.root, self.auth_handler, lambda role: None)
