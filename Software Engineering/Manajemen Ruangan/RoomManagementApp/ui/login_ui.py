import tkinter as tk
from tkinter import messagebox, ttk
from ui.mahasiswa_dosen_ui import MahasiswaDoseninUI
from ui.operator_ui import OperatorUI

class LoginUI:
    def __init__(self, root, auth_handler, on_login_callback):
        self.root = root
        self.auth_handler = auth_handler
        self.on_login_callback = on_login_callback
        self.current_user = None
        
        self.root.title("Room Management System - Login")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        self.show_login_frame()
    
    def show_login_frame(self):
        """Show login frame"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True)
        
        # Title
        title = ttk.Label(frame, text="Room Management System", font=("Arial", 16, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Username
        ttk.Label(frame, text="Username:").grid(row=1, column=0, sticky="w", pady=10)
        username_entry = ttk.Entry(frame, width=25)
        username_entry.grid(row=1, column=1, pady=10)
        
        # Password
        ttk.Label(frame, text="Password:").grid(row=2, column=0, sticky="w", pady=10)
        password_entry = ttk.Entry(frame, width=25, show="*")
        password_entry.grid(row=2, column=1, pady=10)
        
        # Login button
        def login():
            username = username_entry.get()
            password = password_entry.get()
            
            if not username or not password:
                messagebox.showerror("Error", "Username dan password tidak boleh kosong")
                return
            
            user = self.auth_handler.authenticate(username, password)
            if user:
                self.current_user = user
                self.on_login_callback(user['role'])
                self.show_main_ui(user)
            else:
                messagebox.showerror("Error", "Username atau password salah")
        
        login_btn = ttk.Button(frame, text="Login", command=login)
        login_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Demo info
        demo_text = """
Demo Accounts:
- Operator: admin / admin123
- Mahasiswa: mahasiswa1 / pass123
- Dosen: dosen1 / pass123
        """
        info_label = tk.Label(frame, text=demo_text, font=("Arial", 8), justify="left")
        info_label.grid(row=4, column=0, columnspan=2, pady=10)
    
    def show_main_ui(self, user):
        """Show main UI based on user role"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        if user['role'] == 'Operator':
            OperatorUI(self.root, user, self.auth_handler)
        else:
            MahasiswaDoseninUI(self.root, user, self.auth_handler)
