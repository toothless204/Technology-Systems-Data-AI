"""
Admin / Operator window — tabs: Bookings | Rooms | Users | Analytics | Optimization
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.theme import *
from services import booking_service as bs
from services import room_service as rs
from services import auth_service as auth
from services import analytics_service as analytics
from optimization.room_assignment import solve_pending_bookings, optimization_summary


STATUS_COLORS = {
    "approved":  GREEN,
    "rejected":  RED,
    "pending":   ACCENT,
    "cancelled": SUBTEXT,
}


class AdminWindow:
    def __init__(self, root: tk.Tk, user: dict, on_logout):
        self.root     = root
        self.user     = user
        self.on_logout = on_logout
        root.title(f"CampusSpaceOps — Admin ({user['full_name']})")
        root.configure(bg=BG)
        root.minsize(1000, 640)
        self._build()
        self._load_bookings()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
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

        separator(self.root, pady=0)

        # Notebook
        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=0, pady=0)

        self._build_bookings_tab(nb)
        self._build_rooms_tab(nb)
        self._build_users_tab(nb)
        self._build_analytics_tab(nb)
        self._build_optimization_tab(nb)

    # ------------------------------------------------------------------
    # Tab 1 — Bookings
    # ------------------------------------------------------------------
    def _build_bookings_tab(self, nb):
        frame = ttk.Frame(nb)
        nb.add(frame, text=" ☰  Bookings ")

        # Filter bar
        bar = tk.Frame(frame, bg=BG)
        bar.pack(fill="x", padx=12, pady=8)
        tk.Label(bar, text="Filter:", bg=BG, fg=SUBTEXT).pack(side="left")
        self.booking_filter = tk.StringVar(value="all")
        for val, label in [("all","All"),("pending","Pending"),
                           ("approved","Approved"),("rejected","Rejected")]:
            tk.Radiobutton(bar, text=label, variable=self.booking_filter,
                           value=val, bg=BG, fg=TEXT, selectcolor=PANEL,
                           activebackground=BG, command=self._load_bookings
                           ).pack(side="left", padx=6)
        ttk.Button(bar, text="↺ Refresh", command=self._load_bookings
                   ).pack(side="right", padx=4)

        # Tree
        cols = ("id","requester","room","date","start","end","attendees","purpose","status","submitted")
        self.book_tree = ttk.Treeview(frame, columns=cols, show="headings", height=18)
        headers = {"id":"#","requester":"Requester","room":"Room","date":"Date",
                   "start":"Start","end":"End","attendees":"Pax","purpose":"Purpose",
                   "status":"Status","submitted":"Submitted"}
        widths  = {"id":40,"requester":130,"room":70,"date":90,"start":55,"end":55,
                   "attendees":40,"purpose":200,"status":80,"submitted":130}
        for c in cols:
            self.book_tree.heading(c, text=headers[c])
            self.book_tree.column(c, width=widths[c], anchor="w")
        self.book_tree.pack(fill="both", expand=True, padx=12)
        self.book_tree.tag_configure("approved", foreground=GREEN)
        self.book_tree.tag_configure("rejected",  foreground=RED)
        self.book_tree.tag_configure("pending",   foreground=ACCENT)
        self.book_tree.tag_configure("cancelled", foreground=SUBTEXT)

        # Action buttons
        btn_bar = tk.Frame(frame, bg=BG)
        btn_bar.pack(fill="x", padx=12, pady=8)
        ttk.Button(btn_bar, text="✓ Approve", style="Accent.TButton",
                   command=self._approve).pack(side="left", padx=4)
        ttk.Button(btn_bar, text="✗ Reject", style="Danger.TButton",
                   command=self._reject).pack(side="left", padx=4)

    def _load_bookings(self):
        f = self.booking_filter.get()
        rows = bs.get_all_bookings(None if f == "all" else f)
        self.book_tree.delete(*self.book_tree.get_children())
        for b in rows:
            tag = b["status"]
            self.book_tree.insert("", "end", iid=str(b["id"]), tags=(tag,),
                values=(b["id"], b["requester_name"], b["room_name"],
                        b["date"], b["start_time"], b["end_time"],
                        b["attendees"], b["purpose"][:40], b["status"],
                        b["submitted_at"][:16]))

    def _selected_booking_id(self) -> int | None:
        sel = self.book_tree.selection()
        return int(sel[0]) if sel else None

    def _approve(self):
        bid = self._selected_booking_id()
        if not bid:
            messagebox.showwarning("No selection", "Select a booking first.")
            return
        msg = bs.approve_booking(bid, self.user["id"])
        messagebox.showinfo("Result", msg)
        self._load_bookings()

    def _reject(self):
        bid = self._selected_booking_id()
        if not bid:
            messagebox.showwarning("No selection", "Select a booking first.")
            return
        reason = simpledialog.askstring("Reject reason", "Enter rejection reason (optional):", parent=self.root) or ""
        msg = bs.reject_booking(bid, self.user["id"], reason)
        messagebox.showinfo("Result", msg)
        self._load_bookings()

    # ------------------------------------------------------------------
    # Tab 2 — Rooms
    # ------------------------------------------------------------------
    def _build_rooms_tab(self, nb):
        frame = ttk.Frame(nb)
        nb.add(frame, text=" ⬢  Rooms ")

        cols = ("id","name","capacity","location","type","active")
        self.room_tree = ttk.Treeview(frame, columns=cols, show="headings", height=20)
        for c, w in zip(cols, [40,100,70,160,90,60]):
            self.room_tree.heading(c, text=c.title())
            self.room_tree.column(c, width=w, anchor="w")
        self.room_tree.pack(fill="both", expand=True, padx=12, pady=(8,0))
        self._load_rooms()

        btn = tk.Frame(frame, bg=BG)
        btn.pack(fill="x", padx=12, pady=8)
        ttk.Button(btn, text="+ Add Room", style="Accent.TButton",
                   command=self._add_room_dialog).pack(side="left", padx=4)
        ttk.Button(btn, text="↺ Refresh", command=self._load_rooms
                   ).pack(side="left", padx=4)
        ttk.Button(btn, text="Deactivate", style="Danger.TButton",
                   command=self._deactivate_room).pack(side="left", padx=4)

    def _load_rooms(self):
        from database.db import fetchall
        rows = fetchall("SELECT * FROM rooms ORDER BY name")
        self.room_tree.delete(*self.room_tree.get_children())
        for r in rows:
            self.room_tree.insert("", "end", iid=str(r["id"]),
                values=(r["id"], r["name"], r["capacity"],
                        r["location"], r["type"], "Yes" if r["is_active"] else "No"))

    def _add_room_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Add Room")
        win.configure(bg=PANEL)
        win.resizable(False, False)
        fields = {}
        for i, (label, key) in enumerate([
            ("Name", "name"), ("Capacity", "cap"),
            ("Location", "loc"), ("Type (lecture/lab/seminar/meeting)", "typ")
        ]):
            tk.Label(win, text=label, bg=PANEL, fg=SUBTEXT).grid(row=i*2, column=0, padx=16, sticky="w")
            v = tk.StringVar()
            ttk.Entry(win, textvariable=v, width=30).grid(row=i*2+1, column=0, padx=16, pady=(0,8))
            fields[key] = v

        def save():
            try:
                rs.create_room(fields["name"].get(), int(fields["cap"].get()),
                               fields["loc"].get(), fields["typ"].get())
                self._load_rooms()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=win)

        ttk.Button(win, text="Save", style="Accent.TButton", command=save
                   ).grid(row=8, column=0, padx=16, pady=12, sticky="ew")

    def _deactivate_room(self):
        sel = self.room_tree.selection()
        if not sel:
            return
        rid = int(sel[0])
        if messagebox.askyesno("Confirm", f"Deactivate room #{rid}?"):
            rs.deactivate_room(rid)
            self._load_rooms()

    # ------------------------------------------------------------------
    # Tab 3 — Users
    # ------------------------------------------------------------------
    def _build_users_tab(self, nb):
        frame = ttk.Frame(nb)
        nb.add(frame, text=" ◉  Users ")

        cols = ("id","username","role","full_name","email","created_at")
        self.user_tree = ttk.Treeview(frame, columns=cols, show="headings", height=20)
        for c, w in zip(cols, [40,110,70,160,180,140]):
            self.user_tree.heading(c, text=c.replace("_"," ").title())
            self.user_tree.column(c, width=w, anchor="w")
        self.user_tree.pack(fill="both", expand=True, padx=12, pady=8)
        self._load_users()

        btn = tk.Frame(frame, bg=BG)
        btn.pack(fill="x", padx=12, pady=4)
        ttk.Button(btn, text="+ Add User", style="Accent.TButton",
                   command=self._add_user_dialog).pack(side="left", padx=4)
        ttk.Button(btn, text="↺ Refresh", command=self._load_users
                   ).pack(side="left", padx=4)

    def _load_users(self):
        self.user_tree.delete(*self.user_tree.get_children())
        for u in auth.get_all_users():
            self.user_tree.insert("", "end", iid=str(u["id"]),
                values=(u["id"], u["username"], u["role"],
                        u["full_name"], u["email"] or "", u["created_at"][:16]))

    def _add_user_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Add User")
        win.configure(bg=PANEL)
        win.resizable(False, False)
        fields = {}
        for i, (lbl, key, show) in enumerate([
            ("Username","un",""), ("Password","pw","•"),
            ("Full Name","fn",""), ("Email","em",""),
        ]):
            tk.Label(win, text=lbl, bg=PANEL, fg=SUBTEXT).grid(row=i*2, column=0, padx=16, sticky="w")
            v = tk.StringVar()
            ttk.Entry(win, textvariable=v, width=30, show=show).grid(row=i*2+1, column=0, padx=16, pady=(0,8))
            fields[key] = v
        tk.Label(win, text="Role", bg=PANEL, fg=SUBTEXT).grid(row=8, column=0, padx=16, sticky="w")
        role_var = tk.StringVar(value="student")
        ttk.Combobox(win, textvariable=role_var, values=["admin","staff","student"],
                     width=28).grid(row=9, column=0, padx=16, pady=(0,8))

        def save():
            try:
                auth.create_user(fields["un"].get(), fields["pw"].get(),
                                 role_var.get(), fields["fn"].get(), fields["em"].get())
                self._load_users()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=win)

        ttk.Button(win, text="Save", style="Accent.TButton", command=save
                   ).grid(row=10, column=0, padx=16, pady=12, sticky="ew")

    # ------------------------------------------------------------------
    # Tab 4 — Analytics
    # ------------------------------------------------------------------
    def _build_analytics_tab(self, nb):
        frame = ttk.Frame(nb)
        nb.add(frame, text=" △  Analytics ")

        scroll = tk.Canvas(frame, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(frame, orient="vertical", command=scroll.yview)
        scroll.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        scroll.pack(fill="both", expand=True)

        self.analytics_inner = tk.Frame(scroll, bg=BG)
        win_id = scroll.create_window((0, 0), window=self.analytics_inner, anchor="nw")
        self.analytics_inner.bind("<Configure>",
            lambda e: scroll.configure(scrollregion=scroll.bbox("all")))
        scroll.bind("<Configure>",
            lambda e: scroll.itemconfig(win_id, width=e.width))

        ttk.Button(frame, text="↺ Refresh Analytics",
                   command=self._load_analytics).pack(side="bottom", pady=8)
        self._load_analytics()

    def _load_analytics(self):
        for w in self.analytics_inner.winfo_children():
            w.destroy()

        data = analytics.full_dashboard()
        pad = dict(padx=16, pady=4, sticky="w")

        # --- KPI row ---
        rs_data = data["rejection_stats"]
        lt      = data["lead_time"]
        kpi_frame = tk.Frame(self.analytics_inner, bg=BG)
        kpi_frame.pack(fill="x", padx=12, pady=8)
        kpis = [
            ("Total Bookings",    rs_data["total"],                 TEXT),
            ("Approval Rate",     f"{rs_data['approval_rate']}%",   GREEN),
            ("Rejection Rate",    f"{rs_data['rejection_rate']}%",  RED),
            ("Avg Lead Time",     f"{lt['avg_lead_hours']}h",       BLUE),
            ("Pending",           rs_data["pending"],               ACCENT),
        ]
        for i, (label, val, color) in enumerate(kpis):
            c = tk.Frame(kpi_frame, bg=PANEL, bd=0,
                         highlightthickness=1, highlightbackground=BORDER)
            c.grid(row=0, column=i, padx=6, pady=4, ipadx=16, ipady=10, sticky="nsew")
            kpi_frame.columnconfigure(i, weight=1)
            tk.Label(c, text=str(val), bg=PANEL, fg=color,
                     font=("Segoe UI", 18, "bold")).pack(pady=(8,2))
            tk.Label(c, text=label, bg=PANEL, fg=SUBTEXT, font=FONT_BODY).pack(pady=(0,8))

        separator(self.analytics_inner, pady=(4,8))

        # --- Room utilization table ---
        tk.Label(self.analytics_inner, text="Room Utilization (last 30 days)",
                 bg=BG, fg=TEXT, font=FONT_HEAD).pack(**pad)
        util_cols = ("room","capacity","booked_h","avail_h","util_%","idle_seat_h","avg_pax","bookings")
        tree = ttk.Treeview(self.analytics_inner, columns=util_cols, show="headings", height=10)
        for col, w, label in zip(util_cols,
            [80,70,80,80,70,110,70,70],
            ["Room","Cap","Booked h","Avail h","Util %","Idle Seat·h","Avg Pax","Count"]):
            tree.heading(col, text=label)
            tree.column(col, width=w, anchor="center")
        for r in data["utilization"]:
            color = "low" if r["utilization_rate"] < 30 else ("high" if r["utilization_rate"] > 70 else "mid")
            tree.insert("", "end", tags=(color,),
                values=(r["room_name"], r["capacity"], r["booked_hours"],
                        r["available_hours"], f"{r['utilization_rate']}%",
                        r["idle_capacity_seat_hrs"], r["avg_attendees"],
                        r["booking_count"]))
        tree.tag_configure("high", foreground=GREEN)
        tree.tag_configure("mid",  foreground=ACCENT)
        tree.tag_configure("low",  foreground=RED)
        tree.pack(fill="x", padx=12, pady=(0,12))

        separator(self.analytics_inner, pady=(0,8))

        # --- Peak hours ---
        tk.Label(self.analytics_inner, text="Top 10 Peak Demand Slots",
                 bg=BG, fg=TEXT, font=FONT_HEAD).pack(**pad)
        peak_cols = ("day","hour","count")
        ptree = ttk.Treeview(self.analytics_inner, columns=peak_cols, show="headings", height=10)
        for col, w in zip(peak_cols, [80,80,120]):
            ptree.heading(col, text=col.title())
            ptree.column(col, width=w, anchor="center")
        for p in data["peak_hours"]:
            ptree.insert("", "end", values=(p["day"], p["hour"], p["count"]))
        ptree.pack(fill="x", padx=12, pady=(0,16))

    # ------------------------------------------------------------------
    # Tab 5 — Optimization
    # ------------------------------------------------------------------
    def _build_optimization_tab(self, nb):
        frame = ttk.Frame(nb)
        nb.add(frame, text=" ◆  Optimization ")

        top = tk.Frame(frame, bg=BG)
        top.pack(fill="x", padx=12, pady=8)
        tk.Label(top, text="Binary Integer Program — Room Assignment",
                 bg=BG, fg=TEXT, font=FONT_HEAD).pack(side="left")
        ttk.Button(top, text="▶ Run Solver", style="Accent.TButton",
                   command=self._run_optimization).pack(side="right")

        tk.Label(frame,
            text="Assigns pending bookings to rooms minimising wasted seats, "
                 "respecting capacity and time-overlap constraints.",
            bg=BG, fg=SUBTEXT, font=FONT_BODY).pack(padx=12, anchor="w")

        separator(frame, pady=8)

        self.opt_summary_var = tk.StringVar(value="Click 'Run Solver' to compute optimal assignments.")
        tk.Label(frame, textvariable=self.opt_summary_var,
                 bg=BG, fg=ACCENT, font=FONT_BODY).pack(padx=12, anchor="w", pady=(0,8))

        cols = ("req_id","requester","room","capacity","attendees","waste","assigned")
        self.opt_tree = ttk.Treeview(frame, columns=cols, show="headings", height=18)
        for col, w, lbl in zip(cols,
            [60,150,90,70,80,70,80],
            ["Req #","Requester","Room","Cap","Attendees","Waste","Assigned"]):
            self.opt_tree.heading(col, text=lbl)
            self.opt_tree.column(col, width=w, anchor="center")
        self.opt_tree.pack(fill="both", expand=True, padx=12, pady=(0,12))
        self.opt_tree.tag_configure("yes", foreground=GREEN)
        self.opt_tree.tag_configure("no",  foreground=RED)

    def _run_optimization(self):
        assignments = solve_pending_bookings()
        if not assignments:
            self.opt_summary_var.set("No pending bookings to assign.")
            return
        summary = optimization_summary(assignments)
        self.opt_summary_var.set(
            f"Solved {summary['total_requests']} requests — "
            f"{summary['assigned']} assigned, {summary['unassigned']} unassignable | "
            f"Total wasted seats: {summary['total_waste_seats']} | "
            f"Avg waste/booking: {summary['avg_waste_per_booking']}"
        )
        # Fill tree with requester names
        from database.db import fetchone
        self.opt_tree.delete(*self.opt_tree.get_children())
        for a in assignments:
            req = fetchone(
                "SELECT u.full_name FROM bookings b JOIN users u ON b.user_id=u.id WHERE b.id=?",
                (a["request_id"],),
            )
            name = req["full_name"] if req else "—"
            tag = "yes" if a["assigned"] else "no"
            self.opt_tree.insert("", "end", tags=(tag,),
                values=(a["request_id"], name, a["room_name"],
                        a["capacity"] or "—", a["attendees"],
                        a["waste"] if a["waste"] is not None else "—",
                        "Yes" if a["assigned"] else "No"))

    # ------------------------------------------------------------------

    def _logout(self):
        if messagebox.askyesno("Logout", "Return to login screen?"):
            self.on_logout()
