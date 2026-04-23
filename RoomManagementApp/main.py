from database.database_handler import DatabaseHandler
from auth.auth_handler import AuthHandler
from ui.login_ui import LoginUI
import tkinter as tk

if __name__ == "__main__":
    db_handler = DatabaseHandler()
    auth_handler = AuthHandler(db_handler)

    root = tk.Tk()

    def on_login_success(role):
        print(f"Logged in as {role}")

    login_ui = LoginUI(root, auth_handler, on_login_success)
    root.mainloop()
