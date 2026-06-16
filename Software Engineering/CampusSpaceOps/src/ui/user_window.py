"""
User window (staff / student) — tabs: My Bookings | New Booking
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.theme import *
from services import booking_service as bs
from services.room_service import get_all_rooms


class UserWindow:
    def __init__(self, root: tk.Tk, user: dict, on_logout):
        self.root      = root
        self.user      = user
        self.on_logout = on_logout
        root.title(f"CampusSpaceOps — {user['full_name']}")
        root.configure(bg=BG)
        root.minsize(860, 580)
        self._build()
        self._load_my_bookings()

    def _build(self):
        # Header
        header = tk.Frame(self.root, bg=PANEL, pady=10)
        header.pack(fill="x")
        tk.Label(header, text="◉  CAMPUSSPACEOPS", bg=PANEL, fg=ACCENT,
                 font=("Courier New", 12, "bold")).pack(side="left", padx=16)
        tk.Label(header, text=f"● {self.user['full_name']}  [{self.user['role'].upper()}]",
                 bg=PANEL, fg=SUBTEXT, font=FONT_BODY).pack(side="left", padx=8)
        ttk.Button(header, text="Logout", command=self._logout
                   ).pack(side="right", padx=16)

        separator(self.root)

        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True)

        self._build_my_bookings_tab(nb)
        self._build_new_booking_tab(nb)

    # ------------------------------------------------------------------
    # Tab 1 — My Bookings
    # ------------------------------------------------------------------
    def _build_my_bookings_tab(self, nb):
        frame = ttk.Frame(nb)
        nb.add(frame, text=" ☰  My Bookings ")

        cols = ("id","room","date","start","end","attendees","purpose","status","submitted")
        self.my_tree = ttk.Treeview(frame, columns=cols, show="headings", height=18)
        for col, w, lbl in zip(cols,
            [40,90,90,55,55,50,220,80,130],
            ["#","Room","Date","Start","End","Pax","Purpose","Status","Submitted"]):
            self.my_tree.heading(col, text=lbl)
            self.my_tree.column(col, width=w, anchor="w")
        self.my_tree.pack(fill="both", expand=True, padx=12, pady=8)
        self.my_tree.tag_configure("approved",  foreground=GREEN)
        self.my_tree.tag_configure("rejected",   foreground=RED)
        self.my_tree.tag_configure("pending",    foreground=ACCENT)
        self.my_tree.tag_configure("cancelled",  foreground=SUBTEXT)

        btn = tk.Frame(frame, bg=BG)
        btn.pack(fill="x", padx=12, pady=4)
        ttk.Button(btn, text="↺ Refresh", command=self._load_my_bookings
                   ).pack(side="left", padx=4)
        ttk.Button(btn, text="✗ Cancel Selected", style="Danger.TButton",
                   command=self._cancel_booking).pack(side="left", padx=4)

    def _load_my_bookings(self):
        self.my_tree.delete(*self.my_tree.get_children())
        for b in bs.get_user_bookings(self.user["id"]):
            self.my_tree.insert("", "end", iid=str(b["id"]),
                tags=(b["status"],),
                values=(b["id"], b["room_name"], b["date"],
                        b["start_time"], b["end_time"], b["attendees"],
                        b["purpose"][:50], b["status"], b["submitted_at"][:16]))

    def _cancel_booking(self):
        sel = self.my_tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Select a booking to cancel.")
            return
        bid = int(sel[0])
        msg = bs.cancel_booking(bid, self.user["id"])
        messagebox.showinfo("Result", msg)
        self._load_my_bookings()

    # ------------------------------------------------------------------
    # Tab 2 — New Booking
    # ------------------------------------------------------------------
    def _build_new_booking_tab(self, nb):
        frame = ttk.Frame(nb)
        nb.add(frame, text=" + New Booking ")

        inner = tk.Frame(frame, bg=BG)
        inner.pack(padx=48, pady=24, anchor="nw")

        tk.Label(inner, text="New Room Booking Request",
                 bg=BG, fg=TEXT, font=FONT_HEAD).grid(row=0, column=0, columnspan=2,
                                                       sticky="w", pady=(0,16))

        self.rooms = get_all_rooms()
        room_names = [f"{r['name']} (cap {r['capacity']}, {r['location']})" for r in self.rooms]

        fields = [
            ("Room",         "room",     "combo",  room_names),
            ("Date (YYYY-MM-DD)", "date","entry",  str(date.today() + timedelta(days=1))),
            ("Start Time (HH:MM)","start","entry", "09:00"),
            ("End Time (HH:MM)",  "end",  "entry", "11:00"),
            ("Attendees",    "att",      "entry",  "20"),
            ("Purpose",      "purpose",  "entry",  ""),
        ]

        self._form_vars = {}
        for i, (label, key, widget_type, default) in enumerate(fields):
            tk.Label(inner, text=label, bg=BG, fg=SUBTEXT,
                     font=FONT_BODY).grid(row=i*2+1, column=0, sticky="w", pady=(6,2))
            v = tk.StringVar(value=default if isinstance(default, str) else "")
            if widget_type == "combo":
                w = ttk.Combobox(inner, textvariable=v, values=default, width=44)
                if default:
                    w.current(0)
            else:
                w = ttk.Entry(inner, textvariable=v, width=46)
                v.set(default)
            w.grid(row=i*2+2, column=0, sticky="ew")
            self._form_vars[key] = v

        self.conflict_var = tk.StringVar()
        tk.Label(inner, textvariable=self.conflict_var,
                 bg=BG, fg=RED, font=FONT_BODY, wraplength=440
                 ).grid(row=len(fields)*2+2, column=0, sticky="w", pady=4)

        ttk.Button(inner, text="Check Conflicts",
                   command=self._check_conflicts
                   ).grid(row=len(fields)*2+3, column=0, sticky="w", pady=4)
        ttk.Button(inner, text="Submit Booking Request", style="Accent.TButton",
                   command=self._submit
                   ).grid(row=len(fields)*2+4, column=0, sticky="ew", pady=8)

    def _get_room_id(self) -> int | None:
        sel = self._form_vars["room"].get()
        for r in self.rooms:
            if sel.startswith(r["name"]):
                return r["id"]
        return None

    def _check_conflicts(self):
        rid  = self._get_room_id()
        if not rid:
            self.conflict_var.set("Select a room first.")
            return
        conflicts = bs.check_conflict(
            rid,
            self._form_vars["date"].get(),
            self._form_vars["start"].get(),
            self._form_vars["end"].get(),
        )
        if conflicts:
            c = conflicts[0]
            self.conflict_var.set(
                f"⚠ Conflict: {c['requester_name']} already has {c['start_time']}–{c['end_time']} "
                f"on this date (status={c['status']})"
            )
        else:
            self.conflict_var.set("✓ No conflicts detected for this slot.")

    def _submit(self):
        rid = self._get_room_id()
        if not rid:
            messagebox.showerror("Error", "Select a room.")
            return
        try:
            att = int(self._form_vars["att"].get())
        except ValueError:
            messagebox.showerror("Error", "Attendees must be a number.")
            return

        booking_id, err = bs.submit_booking(
            user_id   = self.user["id"],
            room_id   = rid,
            date      = self._form_vars["date"].get(),
            start_time= self._form_vars["start"].get(),
            end_time  = self._form_vars["end"].get(),
            purpose   = self._form_vars["purpose"].get(),
            attendees = att,
        )
        if err:
            messagebox.showerror("Booking rejected", err)
        else:
            messagebox.showinfo("Success", f"Booking #{booking_id} submitted. Awaiting approval.")
            self._load_my_bookings()

    def _logout(self):
        if messagebox.askyesno("Logout", "Return to login screen?"):
            self.on_logout()
