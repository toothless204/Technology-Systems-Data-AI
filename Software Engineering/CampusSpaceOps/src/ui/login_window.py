import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.theme import *
from services.auth_service import authenticate


class LoginWindow:
    def __init__(self, root: tk.Tk, on_success):
        self.root = root
        self.on_success = on_success
        root.title("CampusSpaceOps — Login")
        root.configure(bg=BG)
        root.resizable(False, False)
        self._build()
        root.bind("<Return>", lambda e: self._login())

    def _build(self):
        root = self.root
        # Center card
        outer = tk.Frame(root, bg=BG)
        outer.pack(expand=True, fill="both", padx=80, pady=60)

        # Logo line
        tk.Label(outer, text="◉  CAMPUSSPACEOPS", bg=BG,
                 fg=ACCENT, font=("Courier New", 14, "bold")).pack(pady=(0, 4))
        tk.Label(outer, text="Room Operations Decision-Support System",
                 bg=BG, fg=SUBTEXT, font=FONT_BODY).pack(pady=(0, 24))

        separator(outer, pady=(0, 24))

        card_frame = tk.Frame(outer, bg=PANEL, bd=0,
                              highlightthickness=1, highlightbackground=BORDER)
        card_frame.pack(fill="x")

        inner = tk.Frame(card_frame, bg=PANEL)
        inner.pack(padx=32, pady=32)

        tk.Label(inner, text="Sign In", bg=PANEL, fg=TEXT,
                 font=FONT_HEAD).grid(row=0, column=0, columnspan=2,
                                      sticky="w", pady=(0, 20))

        tk.Label(inner, text="Username", bg=PANEL, fg=SUBTEXT,
                 font=FONT_BODY).grid(row=1, column=0, sticky="w", pady=(0, 4))
        self.username_var = tk.StringVar()
        e1 = ttk.Entry(inner, textvariable=self.username_var, width=32)
        e1.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        e1.focus()

        tk.Label(inner, text="Password", bg=PANEL, fg=SUBTEXT,
                 font=FONT_BODY).grid(row=3, column=0, sticky="w", pady=(0, 4))
        self.password_var = tk.StringVar()
        ttk.Entry(inner, textvariable=self.password_var, show="•", width=32
                  ).grid(row=4, column=0, sticky="ew", pady=(0, 20))

        self.error_var = tk.StringVar()
        tk.Label(inner, textvariable=self.error_var, bg=PANEL, fg=RED,
                 font=FONT_BODY).grid(row=5, column=0, sticky="w", pady=(0, 8))

        ttk.Button(inner, text="Sign In →", style="Accent.TButton",
                   command=self._login).grid(row=6, column=0, sticky="ew")

        inner.columnconfigure(0, weight=1)

        tk.Label(outer, text="Demo credentials: admin / password123  |  mhs001 / password123",
                 bg=BG, fg=SUBTEXT, font=("Segoe UI", 8)).pack(pady=(16, 0))

    def _login(self):
        user = authenticate(self.username_var.get().strip(),
                            self.password_var.get())
        if user:
            self.error_var.set("")
            self.on_success(user)
        else:
            self.error_var.set("Invalid username or password.")
