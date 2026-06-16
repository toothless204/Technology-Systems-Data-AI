"""
CampusSpaceOps — Entry point
Run: python src/app.py
"""
import sys
import os
import tkinter as tk

# Allow imports from src/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import APP_TITLE, APP_WIDTH, APP_HEIGHT
from database.db import initialize_db
from ui.theme import configure_style, BG
from ui.login_window import LoginWindow
from ui.admin_window import AdminWindow
from ui.user_window import UserWindow


def main():
    # First-run: create DB and seed demo data
    initialize_db(seed=True)

    root = tk.Tk()
    root.title(APP_TITLE)
    root.configure(bg=BG)
    root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")

    configure_style()

    current_ui = {}

    def _clear():
        for widget in root.winfo_children():
            widget.destroy()

    def show_login():
        _clear()
        LoginWindow(root, on_success=on_login)

    def on_login(user: dict):
        _clear()
        if user["role"] == "admin":
            AdminWindow(root, user, on_logout=show_login)
        else:
            UserWindow(root, user, on_logout=show_login)

    show_login()
    root.mainloop()


if __name__ == "__main__":
    main()
