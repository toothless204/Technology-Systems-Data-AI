"""Shared dark-theme colour palette and widget factory."""
import tkinter as tk
from tkinter import ttk

BG       = "#0a0f1a"
PANEL    = "#0f172a"
BORDER   = "#1e293b"
ACCENT   = "#f59e0b"
TEXT     = "#f1f5f9"
SUBTEXT  = "#94a3b8"
GREEN    = "#10b981"
RED      = "#ef4444"
BLUE     = "#3b82f6"
PURPLE   = "#8b5cf6"

FONT_MONO = ("Courier New", 10)
FONT_BODY = ("Segoe UI", 10)
FONT_HEAD = ("Segoe UI", 12, "bold")
FONT_TITLE= ("Segoe UI", 16, "bold")


def configure_style():
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TFrame",        background=BG)
    style.configure("Panel.TFrame",  background=PANEL)
    style.configure("TLabel",        background=BG,    foreground=TEXT,   font=FONT_BODY)
    style.configure("Sub.TLabel",    background=PANEL, foreground=SUBTEXT, font=FONT_BODY)
    style.configure("Head.TLabel",   background=BG,    foreground=TEXT,   font=FONT_HEAD)
    style.configure("Title.TLabel",  background=BG,    foreground=ACCENT, font=FONT_TITLE)
    style.configure("Panel.TLabel",  background=PANEL, foreground=TEXT,   font=FONT_BODY)

    style.configure("TButton",
        background=BORDER, foreground=TEXT, font=FONT_BODY,
        borderwidth=0, focusthickness=0, relief="flat", padding=6)
    style.map("TButton",
        background=[("active", ACCENT)],
        foreground=[("active", BG)])

    style.configure("Accent.TButton",
        background=ACCENT, foreground=BG, font=("Segoe UI", 10, "bold"),
        borderwidth=0, relief="flat", padding=8)
    style.map("Accent.TButton",
        background=[("active", "#d97706")])

    style.configure("Danger.TButton",
        background=RED, foreground=TEXT, font=FONT_BODY,
        borderwidth=0, relief="flat", padding=6)

    style.configure("TEntry",
        fieldbackground=BORDER, foreground=TEXT, font=FONT_BODY,
        borderwidth=1, relief="flat")
    style.configure("TCombobox",
        fieldbackground=BORDER, foreground=TEXT, background=BORDER,
        selectbackground=ACCENT, font=FONT_BODY)

    style.configure("Treeview",
        background=PANEL, fieldbackground=PANEL,
        foreground=TEXT, font=FONT_BODY, rowheight=26)
    style.configure("Treeview.Heading",
        background=BORDER, foreground=SUBTEXT, font=("Segoe UI", 9, "bold"),
        relief="flat")
    style.map("Treeview",
        background=[("selected", ACCENT)],
        foreground=[("selected", BG)])

    style.configure("TNotebook",        background=BG, borderwidth=0)
    style.configure("TNotebook.Tab",
        background=BORDER, foreground=SUBTEXT, font=FONT_BODY,
        padding=[12, 6], borderwidth=0)
    style.map("TNotebook.Tab",
        background=[("selected", PANEL)],
        foreground=[("selected", ACCENT)])

    style.configure("Horizontal.TProgressbar",
        troughcolor=BORDER, background=ACCENT, thickness=6)

    return style


def separator(parent, **kw):
    f = tk.Frame(parent, bg=BORDER, height=1)
    f.pack(fill="x", **kw)


def card(parent, **kw):
    f = tk.Frame(parent, bg=PANEL, bd=0, highlightthickness=1,
                 highlightbackground=BORDER)
    return f


def badge(parent, text: str, color: str = ACCENT) -> tk.Label:
    return tk.Label(parent, text=text, bg=color, fg=BG,
                    font=("Segoe UI", 8, "bold"), padx=6, pady=2)
