# ui.py - UI components and windows for VAY Travels

import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import Image, ImageTk
import subprocess
import csv
import os
import webbrowser
import secrets
import hashlib
import base64
import threading
from urllib.parse import urlencode, parse_qs, urlparse
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests
from tkcalendar import DateEntry
from config import (APP_TITLE, WINDOW_SIZE, LOGIN_WINDOW_SIZE, SIGNUP_WINDOW_SIZE, GIF_PATH, CITIES, HOTELS_BY_CITY, FLIGHTS,
                   PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, SUCCESS_COLOR, WARNING_COLOR, ERROR_COLOR,
                   BACKGROUND_COLOR, CARD_COLOR, TEXT_COLOR, TEXT_LIGHT, TITLE_FONT, HEADER_FONT,
                   SUBHEADER_FONT, BUTTON_FONT, BODY_FONT, SMALL_FONT)
from database import db_manager
from logic import validate_date, calculate_distance, calculate_price, read_reviews, write_review

# Toast notification system
def show_toast(parent, message, duration=3000, toast_type="info"):
    """Show a modern toast notification"""
    colors = {
        "success": SUCCESS_COLOR,
        "error": ERROR_COLOR,
        "warning": WARNING_COLOR,
        "info": PRIMARY_COLOR
    }

    # Create toast window
    toast = tk.Toplevel(parent)
    toast.title("")
    toast.geometry("400x60")
    toast.overrideredirect(True)  # Remove window decorations
    toast.attributes("-topmost", True)  # Always on top

    # Position at bottom right
    x = parent.winfo_x() + parent.winfo_width() - 420
    y = parent.winfo_y() + parent.winfo_height() - 80
    toast.geometry(f"+{x}+{y}")

    # Toast frame
    frame = tk.Frame(toast, bg=colors.get(toast_type, PRIMARY_COLOR), bd=0)
    frame.pack(fill="both", expand=True)

    # Message label
    label = tk.Label(frame, text=message, font=BODY_FONT, fg="white", bg=colors.get(toast_type, PRIMARY_COLOR),
                     wraplength=380, justify="left", padx=15, pady=10)
    label.pack(fill="both", expand=True)

    # Auto destroy after duration
    def destroy_toast():
        try:
            toast.destroy()
        except:
            pass

    toast.after(duration, destroy_toast)

    # Click to dismiss
    def on_click(event):
        destroy_toast()

    frame.bind("<Button-1>", on_click)
    label.bind("<Button-1>", on_click)

    return toast
SMALL_FONT = ("Segoe UI", 10)

NAVY = "#0B1F33"
SKY = "#2563EB"
CORAL = "#F97316"
INK = "#122033"
MUTED = "#667085"
SURFACE = "#FFFFFF"
CANVAS = "#F4F7FB"
BORDER = "#DFE7F1"


def configure_modern_window(window, title, size, background=CANVAS):
    window.title(title)
    window.geometry(size)
    window.minsize(420, 420)
    window.configure(bg=background)


def create_modern_button(parent, text, command, style="primary", width=None):
    styles = {
        "primary": (SKY, "#1D4ED8", "white"),
        "coral": (CORAL, "#EA580C", "white"),
        "success": ("#059669", "#047857", "white"),
        "outline": (SURFACE, "#E8EEF7", INK),
        "danger": ("#DC2626", "#B91C1C", "white"),
    }
    normal, hover, foreground = styles.get(style, styles["primary"])
    button = tk.Button(parent, text=text, command=command,
                       font=("Segoe UI", 12, "bold"), bg=normal, fg=foreground,
                       activebackground=hover, activeforeground=foreground,
                       bd=0, cursor="hand2", relief="flat", padx=18, pady=10,
                       width=width)
    button.bind("<Enter>", lambda _event: button.config(bg=hover))
    button.bind("<Leave>", lambda _event: button.config(bg=normal))
    return button


def create_entry(parent, placeholder="", password=False, width=34):
    entry = tk.Entry(parent, font=("Segoe UI", 13), bg="#F8FAFC", fg=MUTED,
                     insertbackground=INK, bd=1, relief="solid", width=width,
                     highlightthickness=1, highlightbackground=BORDER,
                     highlightcolor=SKY, show="")
    entry.placeholder = placeholder
    entry.insert(0, placeholder)

    def on_focus_in(_event):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg=INK, show="*" if password else "")

    def on_focus_out(_event):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg=MUTED, show="")

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    return entry


def create_choice_cards(parent, variable, choices, columns=4, command=None):
    grid = tk.Frame(parent, bg=SURFACE)
    for index, choice in enumerate(choices):
        row, column = divmod(index, columns)
        radio = tk.Radiobutton(
            grid,
            text=choice,
            variable=variable,
            value=choice,
            indicatoron=False,
            cursor="hand2",
            font=("Segoe UI", 11, "bold"),
            bg="#F8FAFC",
            fg=INK,
            selectcolor="#DBEAFE",
            activebackground="#EFF6FF",
            activeforeground=INK,
            bd=1,
            relief="solid",
            padx=10,
            pady=9,
            width=16,
            command=command,
        )
        radio.grid(row=row, column=column, padx=5, pady=5)
    return grid


def create_scrollable_area(parent, background=CANVAS, horizontal=False):
    container = tk.Frame(parent, bg=background)
    container.pack(fill="both", expand=True)

    canvas = tk.Canvas(container, bg=background, highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    vertical = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    vertical.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=vertical.set)

    horizontal_scroll = None
    if horizontal:
        horizontal_scroll = tk.Scrollbar(parent, orient="horizontal", command=canvas.xview)
        horizontal_scroll.pack(side="bottom", fill="x")
        canvas.configure(xscrollcommand=horizontal_scroll.set)

    content = tk.Frame(canvas, bg=background)
    window_id = canvas.create_window((0, 0), window=content, anchor="nw")

    def update_scroll_region(_event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def resize_content(event):
        if not horizontal:
            canvas.itemconfigure(window_id, width=event.width)

    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    content.bind("<Configure>", update_scroll_region)
    canvas.bind("<Configure>", resize_content)
    canvas.bind_all("<MouseWheel>", on_mousewheel)

    return canvas, content, vertical

class LoginWindow:
    def __init__(self, on_login_success, on_signup):
        self.window = tk.Tk()
        configure_modern_window(self.window, f"{APP_TITLE} - Welcome", "1020x680")
        self.on_login_success = on_login_success
        self.on_signup = on_signup
        self.setup_ui()

    def setup_ui(self):
        hero = tk.Frame(self.window, bg=NAVY, width=520)
        hero.pack(side="left", fill="y")
        hero.pack_propagate(False)
        brand = tk.Frame(hero, bg=NAVY)
        brand.pack(anchor="nw", padx=42, pady=(40, 0))
        tk.Label(brand, text="VAY", font=("Segoe UI", 26, "bold"), bg=NAVY, fg="white").pack(side="left")
        tk.Label(brand, text="  TRAVELS", font=("Segoe UI", 12, "bold"), bg=NAVY, fg="#93C5FD").pack(side="left", pady=(8, 0))
        tk.Label(hero, text="Plan less.\nDiscover more.", font=("Segoe UI", 38, "bold"),
                 bg=NAVY, fg="white", justify="left").pack(anchor="nw", padx=42, pady=(90, 18))
        tk.Label(hero, text="Curated destinations, simple bookings,\nand memorable journeys across India.",
                 font=("Segoe UI", 14), bg=NAVY, fg="#C9D6E5", justify="left").pack(anchor="nw", padx=42)
        try:
            image = Image.open(os.path.join(os.path.dirname(__file__), "Kolkata.jpg")).resize((440, 230), Image.Resampling.LANCZOS)
            self.login_hero_image = ImageTk.PhotoImage(image)
            tk.Label(hero, image=self.login_hero_image, bg=NAVY, bd=0).pack(padx=42, pady=(45, 0), anchor="nw")
        except Exception:
            pass

        panel = tk.Frame(self.window, bg=SURFACE)
        panel.pack(side="right", fill="both", expand=True)
        card = tk.Frame(panel, bg=SURFACE)
        card.place(relx=0.5, rely=0.5, anchor="center", width=390)
        tk.Label(card, text="Welcome back", font=("Segoe UI", 28, "bold"), bg=SURFACE, fg=INK).pack(anchor="w")
        tk.Label(card, text="Sign in to continue to VAY Travels", font=("Segoe UI", 12), bg=SURFACE, fg=MUTED).pack(anchor="w", pady=(5, 28))

        tk.Label(card, text="Username", font=("Segoe UI", 11, "bold"), bg=SURFACE, fg=INK).pack(anchor="w", pady=(0, 7))
        self.entry_username = create_entry(card, "Enter your username", width=38)
        self.entry_username.pack(ipady=10)
        tk.Label(card, text="Password", font=("Segoe UI", 11, "bold"), bg=SURFACE, fg=INK).pack(anchor="w", pady=(18, 7))
        self.entry_password = create_entry(card, "Enter your password", password=True, width=38)
        self.entry_password.pack(ipady=10)

        tk.Label(card, text="Continue as", font=("Segoe UI", 11, "bold"), bg=SURFACE, fg=INK).pack(anchor="w", pady=(18, 7))
        self.login_role = tk.StringVar(value="user")
        role_frame = tk.Frame(card, bg=SURFACE)
        role_frame.pack(fill="x")
        for label, value in (("Traveler", "user"), ("Administrator", "admin")):
            tk.Radiobutton(role_frame, text=label, variable=self.login_role, value=value,
                           font=("Segoe UI", 11), bg=SURFACE, fg=INK,
                           selectcolor="#DBEAFE", activebackground=SURFACE,
                           padx=8, pady=7).pack(side="left", expand=True)

        create_modern_button(card, "Sign in", self.login, "primary", 38).pack(pady=(24, 12), ipady=3)
        create_modern_button(card, "Create a traveler account", self.on_signup, "outline", 38).pack(pady=(0, 14), ipady=3)
        if os.getenv("GOOGLE_CLIENT_ID"):
            tk.Label(card, text="or", font=("Segoe UI", 10), bg=SURFACE, fg=MUTED).pack(pady=(2, 8))
            create_modern_button(card, "Continue with Google", self.google_login, "outline", 38).pack(ipady=3)

        self.entry_username.bind("<Return>", lambda _event: self.login())
        self.entry_password.bind("<Return>", lambda _event: self.login())

    def login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get()
        if username == "Enter your username":
            username = ""
        if password == "Enter your password":
            password = ""
        role = self.login_role.get()
        if not username or not password:
            messagebox.showerror("Login Failed", "Please fill both Password and Username fields")
            return
        try:
            userlist = db_manager.get_user_credentials()
        except Exception as exc:
            messagebox.showerror("Database Error", f"Unable to connect to the database:\n{exc}")
            return
        if username not in userlist:
            messagebox.showerror("Login Failed", f"Username {username} does not exist!")
            return
        real_role = db_manager.get_user_role(username)
        if real_role != role:
            messagebox.showerror("Login Failed", f"{role} username {username} was not found")
            return
        if userlist[username] != password:
            messagebox.showerror("Login Failed", "Password Incorrect")
            return
        self.on_login_success(role, username)

    def google_login(self):
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        if not client_id:
            messagebox.showinfo("Google Sign-In", "Set GOOGLE_CLIENT_ID to enable Google authentication.")
            return

        state = secrets.token_urlsafe(24)
        verifier = secrets.token_urlsafe(64)
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
        result = {}

        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                query = parse_qs(urlparse(self.path).query)
                result["code"] = query.get("code", [None])[0]
                result["state"] = query.get("state", [None])[0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"<html><body style='font-family:Segoe UI;text-align:center;padding-top:80px'><h2>Sign-in complete</h2><p>You can close this window and return to VAY Travels.</p></body></html>")

            def log_message(self, _format, *_args):
                return

        try:
            server = HTTPServer(("127.0.0.1", 8765), CallbackHandler)
        except OSError as exc:
            messagebox.showerror("Google Sign-In", f"Could not open the local sign-in callback:\n{exc}")
            return

        def exchange_token():
            server.handle_request()
            if result.get("state") != state or not result.get("code"):
                self.window.after(0, lambda: messagebox.showerror("Google Sign-In", "Google authentication was cancelled or failed"))
                server.server_close()
                return
            try:
                token_response = requests.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": client_id,
                        "code": result["code"],
                        "code_verifier": verifier,
                        "grant_type": "authorization_code",
                        "redirect_uri": "http://127.0.0.1:8765/",
                    },
                    timeout=15,
                )
                token_response.raise_for_status()
                access_token = token_response.json()["access_token"]
                profile = requests.get(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=15,
                )
                profile.raise_for_status()
                google_profile = profile.json()
                email = google_profile["email"]
                username = email
                users = db_manager.get_user_credentials()
                if username not in users:
                    db_manager.insert_user(username, secrets.token_urlsafe(32), "user")
                self.window.after(0, lambda: self.on_login_success("user", username))
            except Exception as exc:
                self.window.after(0, lambda: messagebox.showerror("Google Sign-In", f"Authentication failed:\n{exc}"))
            finally:
                server.server_close()

        threading.Thread(target=exchange_token, daemon=True).start()
        params = urlencode({
            "client_id": client_id,
            "redirect_uri": "http://127.0.0.1:8765/",
            "response_type": "code",
            "scope": "openid email profile",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "state": state,
            "prompt": "select_account",
        })
        webbrowser.open(f"https://accounts.google.com/o/oauth2/v2/auth?{params}")

    def run(self):
        self.window.mainloop()

class SignupWindow:
    def __init__(self, parent, on_success):
        self.window = tk.Toplevel(parent)
        configure_modern_window(self.window, "Create your VAY account", "820x610")
        self.on_success = on_success
        self.setup_ui()

    def setup_ui(self):
        left = tk.Frame(self.window, bg=NAVY, width=280)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        tk.Label(left, text="VAY", font=("Segoe UI", 24, "bold"), bg=NAVY, fg="white").pack(padx=36, pady=(40, 4), anchor="w")
        tk.Label(left, text="TRAVELS", font=("Segoe UI", 11, "bold"), bg=NAVY, fg="#93C5FD").pack(padx=36, anchor="w")
        tk.Label(left, text="Your next\njourney starts here.",
                 font=("Segoe UI", 24, "bold"), bg=NAVY, fg="white", justify="left").pack(padx=36, pady=(100, 16), anchor="w")
        tk.Label(left, text="Create an account to save trips,\nmanage bookings, and explore India.",
                 font=("Segoe UI", 11), bg=NAVY, fg="#C9D6E5", justify="left").pack(padx=36, anchor="w")

        card = tk.Frame(self.window, bg=SURFACE)
        card.pack(side="right", fill="both", expand=True)
        form = tk.Frame(card, bg=SURFACE)
        form.place(relx=0.5, rely=0.5, anchor="center", width=390)
        tk.Label(form, text="Create account", font=("Segoe UI", 26, "bold"), bg=SURFACE, fg=INK).pack(anchor="w")
        tk.Label(form, text="Join VAY Travels in a few seconds", font=("Segoe UI", 12), bg=SURFACE, fg=MUTED).pack(anchor="w", pady=(5, 24))

        tk.Label(form, text="Username", font=("Segoe UI", 11, "bold"), bg=SURFACE, fg=INK).pack(anchor="w", pady=(0, 7))
        self.signup_username = create_entry(form, "Choose a username", width=38)
        self.signup_username.pack(ipady=10)
        tk.Label(form, text="Password", font=("Segoe UI", 11, "bold"), bg=SURFACE, fg=INK).pack(anchor="w", pady=(18, 7))
        self.signup_password = create_entry(form, "Create a password", password=True, width=38)
        self.signup_password.pack(ipady=10)

        tk.Label(form, text="Account type", font=("Segoe UI", 11, "bold"), bg=SURFACE, fg=INK).pack(anchor="w", pady=(18, 7))
        self.signup_role = tk.StringVar(value="user")
        role_frame = tk.Frame(form, bg=SURFACE)
        role_frame.pack(fill="x")
        for label, value in (("Traveler", "user"), ("Administrator", "admin")):
            tk.Radiobutton(role_frame, text=label, variable=self.signup_role, value=value,
                           font=("Segoe UI", 11), bg=SURFACE, fg=INK,
                           selectcolor="#DBEAFE", activebackground=SURFACE,
                           padx=8, pady=7).pack(side="left", expand=True)
        create_modern_button(form, "Create account", self.save_user, "success", 38).pack(pady=(24, 0), ipady=3)

    def save_user(self):
        uname = self.signup_username.get()
        pword = self.signup_password.get()
        role = self.signup_role.get()
        if uname == "Choose a username":
            uname = ""
        if pword == "Create a password":
            pword = ""
        if not uname or not pword:
            messagebox.showerror("Error", "Fields cannot be empty")
            return
        try:
            userlist = db_manager.get_user_credentials()
        except Exception as exc:
            messagebox.showerror("Database Error", f"Unable to connect to the database:\n{exc}")
            return
        if uname in userlist:
            messagebox.showerror("Error", "Username already exists!")
            return
        try:
            db_manager.insert_user(uname, pword, role)
            userlist[uname] = pword
            messagebox.showinfo("Success", "Account created successfully!")
            self.window.destroy()
            self.on_success()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

class AdminWindow:
    def __init__(self, on_logout):
        self.window = tk.Tk()
        configure_modern_window(self.window, f"{APP_TITLE} - Admin", "1280x760")
        self.on_logout = on_logout
        self.setup_ui()

    def setup_ui(self):
        sidebar = tk.Frame(self.window, bg=NAVY, width=250)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text="VAY", font=("Segoe UI", 24, "bold"), bg=NAVY, fg="white").pack(padx=28, pady=(32, 0), anchor="w")
        tk.Label(sidebar, text="TRAVELS ADMIN", font=("Segoe UI", 10, "bold"), bg=NAVY, fg="#93C5FD").pack(padx=28, anchor="w")

        nav = tk.Frame(sidebar, bg=NAVY)
        nav.pack(fill="x", pady=(42, 0), padx=14)
        nav_items = [
            ("Overview", self.show_dashboard),
            ("Search bookings", self.open_search_window),
            ("Modify bookings", self.open_modify_window),
            ("Traveler reviews", self.open_review_window),
            ("Reports", self.open_report_window),
        ]
        for label, command in nav_items:
            button = create_modern_button(nav, f"  {label}", command, "outline", 20)
            button.config(bg=NAVY, fg="#C9D6E5", activebackground="#173552")
            button.bind("<Enter>", lambda event, btn=button: btn.config(bg="#173552"))
            button.bind("<Leave>", lambda event, btn=button: btn.config(bg=NAVY))
            button.pack(fill="x", pady=3)
        create_modern_button(sidebar, "Log out", self.logout, "danger", 20).pack(side="bottom", pady=24, padx=14)

        self.main_frame = tk.Frame(self.window, bg=CANVAS)
        self.main_frame.pack(side="right", fill="both", expand=True)
        self.show_dashboard()

    def create_hover_button(self, parent, text, command, **kwargs):
        """Create a button with hover effects"""
        btn = tk.Button(parent, text=text, command=command, **kwargs)
        original_bg = kwargs.get('bg', PRIMARY_COLOR)
        btn.bind("<Enter>", lambda e: btn.config(bg=SECONDARY_COLOR))
        btn.bind("<Leave>", lambda e: btn.config(bg=original_bg))
        return btn

    def show_dashboard(self):
        """Display the admin dashboard"""
        # Clear current content
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Dashboard header
        header_frame = tk.Frame(self.main_frame, bg=BACKGROUND_COLOR)
        header_frame.pack(fill="x", padx=30, pady=20)
        tk.Label(header_frame, text="📊 Admin Dashboard", font=HEADER_FONT, bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(anchor="w")
        tk.Label(header_frame, text="Manage bookings, users, and generate reports", font=BODY_FONT, bg=BACKGROUND_COLOR, fg=TEXT_LIGHT).pack(anchor="w", pady=(5,0))

        # Stats cards with modern design
        stats_frame = tk.Frame(self.main_frame, bg=BACKGROUND_COLOR)
        stats_frame.pack(pady=30)

        # Get stats
        total_bookings = len(db_manager.get_all_bookings())
        total_users = len(db_manager.get_all_users())

        # Modern stat cards
        self.create_stat_card(stats_frame, "📅 Total Bookings", str(total_bookings), PRIMARY_COLOR).pack(side="left", padx=20)
        self.create_stat_card(stats_frame, "👥 Total Users", str(total_users), SECONDARY_COLOR).pack(side="left", padx=20)

        # Quick actions
        actions_frame = tk.Frame(self.main_frame, bg=BACKGROUND_COLOR)
        actions_frame.pack(pady=30)
        tk.Label(actions_frame, text="⚡ Quick Actions", font=SUBHEADER_FONT, bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(pady=(0,20))

        action_buttons = [
            ("📋 View All Bookings", self.view_all_bookings),
            ("📊 Generate Report", self.open_report_window),
            ("👤 Manage Users", self.manage_users)
        ]

        for text, command in action_buttons:
            self.create_hover_button(actions_frame, text, command, bg=ACCENT_COLOR, activebackground=SUCCESS_COLOR, padx=25, pady=12).pack(side="left", padx=15)

    def create_stat_card(self, parent, title, value, color):
        """Create a modern stat card"""
        card = tk.Frame(parent, bg=CARD_COLOR, bd=0, relief="flat", width=250, height=120)
        card.pack_propagate(False)

        # Color bar at top
        color_bar = tk.Frame(card, bg=color, height=8)
        color_bar.pack(fill="x")

        content = tk.Frame(card, bg=CARD_COLOR)
        content.pack(fill="both", expand=True, padx=20, pady=15)

        tk.Label(content, text=title, font=SUBHEADER_FONT, bg=CARD_COLOR, fg=TEXT_COLOR).pack(anchor="w")
        tk.Label(content, text=value, font=("Segoe UI", 36, "bold"), bg=CARD_COLOR, fg=color).pack(anchor="w", pady=(10,0))

        return card

    def view_all_bookings(self):
        # Open a window to view all bookings
        all_win = tk.Toplevel()
        configure_modern_window(all_win, "All bookings", "1000x620")
        tk.Label(all_win, text="All bookings", font=("Segoe UI", 24, "bold"), bg=CANVAS, fg=INK).pack(pady=(24, 4))
        tk.Label(all_win, text="Live reservation overview", font=("Segoe UI", 12), bg=CANVAS, fg=MUTED).pack(pady=(0, 14))
        _canvas, scroll_content, _vertical = create_scrollable_area(all_win, CANVAS, horizontal=True)
        bookings = db_manager.get_all_bookings()
        if bookings:
            columns = ["Tour ID", "Departure", "Arrival", "Date", "Days", "Persons", "Username"]
            table_frame = tk.Frame(scroll_content, bg=SURFACE, padx=12, pady=12)
            table_frame.pack(padx=24, pady=10, fill="both", expand=True)
            for col, header in enumerate(columns):
                tk.Label(table_frame, text=header, font=("Segoe UI", 11, "bold"), bg=NAVY, fg="white", padx=10, pady=8).grid(row=0, column=col, sticky="nsew")
            for row, booking in enumerate(bookings, start=1):
                row_bg = "#FFFFFF" if row % 2 else "#F8FAFC"
                for col, value in enumerate(booking):
                    tk.Label(table_frame, text=value, font=("Segoe UI", 10), bg=row_bg, fg=INK, padx=10, pady=7).grid(row=row, column=col, sticky="nsew", pady=1)
            for col in range(len(columns)):
                table_frame.columnconfigure(col, weight=1)
        else:
            empty = tk.Frame(scroll_content, bg=SURFACE)
            empty.pack(padx=50, pady=70, fill="both", expand=True)
            tk.Label(empty, text="No bookings yet", font=("Segoe UI", 20, "bold"), bg=SURFACE, fg=INK).pack(pady=(40, 6))
            tk.Label(empty, text="New reservations will appear here automatically.", bg=SURFACE, fg=MUTED).pack()
        all_win.mainloop()

    def manage_users(self):
        users = db_manager.get_all_users()
        users_win = tk.Toplevel()
        configure_modern_window(users_win, "Traveler accounts", "620x560")
        tk.Label(users_win, text="Traveler accounts", font=("Segoe UI", 24, "bold"), bg=CANVAS, fg=INK).pack(pady=(24, 4))
        tk.Label(users_win, text=f"{len(users)} registered accounts", font=("Segoe UI", 12), bg=CANVAS, fg=MUTED).pack(pady=(0, 16))
        _canvas, scroll_content, _vertical = create_scrollable_area(users_win, CANVAS)
        list_card = tk.Frame(scroll_content, bg=SURFACE, padx=12, pady=12)
        list_card.pack(padx=50, pady=10, fill="both", expand=True)
        for index, username in enumerate(users, start=1):
            row_bg = "#FFFFFF" if index % 2 else "#F8FAFC"
            tk.Label(list_card, text=f"{index:02d}", font=("Segoe UI", 11, "bold"), bg=row_bg, fg=SKY, width=6, pady=10).grid(row=index, column=0, sticky="w")
            tk.Label(list_card, text=username, font=("Segoe UI", 12), bg=row_bg, fg=INK, padx=12, pady=10).grid(row=index, column=1, sticky="ew")
            list_card.columnconfigure(1, weight=1)
        if not users:
            tk.Label(list_card, text="No registered accounts", font=("Segoe UI", 16), bg=SURFACE, fg=MUTED).pack(pady=40)

    def animate_plane(self, frame_index=0):
        if self.plane_frames:
            frame = self.plane_frames[frame_index]
            self.plane_label.config(image=frame)
            frame_index = (frame_index + 1) % len(self.plane_frames)
            self.window.after(80, self.animate_plane, frame_index)

    def open_search_window(self):
        search_win = tk.Toplevel()
        configure_modern_window(search_win, "Search bookings", "1000x620")
        tk.Label(search_win, text="Search reservations", font=("Segoe UI", 24, "bold"), bg=CANVAS, fg=INK).pack(pady=(24, 4))
        tk.Label(search_win, text="Enter a Tour ID to open its reservation details", font=("Segoe UI", 12), bg=CANVAS, fg=MUTED).pack()
        toolbar = tk.Frame(search_win, bg=SURFACE, padx=20, pady=16)
        toolbar.pack(padx=40, pady=20, fill="x")
        s_entry = create_entry(toolbar, "Tour ID", width=28)
        s_entry.pack(side="left", ipady=9)
        _canvas, scroll_content, _vertical = create_scrollable_area(search_win, CANVAS, horizontal=True)
        s_frame = tk.Frame(scroll_content, bg=SURFACE, padx=12, pady=12)
        s_frame.pack(padx=40, pady=10, fill="x")

        def search_tourid():
            tour_id = s_entry.get()
            if not tour_id:
                messagebox.showerror("Error", "Enter Tourid to be searched")
                return
            s_entry.delete(0, tk.END)
            try:
                tour_id_number = int(tour_id)
            except ValueError:
                messagebox.showerror("Error", "Enter a valid numeric Tourid")
                return
            ids = db_manager.get_all_tour_ids()
            if tour_id_number not in ids:
                messagebox.showerror("Error", "Enter a valid Tourid")
                return
            columns = ["tourid", "departure", "arrival", "traveldate", "durationdays", "persons", "username"]
            data = db_manager.get_booking_by_tourid(tour_id)
            for col, element in enumerate(columns):
                tk.Label(s_frame, text=element.upper(), font=("Segoe UI", 10, "bold"), bg=NAVY, fg="white", padx=8, pady=8).grid(row=0, column=col, padx=1, pady=1, sticky="nsew")
            for row, row_data in enumerate(data):
                for col, element in enumerate(row_data):
                    tk.Label(s_frame, text=element, font=("Segoe UI", 11), bg="#F8FAFC", fg=INK, padx=8, pady=10).grid(row=row+1, column=col, padx=1, pady=1, sticky="nsew")
            for col in range(len(columns)):
                s_frame.columnconfigure(col, weight=1)

        create_modern_button(toolbar, "Search", search_tourid, "primary", 12).pack(side="left", padx=(12, 0), ipady=2)
        s_entry.bind("<Return>", lambda _event: search_tourid())
        search_win.mainloop()

    def open_modify_window(self):
        modify_win = tk.Toplevel()
        configure_modern_window(modify_win, "Modify booking", "700x620")
        tk.Label(modify_win, text="Manage a reservation", font=("Segoe UI", 24, "bold"), bg=CANVAS, fg=INK).pack(pady=(24, 4))
        tk.Label(modify_win, text="Enter a Tour ID, then update or remove the booking", font=("Segoe UI", 12), bg=CANVAS, fg=MUTED).pack(pady=(0, 12))
        _canvas, scroll_content, _vertical = create_scrollable_area(modify_win, CANVAS)
        m_frame = tk.Frame(scroll_content, bg=SURFACE, padx=24, pady=16)
        m_frame.pack(padx=40, pady=10, fill="x")

        # Tourid
        tk.Label(m_frame, text="Tour ID:", font=("Segoe UI", 12, "bold"), bg=SURFACE, fg=INK).grid(row=0, column=0, padx=20, pady=8, sticky="e")
        id_e = tk.Entry(m_frame, width=24, font=("Segoe UI", 12), bg="#F8FAFC", relief="solid", bd=1)
        id_e.grid(row=0, column=1, padx=20, pady=10)

        # Departure
        tk.Label(m_frame, text="Departure:", font=("Segoe UI", 12, "bold"), bg=SURFACE, fg=INK).grid(row=1, column=0, pady=8, padx=20, sticky="e")
        dep_var = tk.StringVar()
        tk.OptionMenu(m_frame, dep_var, "", *CITIES).grid(row=1, column=1, padx=20, pady=8, sticky="w")

        # Arrival
        tk.Label(m_frame, text="Arrival:", font=("Segoe UI", 12, "bold"), bg=SURFACE, fg=INK).grid(row=2, column=0, pady=8, padx=20, sticky="e")
        arr_var = tk.StringVar()
        tk.OptionMenu(m_frame, arr_var, "", *CITIES).grid(row=2, column=1, padx=20, pady=8, sticky="w")

        # Date
        tk.Label(m_frame, text="Departure date:", font=("Segoe UI", 12, "bold"), bg=SURFACE, fg=INK).grid(row=3, column=0, padx=20, pady=8, sticky="e")
        date_e = tk.Entry(m_frame, width=24, font=("Segoe UI", 12), bg="#F8FAFC", relief="solid", bd=1)
        date_e.grid(row=3, column=1, padx=20, pady=10)

        # Days
        tk.Label(m_frame, text="Days:", font=("Segoe UI", 12, "bold"), bg=SURFACE, fg=INK).grid(row=4, column=0, pady=8, padx=20, sticky="e")
        days_e = tk.Entry(m_frame, width=24, font=("Segoe UI", 12), bg="#F8FAFC", relief="solid", bd=1)
        days_e.grid(row=4, column=1, padx=20, pady=10)

        # Persons
        tk.Label(m_frame, text="Persons:", font=("Segoe UI", 12, "bold"), bg=SURFACE, fg=INK).grid(row=5, column=0, pady=8, padx=20, sticky="e")
        persons_e = tk.Entry(m_frame, width=24, font=("Segoe UI", 12), bg="#F8FAFC", relief="solid", bd=1)
        persons_e.grid(row=5, column=1, padx=20, pady=10)

        def delete_record():
            d_tourid = id_e.get()
            ids = db_manager.get_all_tour_ids()
            if not d_tourid:
                messagebox.showerror("Error", "Tourid field empty, Kindly enter tourid")
                return
            try:
                d_tourid_number = int(d_tourid)
            except ValueError:
                messagebox.showerror("Error", "Enter a valid numeric Tourid")
                return
            if d_tourid_number not in ids:
                messagebox.showerror("Error", "Tourid not found, Kindly add a valid tourid")
                return
            db_manager.delete_booking(d_tourid)
            modify_win.destroy()

        def modify_record():
            m_tourid = id_e.get()
            m_dep = dep_var.get()
            m_arr = arr_var.get()
            m_date = date_e.get()
            m_days = days_e.get()
            m_persons = persons_e.get()
            currdate = db_manager.get_current_date()
            ids = db_manager.get_all_tour_ids()

            if m_dep and m_arr and m_dep == m_arr:
                messagebox.showerror("Error", "Departure and Arrival City must be different")
                return
            try:
                m_tourid_number = int(m_tourid)
            except (TypeError, ValueError):
                messagebox.showerror("Error", "Enter valid tourid")
                return
            errors = validate_date(m_date, currdate) if m_date else []
            if errors:
                messagebox.showerror("Invalid Date", errors[0])
                return
            if m_tourid_number not in ids:
                messagebox.showerror("Error", "Enter valid tourid")
                return
            if m_days:
                try:
                    days_value = int(m_days)
                    if days_value < 1:
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Error", "Days must be a positive whole number")
                    return
            if m_persons:
                try:
                    persons_value = int(m_persons)
                    if persons_value < 1:
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Error", "Persons must be a positive whole number")
                    return
            if m_dep:
                db_manager.update_booking(m_tourid, 'departure', m_dep)
            if m_arr:
                db_manager.update_booking(m_tourid, 'arrival', m_arr)
            if m_date:
                db_manager.update_booking(m_tourid, 'traveldate', m_date)
            if m_days:
                db_manager.update_booking(m_tourid, 'durationdays', days_value)
            if m_persons:
                db_manager.update_booking(m_tourid, 'persons', persons_value)
            modify_win.destroy()

        actions = tk.Frame(modify_win, bg=CANVAS)
        actions.pack(pady=12)
        create_modern_button(actions, "Save changes", modify_record, "primary", 18).pack(side="left", padx=8)
        create_modern_button(actions, "Delete booking", delete_record, "danger", 18).pack(side="left", padx=8)
        modify_win.mainloop()

    def open_review_window(self):
        read_review_win = tk.Toplevel()
        configure_modern_window(read_review_win, "Traveler reviews", "700x700")
        tk.Label(read_review_win, text="Traveler reviews", font=("Segoe UI", 24, "bold"), bg=CANVAS, fg=INK).pack(pady=(24, 4))
        tk.Label(read_review_win, text="Search feedback by username", font=("Segoe UI", 12), bg=CANVAS, fg=MUTED).pack()
        toolbar = tk.Frame(read_review_win, bg=SURFACE, padx=20, pady=16)
        toolbar.pack(padx=40, pady=20, fill="x")
        r_id = create_entry(toolbar, "Username", width=24)
        r_id.pack(side="left", ipady=9)
        _canvas, scroll_content, _vertical = create_scrollable_area(read_review_win, CANVAS)
        review_card = tk.Frame(scroll_content, bg=SURFACE, padx=12, pady=12)
        review_card.pack(padx=40, pady=(0, 20), fill="both", expand=True)
        review_box = scrolledtext.ScrolledText(review_card, wrap=tk.WORD, width=70, height=16,
                                               font=("Segoe UI", 12), bg="#F8FAFC", fg=INK,
                                               bd=0, relief="flat", padx=16, pady=16)
        review_box.pack(fill="both", expand=True)

        def search_review():
            username = r_id.get()
            if not username:
                messagebox.showerror("Error", "Enter username")
                return
            r_id.delete(0, tk.END)
            review = read_reviews(username)
            review_box.delete("1.0", tk.END)
            review_box.insert(tk.END, f"{username}\n{review}")

        create_modern_button(toolbar, "Find review", search_review, "primary", 14).pack(side="left", padx=(12, 0), ipady=2)
        r_id.bind("<Return>", lambda _event: search_review())
        read_review_win.mainloop()

    def open_report_window(self):
        report_win = tk.Toplevel()
        configure_modern_window(report_win, "Generate report", "620x520")
        tk.Label(report_win, text="Export a booking report", font=("Segoe UI", 24, "bold"), bg=CANVAS, fg=INK).pack(pady=(24, 4))
        tk.Label(report_win, text="Choose the fields you want in the CSV", font=("Segoe UI", 12), bg=CANVAS, fg=MUTED).pack(pady=(0, 16))

        _canvas, scroll_content, _vertical = create_scrollable_area(report_win, CANVAS)
        r_frame = tk.Frame(scroll_content, bg=SURFACE, padx=24, pady=18)
        r_frame.pack(padx=60, pady=10, fill="both", expand=True)

        var1 = tk.IntVar()
        var2 = tk.IntVar()
        var3 = tk.IntVar()
        var4 = tk.IntVar()
        var5 = tk.IntVar()
        var6 = tk.IntVar()
        var7 = tk.IntVar()

        report_fields = [
            ("Tour ID", var1), ("Departure", var2), ("Arrival", var3),
            ("Travel date", var4), ("Duration", var5), ("Persons", var6), ("Username", var7),
        ]
        for row, (label, variable) in enumerate(report_fields, start=1):
            tk.Checkbutton(r_frame, text=label, variable=variable, font=("Segoe UI", 12),
                           bg=SURFACE, fg=INK, selectcolor="#DBEAFE",
                           activebackground=SURFACE, padx=8, pady=6).grid(row=row, column=0, sticky="w")

        def generate():
            l = {"tourid": var1.get(), "departure": var2.get(), "arrival": var3.get(), "traveldate": var4.get(), "durationdays": var5.get(), "persons": var6.get(), "username": var7.get()}
            header = []
            field = []
            for i in l:
                if l[i]:
                    header.append(i.upper())
                    field.append(i)
            if not field:
                messagebox.showerror("Error", "Kindly check atleast one field to generate report")
                return
            data = db_manager.get_report_data(field)
            report_path = os.path.join(os.path.dirname(__file__), "report.csv")
            with open(report_path, "w", newline="", encoding="utf-8") as f:
                csvw = csv.writer(f)
                csvw.writerow(header)
                for row in data:
                    csvw.writerow(list(row))
            try:
                subprocess.Popen(["excel.exe", report_path])
            except:
                messagebox.showinfo("Report Generated", f"Report saved to {report_path}")
            report_win.destroy()

        create_modern_button(r_frame, "Generate CSV", generate, "success", 16).grid(row=3, column=2, rowspan=3, padx=30)
        report_win.mainloop()

    def logout(self):
        messagebox.showinfo("Thank You", f"Thank You for visiting {APP_TITLE}!")
        self.window.destroy()
        self.on_logout()

    def run(self):
        self.window.mainloop()

# Similarly for UserWindow - I'll add a placeholder, but it's large, so in next steps
class UserWindow:
    def __init__(self, username, on_logout):
        self.username = username
        self.window = tk.Tk()
        configure_modern_window(self.window, f"{APP_TITLE} - Traveler", "1280x760")
        self.on_logout = on_logout
        self.setup_ui()

    def setup_ui(self):
        # Create sidebar
        self.sidebar = tk.Frame(self.window, bg=NAVY, width=250)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Sidebar header
        sidebar_header = tk.Frame(self.sidebar, bg=NAVY, height=80)
        sidebar_header.pack(fill="x")
        tk.Label(sidebar_header, text="VAY TRAVELS", font=("Segoe UI", 16, "bold"), bg=NAVY, fg="white").pack(pady=20)

        # Sidebar navigation buttons
        nav_buttons = [
            ("🏠 Home", self.show_home),
            ("📅 Book Trip", self.open_make_booking_window),
            ("📋 My Bookings", self.open_booking_history_window),
            ("⭐ Reviews", self.open_write_review_window),
            ("ℹ️ About", self.open_about_us_window),
            ("📞 Contact", self.open_contact_us_window)
        ]

        self.nav_frame = tk.Frame(self.sidebar, bg=NAVY)
        self.nav_frame.pack(fill="x", pady=20)

        self.current_page = "Home"  # Track current page

        for text, command in nav_buttons:
            btn = self.create_sidebar_button(text, command)
            btn.pack(fill="x", padx=10, pady=2)

        # Logout button at bottom
        logout_frame = tk.Frame(self.sidebar, bg=NAVY)
        logout_frame.pack(side="bottom", fill="x", pady=20)
        self.create_sidebar_button("🚪 Logout", self.logout).pack(fill="x", padx=10)

        # Main content area
        self.main_frame = tk.Frame(self.window, bg=CANVAS)
        self.main_frame.pack(side="right", fill="both", expand=True)

        # Top banner for main content
        self.top_banner = tk.Frame(self.main_frame, bg="white", height=60, relief="raised", bd=1)
        self.top_banner.pack(fill="x")
        self.page_title = tk.Label(self.top_banner, text="🏠 Home", font=HEADER_FONT, bg="white", fg=TEXT_COLOR)
        self.page_title.pack(side="left", padx=30, pady=15)

        # Content frame
        self.content_frame = tk.Frame(self.main_frame, bg=BACKGROUND_COLOR)
        self.content_frame.pack(fill="both", expand=True)

        # Show home by default
        self.show_home()

    def create_sidebar_button(self, text, command):
        """Create a sidebar navigation button"""
        btn = tk.Button(self.nav_frame, text=text, font=BUTTON_FONT, bg=NAVY, fg="#C9D6E5",
                       activebackground="#173552", activeforeground="white", bd=0,
                       cursor="hand2", relief="flat", anchor="w", padx=20, pady=12, command=command)

        # Hover effects
        def on_enter(e):
            if self.current_page not in text:
                btn.config(bg="#173552")

        def on_leave(e):
            if self.current_page not in text:
                btn.config(bg=NAVY)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def update_sidebar_selection(self, page_name):
        """Update sidebar button selection"""
        self.current_page = page_name
        self.page_title.config(text=f"{page_name}")

        # Update button colors
        for child in self.nav_frame.winfo_children():
            if isinstance(child, tk.Button):
                if page_name in child.cget("text"):
                    child.config(bg="#173552")
                else:
                    child.config(bg=NAVY)

    def create_hover_button(self, parent, text, command, **kwargs):
        """Create a button with hover effects"""
        btn = tk.Button(parent, text=text, command=command, **kwargs)
        btn.bind("<Enter>", lambda e: btn.config(bg=SECONDARY_COLOR))
        btn.bind("<Leave>", lambda e: btn.config(bg=kwargs.get('bg', PRIMARY_COLOR)))
        return btn

    def show_home(self):
        """Display the home dashboard"""
        self.update_sidebar_selection("🏠 Home")

        # Clear current content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Welcome message
        welcome_frame = tk.Frame(self.content_frame, bg=BACKGROUND_COLOR)
        welcome_frame.pack(fill="x", padx=30, pady=20)
        tk.Label(welcome_frame, text=f"Welcome back, {self.username}!", font=HEADER_FONT, bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(anchor="w")
        tk.Label(welcome_frame, text="Discover your next adventure", font=SUBHEADER_FONT, bg=BACKGROUND_COLOR, fg=TEXT_LIGHT).pack(anchor="w", pady=(5,0))

        # Search bar with modern styling
        search_frame = tk.Frame(self.content_frame, bg=CARD_COLOR, pady=10, padx=25, relief="raised", bd=1)
        search_frame.pack(fill="x", padx=30, pady=5)

        tk.Label(search_frame, text="✈️ Where do you want to go?", font=HEADER_FONT, bg=CARD_COLOR, fg=TEXT_COLOR).pack(pady=(0,5))
        search_entry = tk.Entry(search_frame, font=BODY_FONT, width=50, bd=2, relief="solid", highlightthickness=1, highlightcolor=PRIMARY_COLOR)
        search_entry.pack(pady=1, ipady=3)

        # Create suggestions listbox (initially hidden)
        self.suggestions_listbox = tk.Listbox(search_frame, font=BODY_FONT, height=5, bg="white", fg=TEXT_COLOR,
                                            selectbackground=PRIMARY_COLOR, selectforeground="white",
                                            relief="flat", bd=1, highlightthickness=1, highlightcolor=PRIMARY_COLOR)
        self.suggestions_listbox.pack_forget()  # Initially hidden

        # Bind events to search entry
        search_entry.bind('<KeyRelease>', self.on_search_key_release)
        search_entry.bind('<Return>', lambda e: self.search_destination(search_entry.get()))
        search_entry.bind('<Escape>', self.hide_suggestions)
        search_entry.bind('<Button-1>', lambda e: self.hide_suggestions())  # Hide when clicking on entry

        # Bind listbox selection
        self.suggestions_listbox.bind('<<ListboxSelect>>', self.on_suggestion_select)
        self.suggestions_listbox.bind('<Return>', self.on_suggestion_select)
        self.suggestions_listbox.bind('<Escape>', self.hide_suggestions)

        search_btn = self.create_hover_button(search_frame, "🔍 Search", lambda: self.search_destination(search_entry.get()),
                                            bg=ACCENT_COLOR, activebackground=SUCCESS_COLOR, padx=20, pady=6)
        search_btn.pack(pady=3)

        # Featured destinations with modern cards
        featured_frame = tk.Frame(self.content_frame, bg=BACKGROUND_COLOR)
        featured_frame.pack(fill="both", expand=True, padx=30, pady=20)

        tk.Label(featured_frame, text="🌟 Popular Destinations", font=HEADER_FONT, bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(pady=(0,25))

        # Create modern destination cards in a responsive grid
        destinations = [
            {"name": "Delhi", "image": os.path.join(os.path.dirname(__file__), "Delhi.jpg"), "desc": "Historical & Cultural Hub"},
            {"name": "Mumbai", "image": os.path.join(os.path.dirname(__file__), "Mumbai.jpg"), "desc": "City of Dreams"},
            {"name": "Bangalore", "image": os.path.join(os.path.dirname(__file__), "Bangalore.jpg"), "desc": "Silicon Valley of India"},
            {"name": "Chennai", "image": os.path.join(os.path.dirname(__file__), "Chennai.jpg"), "desc": "Coastal Metropolitan"},
            {"name": "Kolkata", "image": os.path.join(os.path.dirname(__file__), "Kolkata.jpg"), "desc": "Cultural Capital"}
        ]

        # Create a canvas with scrollbar for responsive layout
        canvas_frame = tk.Frame(featured_frame, bg=BACKGROUND_COLOR)
        canvas_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(canvas_frame, bg=BACKGROUND_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
        scrollable_frame = tk.Frame(canvas, bg=BACKGROUND_COLOR)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="top", fill="both", expand=True)
        scrollbar.pack(side="bottom", fill="x")

        # Create destination cards in the scrollable frame
        for i, dest in enumerate(destinations):
            card = self.create_destination_card(scrollable_frame, dest)
            card.grid(row=0, column=i, padx=15, pady=10, sticky="n")

    def on_search_key_release(self, event):
        """Handle key release in search entry for Google-like suggestions"""
        # Skip certain keys that shouldn't trigger search
        if event.keysym in ['Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R', 'Caps_Lock']:
            return

        query = event.widget.get().strip().lower()

        # Clear previous suggestions
        self.suggestions_listbox.delete(0, tk.END)

        if query:
            # Filter cities that match the query
            matching_cities = [city for city in CITIES if query in city.lower()]

            if matching_cities:
                # Show suggestions
                for city in matching_cities[:5]:  # Limit to 5 suggestions
                    self.suggestions_listbox.insert(tk.END, city)

                # Position and show the listbox below the search entry
                self.suggestions_listbox.pack(after=event.widget, pady=(0, 0))
                self.suggestions_listbox.lift()  # Bring to front
            else:
                # No matches, hide suggestions
                self.suggestions_listbox.pack_forget()
        else:
            # Empty query, hide suggestions
            self.suggestions_listbox.pack_forget()

    def hide_suggestions(self, event=None):
        """Hide the suggestions listbox"""
        try:
            self.suggestions_listbox.pack_forget()
        except:
            pass  # Listbox might already be hidden

    def on_suggestion_select(self, event=None):
        """Handle selection from suggestions listbox"""
        selection = self.suggestions_listbox.curselection()
        if selection:
            selected_city = self.suggestions_listbox.get(selection[0])
            # Find the search entry in the search frame
            search_frame = self.suggestions_listbox.master  # Parent of listbox is search_frame
            for widget in search_frame.winfo_children():
                if isinstance(widget, tk.Entry):
                    widget.delete(0, tk.END)
                    widget.insert(0, selected_city)
                    self.hide_suggestions()
                    self.search_destination(selected_city)
                    return

    def search_destination(self, query):
        """Handle destination search"""
        self.hide_suggestions()

        if query.strip():
            # Check if the query matches any city
            matching_cities = [city for city in CITIES if query.lower() in city.lower()]

            if matching_cities:
                # If exact match, go to booking
                if query.title() in CITIES:
                    self.quick_book(query.title())
                else:
                    # Show first matching city
                    self.quick_book(matching_cities[0])
            else:
                # No matches found - just show a brief message
                show_toast(self.window, f"No destinations found for '{query}'", toast_type="warning")
        else:
            show_toast(self.window, "Please enter a destination", toast_type="info")

    def create_destination_card(self, parent, dest_data):
        """Create a modern destination card with landmark image and hover effects"""
        card = tk.Frame(parent, bg=CARD_COLOR, bd=0, relief="flat", width=160, height=140)
        card.pack_propagate(False)
        card.grid_propagate(False)

        # Load and display landmark image
        try:
            image = Image.open(dest_data["image"])
            image = image.resize((140, 70), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)

            # Keep a reference to prevent garbage collection
            if not hasattr(self, 'image_refs'):
                self.image_refs = []
            self.image_refs.append(photo)

            image_label = tk.Label(card, image=photo, bg=CARD_COLOR)
            image_label.pack(pady=(5, 2))

        except Exception as e:
            # Fallback to emoji if image fails to load
            image_label = tk.Label(card, text="🏛️", font=("Segoe UI", 30), bg=CARD_COLOR)
            image_label.pack(pady=(10, 2))
            print(f"Failed to load image {dest_data['image']}: {e}")

        # City name
        name_label = tk.Label(card, text=dest_data["name"], font=SUBHEADER_FONT, bg=CARD_COLOR, fg=TEXT_COLOR)
        name_label.pack(pady=(0, 2))

        # Description
        desc_label = tk.Label(card, text=dest_data["desc"], font=SMALL_FONT, bg=CARD_COLOR, fg=TEXT_LIGHT, wraplength=140, justify="center")
        desc_label.pack(pady=(0, 8))

        # Hover effects for the entire card
        def on_enter(e):
            card.config(bg="#F1F5F9")  # Light blue tint
            image_label.config(bg="#F1F5F9")
            name_label.config(bg="#F1F5F9")
            desc_label.config(bg="#F1F5F9")

        def on_leave(e):
            card.config(bg=CARD_COLOR)
            image_label.config(bg=CARD_COLOR)
            name_label.config(bg=CARD_COLOR)
            desc_label.config(bg=CARD_COLOR)

        # Make entire card clickable
        def on_click(e):
            self.quick_book(dest_data["name"])

        # Bind hover and click events to all elements
        for widget in [card, image_label, name_label, desc_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)

        # Add cursor change on hover
        card.config(cursor="hand2")

        return card

    def quick_book(self, destination):
        # Open booking window with destination pre-selected
        self.open_make_booking_window(arrival=destination)

    def open_booking_history_window(self):
        self.update_sidebar_selection("📋 My Bookings")
        bookings = db_manager.get_user_bookings(self.username)
        history_win = tk.Toplevel()
        configure_modern_window(history_win, "Booking history", "900x620")
        tk.Label(history_win, text="Your bookings", font=("Segoe UI", 24, "bold"), bg=CANVAS, fg=INK).pack(pady=(24, 4))
        tk.Label(history_win, text="A quick view of every trip you have planned", font=("Segoe UI", 12), bg=CANVAS, fg=MUTED).pack(pady=(0, 16))
        _canvas, scroll_content, _vertical = create_scrollable_area(history_win, CANVAS, horizontal=True)
        table_card = tk.Frame(scroll_content, bg=SURFACE, padx=12, pady=12)
        table_card.pack(padx=24, pady=10, fill="both", expand=True)
        headers = ["Departure City", "Arrival City", "Departure Date", "No. of Days", "No. of People"]
        for col, text in enumerate(headers):
            tk.Label(table_card, text=text, font=("Segoe UI", 10, "bold"), bg=NAVY, fg="white", padx=8, pady=8).grid(row=0, column=col, sticky="nsew", padx=1, pady=1)
        for row_index, row_data in enumerate(bookings, start=2):
            row_bg = "#FFFFFF" if row_index % 2 else "#F8FAFC"
            for col_index, cell_data in enumerate(row_data):
                tk.Label(table_card, text=cell_data, font=("Segoe UI", 11), bg=row_bg, fg=INK, padx=8, pady=10).grid(row=row_index, column=col_index, sticky="nsew", padx=1, pady=1)
        if not bookings:
            tk.Label(table_card, text="No previous bookings yet", font=("Segoe UI", 18, "bold"), bg=SURFACE, fg=INK).grid(row=2, column=0, columnspan=5, pady=60)
            tk.Label(table_card, text="Plan a new trip to see it appear here.", bg=SURFACE, fg=MUTED).grid(row=3, column=0, columnspan=5)
        for col in range(5):
            table_card.columnconfigure(col, weight=1)
        history_win.mainloop()

    def open_about_us_window(self):
        self.update_sidebar_selection("ℹ️ About")
        about_win = tk.Toplevel(self.window)
        configure_modern_window(about_win, "About VAY Travels", "600x500")
        tk.Label(about_win, text="About VAY Travels", font=("Segoe UI", 24, "bold"), bg=CANVAS, fg=INK).pack(pady=(24, 14))
        _canvas, scroll_content, _vertical = create_scrollable_area(about_win, CANVAS)
        card = tk.Frame(scroll_content, bg=SURFACE, padx=28, pady=24)
        card.pack(padx=50, pady=10, fill="both", expand=True)
        tk.Label(card, text="Travel made simple", font=("Segoe UI", 18, "bold"), bg=SURFACE, fg=SKY).pack(anchor="w")
        tk.Label(card, text="VAY Travels brings destination discovery, hotel selection,\nflight choices, and booking management into one easy experience.",
                 font=("Segoe UI", 12), bg=SURFACE, fg=INK, justify="left").pack(anchor="w", pady=(12, 24))
        for title, detail in (("Curated stays", "A range of trusted hotels for every budget"),
                              ("Simple planning", "Clear trip details and transparent pricing"),
                              ("Traveler support", "Friendly help before and after your journey")):
            row = tk.Frame(card, bg="#F8FAFC")
            row.pack(fill="x", pady=4)
            tk.Label(row, text=title, font=("Segoe UI", 11, "bold"), bg="#F8FAFC", fg=INK, width=18, pady=10).pack(side="left")
            tk.Label(row, text=detail, font=("Segoe UI", 11), bg="#F8FAFC", fg=MUTED).pack(side="left", padx=10)
        about_win.mainloop()

    def open_contact_us_window(self):
        self.update_sidebar_selection("📞 Contact")
        contact_win = tk.Toplevel(self.window)
        configure_modern_window(contact_win, "Contact VAY Travels", "600x420")
        tk.Label(contact_win, text="Contact VAY", font=("Segoe UI", 24, "bold"), bg=CANVAS, fg=INK).pack(pady=(24, 14))
        _canvas, scroll_content, _vertical = create_scrollable_area(contact_win, CANVAS)
        card = tk.Frame(scroll_content, bg=SURFACE, padx=24, pady=18)
        card.pack(padx=50, pady=10, fill="both", expand=True)
        contacts = [
            ("Phone", "+91 98765 43210"),
            ("Email", "support@vaytravels.com"),
            ("Office", "123 Travel Street, New Delhi"),
            ("Hours", "Monday to Saturday, 9 AM - 6 PM"),
        ]
        for label, value in contacts:
            row = tk.Frame(card, bg="#F8FAFC")
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label, font=("Segoe UI", 11, "bold"), bg="#F8FAFC", fg=SKY, width=12, pady=12).pack(side="left")
            tk.Label(row, text=value, font=("Segoe UI", 11), bg="#F8FAFC", fg=INK).pack(side="left", padx=10)
        contact_win.mainloop()

    def open_make_booking_window(self, arrival=None):
        self.update_sidebar_selection("📅 Book Trip")

        booking_win = tk.Toplevel(self.window)
        configure_modern_window(booking_win, "Plan your trip", "900x720")
        tk.Label(booking_win, text="Plan your trip", font=("Segoe UI", 24, "bold"), bg=CANVAS, fg=INK).pack(pady=(24, 4))
        tk.Label(booking_win, text="Choose your route and travel details", font=("Segoe UI", 12), bg=CANVAS, fg=MUTED).pack(pady=(0, 12))

        _canvas, scroll_content, _vertical = create_scrollable_area(booking_win, CANVAS)
        form_frame = tk.Frame(scroll_content, bg=SURFACE, padx=28, pady=18)
        form_frame.pack(pady=10, padx=40, fill="x")

        # Departure City
        tk.Label(form_frame, text="Departure City:", font=("Helvetica", 14), bg=SURFACE, fg=INK).grid(row=0, column=0, sticky="e", pady=10, padx=10)
        departure_city_var = tk.StringVar()
        create_choice_cards(form_frame, departure_city_var, CITIES, columns=4).grid(row=0, column=1, pady=4)

        # Arrival City
        tk.Label(form_frame, text="Arrival City:", font=("Helvetica", 14), bg=SURFACE, fg=INK).grid(row=1, column=0, sticky="e", pady=10, padx=10)
        arrival_city_var = tk.StringVar(value=arrival if arrival else "")
        create_choice_cards(form_frame, arrival_city_var, CITIES, columns=4).grid(row=1, column=1, pady=4)

        # Departure Date
        tk.Label(form_frame, text="Departure Date:", font=("Helvetica", 14), bg=SURFACE, fg=INK).grid(row=2, column=0, sticky="e", pady=10, padx=10)
        departure_date_entry = DateEntry(form_frame, font=("Helvetica", 12), date_pattern='yyyy-mm-dd', locale='en_US', showweeknumbers=False, firstweekday='sunday')
        departure_date_entry.grid(row=2, column=1)

        # Number of Days
        tk.Label(form_frame, text="Number of Days:", font=("Helvetica", 14), bg=SURFACE, fg=INK).grid(row=3, column=0, sticky="e", pady=10, padx=10)
        num_days_entry = tk.Entry(form_frame, font=("Helvetica", 12))
        num_days_entry.grid(row=3, column=1)

        # Number of People
        tk.Label(form_frame, text="Number of People:", font=("Helvetica", 14), bg=SURFACE, fg=INK).grid(row=4, column=0, sticky="e", pady=10, padx=10)
        people_frame = tk.Frame(form_frame, bg=SURFACE)
        people_frame.grid(row=4, column=1)
        num_people = tk.IntVar(value=1)
        tk.Button(people_frame, text="-", command=lambda: num_people.set(max(1, num_people.get() - 1)), font=("Helvetica", 12), width=3).pack(side="left", padx=5)
        tk.Label(people_frame, textvariable=num_people, font=("Helvetica", 12), width=5, bg=SURFACE).pack(side="left")
        tk.Button(people_frame, text="+", command=lambda: num_people.set(num_people.get() + 1), font=("Helvetica", 12), width=3).pack(side="left", padx=5)

        def get_values():
            departure = departure_city_var.get()
            arrival = arrival_city_var.get()
            date = departure_date_entry.get()
            days = num_days_entry.get()
            people = num_people.get()
            if not departure or not arrival:
                messagebox.showerror("Submission Error", "Please select departure and arrival cities")
                return
            try:
                days_value = int(days)
                if days_value < 1:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Submission Error", "Number of Days must be a positive whole number")
                return
            currdate = db_manager.get_current_date()

            if departure == arrival:
                messagebox.showerror("Submission Error", "Departure and Arrival City must be different")
                return
            errors = validate_date(date, currdate)
            if errors:
                messagebox.showerror("Invalid Date", errors[0])
                return
            tourid = db_manager.get_next_tourid()
            db_manager.insert_booking(tourid, departure, arrival, date, days_value, people, self.username)
            booking_win.destroy()
            self.open_hotel_window(tourid, departure, arrival, num_people.get())

        create_modern_button(booking_win, "Continue", get_values, "primary", 22).pack(pady=20, ipady=4)
        booking_win.mainloop()

    def open_hotel_window(self, tourid, departure, arrival, num_people):
        hotel_win = tk.Toplevel()
        configure_modern_window(hotel_win, "Stay and flights", "920x760")
        tk.Label(hotel_win, text="Choose your stay", font=("Segoe UI", 24, "bold"), bg=CANVAS, fg=INK).pack(pady=(24, 4))
        tk.Label(hotel_win, text=f"{departure} to {arrival}", font=("Segoe UI", 12), bg=CANVAS, fg=MUTED).pack(pady=(0, 12))

        _canvas, scroll_content, _vertical = create_scrollable_area(hotel_win, CANVAS)
        form_frame = tk.Frame(scroll_content, bg=SURFACE, padx=28, pady=18)
        form_frame.pack(pady=10, padx=40, fill="both", expand=True)

        # Hotel
        tk.Label(form_frame, text="Hotel:", font=("Helvetica", 14), bg=SURFACE, fg=INK).grid(row=0, column=0, sticky="e", pady=10, padx=10)
        hotel_var = tk.StringVar()
        hotel_options = HOTELS_BY_CITY.get(arrival, [])
        create_choice_cards(form_frame, hotel_var, hotel_options, columns=2).grid(row=0, column=1, pady=4)

        # Flights
        tk.Label(form_frame, text="Departure Flight:", font=("Helvetica", 14), bg=SURFACE, fg=INK).grid(row=1, column=0, sticky="e", pady=10, padx=10)
        dep_flight_var = tk.StringVar()
        create_choice_cards(form_frame, dep_flight_var, FLIGHTS, columns=2).grid(row=1, column=1, pady=4)

        tk.Label(form_frame, text="Arrival Flight:", font=("Helvetica", 14), bg=SURFACE, fg=INK).grid(row=2, column=0, sticky="e", pady=10, padx=10)
        arr_flight_var = tk.StringVar()
        create_choice_cards(form_frame, arr_flight_var, FLIGHTS, columns=2).grid(row=2, column=1, pady=4)

        def submit_booking():
            hotel = hotel_var.get()
            depflight = dep_flight_var.get()
            arrflight = arr_flight_var.get()
            if not all([hotel, depflight, arrflight]):
                messagebox.showerror("Missing Information", "Please select a hotel and flights.")
                return
            db_manager.insert_hotel_flight(hotel, depflight, arrflight, tourid)
            hotel_win.destroy()
            self.open_price_window(departure, arrival, hotel, num_people)

        create_modern_button(hotel_win, "Review trip", submit_booking, "primary", 22).pack(pady=24)
        hotel_win.mainloop()

    def open_price_window(self, departure, arrival, hotel, num_people):
        dep_coords = db_manager.get_coordinates(departure)
        arr_coords = db_manager.get_coordinates(arrival)
        if not dep_coords or not arr_coords:
            messagebox.showerror("Error", "Coordinates not found")
            return
        distance = calculate_distance(dep_coords[0], dep_coords[1], arr_coords[0], arr_coords[1])
        hotel_price = int(hotel.split('Rs')[-1])
        price = calculate_price(distance, num_people, hotel_price)

        price_win = tk.Toplevel()
        configure_modern_window(price_win, "Trip summary", "560x480")
        tk.Label(price_win, text="Trip summary", font=("Segoe UI", 24, "bold"), bg=CANVAS, fg=INK).pack(pady=(24, 16))
        _canvas, scroll_content, _vertical = create_scrollable_area(price_win, CANVAS)
        card = tk.Frame(scroll_content, bg=SURFACE, padx=24, pady=20)
        card.pack(fill="x", padx=36)
        tk.Label(card, text=f"{departure}  →  {arrival}", font=("Segoe UI", 18, "bold"), bg=SURFACE, fg=INK).pack(anchor="w")
        tk.Label(card, text=f"{hotel}  •  {num_people} {'traveler' if num_people == 1 else 'travelers'}", font=("Segoe UI", 12), bg=SURFACE, fg=MUTED).pack(anchor="w", pady=(8, 16))
        tk.Label(card, text="Total payable", font=("Segoe UI", 11, "bold"), bg=SURFACE, fg=MUTED).pack(anchor="w")
        tk.Label(card, text=f"₹{price:,}", font=("Segoe UI", 30, "bold"), bg=SURFACE, fg=SKY).pack(anchor="w")
        create_modern_button(price_win, "Continue to payment", lambda: self.payment_window(price_win, price, departure, arrival, hotel, num_people), "coral", 26).pack(pady=24)
        price_win.mainloop()

    def payment_window(self, parent, price, departure, arrival, hotel, num_people):
        parent.destroy()
        pay_win = tk.Toplevel()
        configure_modern_window(pay_win, "Secure checkout", "760x620")

        header = tk.Frame(pay_win, bg=SURFACE, height=76)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="VAY Travels", font=("Segoe UI", 15, "bold"), bg=SURFACE, fg=INK).pack(side="left", padx=28)
        tk.Label(header, text="🔒 Secure checkout", font=("Segoe UI", 11), bg=SURFACE, fg=MUTED).pack(side="right", padx=28)

        _canvas, scroll_content, _vertical = create_scrollable_area(pay_win, CANVAS)
        columns = tk.Frame(scroll_content, bg=CANVAS)
        columns.pack(fill="both", expand=True, padx=28, pady=24)

        left = tk.Frame(columns, bg=SURFACE, padx=24, pady=22)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))

        right = tk.Frame(columns, bg=SURFACE, padx=20, pady=20)
        right.pack(side="right", fill="y", padx=(12, 0), ipadx=8)
        right.configure(width=230)

        tk.Label(left, text="Choose payment method", font=("Segoe UI", 18, "bold"), bg=SURFACE, fg=INK).pack(anchor="w")

        method_var = tk.StringVar(value="Card")
        method_row = tk.Frame(left, bg=SURFACE)
        method_row.pack(fill="x", pady=(14, 18))
        for method in ("Card", "UPI"):
            tk.Radiobutton(method_row, text=method, variable=method_var, value=method,
                           indicatoron=False, cursor="hand2", font=("Segoe UI", 11, "bold"),
                           bg="#F8FAFC", fg=INK, selectcolor="#DBEAFE",
                           activebackground="#EFF6FF", activeforeground=INK,
                           bd=1, relief="solid", padx=18, pady=9, width=12).pack(side="left", padx=(0, 8))

        card_form = tk.Frame(left, bg=SURFACE)
        upi_form = tk.Frame(left, bg=SURFACE)

        tk.Label(card_form, text="Name on card", font=("Segoe UI", 10, "bold"), bg=SURFACE, fg=INK).pack(anchor="w")
        self.card_name_entry = create_entry(card_form, "Enter name", width=38)
        self.card_name_entry.pack(pady=(6, 12), ipady=7)

        tk.Label(card_form, text="Card number", font=("Segoe UI", 10, "bold"), bg=SURFACE, fg=INK).pack(anchor="w")
        self.card_number_entry = create_entry(card_form, "1234 5678 9012 3456", width=38)
        self.card_number_entry.pack(pady=(6, 12), ipady=7)

        def format_card_number(_event=None):
            if self.card_number_entry.get() == "1234 5678 9012 3456":
                return
            digits = "".join(char for char in self.card_number_entry.get() if char.isdigit())[:16]
            formatted = " ".join(digits[index:index + 4] for index in range(0, len(digits), 4))
            if self.card_number_entry.get() != formatted:
                self.card_number_entry.delete(0, tk.END)
                self.card_number_entry.insert(0, formatted)

        def format_expiry(_event=None):
            if self.expiry_entry.get() == "MM/YY":
                return
            digits = "".join(char for char in self.expiry_entry.get() if char.isdigit())[:4]
            formatted = digits if len(digits) < 3 else f"{digits[:2]}/{digits[2:]}"
            if self.expiry_entry.get() != formatted:
                self.expiry_entry.delete(0, tk.END)
                self.expiry_entry.insert(0, formatted)

        def format_cvv(_event=None):
            if self.cvv_entry.get() == "•••":
                return
            digits = "".join(char for char in self.cvv_entry.get() if char.isdigit())[:4]
            if self.cvv_entry.get() != digits:
                self.cvv_entry.delete(0, tk.END)
                self.cvv_entry.insert(0, digits)

        self.card_number_entry.bind("<KeyRelease>", format_card_number)

        card_details = tk.Frame(card_form, bg=SURFACE)
        card_details.pack(fill="x")
        expiry_group = tk.Frame(card_details, bg=SURFACE)
        expiry_group.pack(side="left")
        tk.Label(expiry_group, text="Expiry date", font=("Segoe UI", 10, "bold"), bg=SURFACE, fg=INK).pack(anchor="w")
        self.expiry_entry = create_entry(expiry_group, "MM/YY", width=14)
        self.expiry_entry.pack(pady=(6, 0), ipady=7)

        cvv_group = tk.Frame(card_details, bg=SURFACE)
        cvv_group.pack(side="right")
        tk.Label(cvv_group, text="CVV", font=("Segoe UI", 10, "bold"), bg=SURFACE, fg=INK).pack(anchor="w")
        self.cvv_entry = create_entry(cvv_group, "•••", password=True, width=12)
        self.cvv_entry.pack(pady=(6, 0), ipady=7)
        self.expiry_entry.bind("<KeyRelease>", format_expiry)
        self.cvv_entry.bind("<KeyRelease>", format_cvv)

        tk.Label(upi_form, text="UPI ID", font=("Segoe UI", 10, "bold"), bg=SURFACE, fg=INK).pack(anchor="w")
        self.upi_entry = create_entry(upi_form, "name@bank", width=38)
        self.upi_entry.pack(pady=(6, 12), ipady=7)
        tk.Label(upi_form, text="Use your preferred UPI app or enter a valid UPI ID.",
                 font=("Segoe UI", 10), bg=SURFACE, fg=MUTED, wraplength=380).pack(anchor="w")

        def switch_method(*_args):
            card_form.pack_forget()
            upi_form.pack_forget()
            if method_var.get() == "Card":
                card_form.pack(fill="x")
            else:
                upi_form.pack(fill="x")

        method_var.trace_add("write", switch_method)
        switch_method()

        tk.Label(right, text="Booking summary", font=("Segoe UI", 14, "bold"), bg=SURFACE, fg=INK).pack(anchor="w")
        tk.Label(right, text=f"{departure} → {arrival}", font=("Segoe UI", 11, "bold"),
                 bg=SURFACE, fg=INK, wraplength=210).pack(anchor="w", pady=(14, 6))
        tk.Label(right, text=f"{hotel}\n{num_people} {'traveler' if num_people == 1 else 'travelers'}",
                 font=("Segoe UI", 10), bg=SURFACE, fg=MUTED, justify="left").pack(anchor="w")
        tk.Frame(right, bg=BORDER, height=1).pack(fill="x", pady=16)
        tk.Label(right, text="Total payable", font=("Segoe UI", 10, "bold"), bg=SURFACE, fg=MUTED).pack(anchor="w")
        tk.Label(right, text=f"₹{price:,}", font=("Segoe UI", 24, "bold"), bg=SURFACE, fg=SKY).pack(anchor="w", pady=(4, 14))

        def complete_selected_payment():
            if method_var.get() == "Card":
                name = self.card_name_entry.get()
                number = self.card_number_entry.get().replace(" ", "")
                expiry = self.expiry_entry.get()
                cvv = self.cvv_entry.get()
                if name in ("", "Enter name") or len(number) < 12 or expiry in ("", "MM/YY") or not cvv:
                    messagebox.showerror("Payment details", "Please enter valid card details.")
                    return
            else:
                upi = self.upi_entry.get()
                if upi in ("", "name@bank") or "@" not in upi:
                    messagebox.showerror("Payment details", "Please enter a valid UPI ID.")
                    return
            self.complete_payment(pay_win)

        create_modern_button(right, f"Pay ₹{price:,}", complete_selected_payment, "success", 18).pack(fill="x", ipady=4)
        tk.Label(right, text="Powered by VAY Secure", font=("Segoe UI", 9), bg=SURFACE, fg=MUTED).pack(pady=(10, 0))
        pay_win.mainloop()

    def complete_payment(self, pay_win):
        pay_win.destroy()
        messagebox.showinfo("Success", f"Booking successful! Thank you for choosing {APP_TITLE}!")

    def open_write_review_window(self):
        self.update_sidebar_selection("⭐ Reviews")

        review_win = tk.Toplevel()
        configure_modern_window(review_win, "Share a review", "560x460")
        tk.Label(review_win, text="How was your journey?", font=("Segoe UI", 22, "bold"), bg=CANVAS, fg=INK).pack(pady=(24, 4))
        tk.Label(review_win, text="Your feedback helps future travelers.", font=("Segoe UI", 12), bg=CANVAS, fg=MUTED).pack(pady=(0, 12))
        _canvas, scroll_content, _vertical = create_scrollable_area(review_win, CANVAS)
        text_box = tk.Text(scroll_content, wrap="word", font=("Helvetica", 12), width=50, height=12,
                            bg=SURFACE, fg=INK, bd=1, relief="solid",
                            highlightthickness=1, highlightbackground=BORDER,
                            highlightcolor=SKY)
        text_box.pack(padx=36, pady=10, fill="both", expand=True)
        create_modern_button(review_win, "Submit review", lambda: self.submit_review(review_win, text_box), "primary", 24).pack(pady=16)
        review_win.mainloop()

    def submit_review(self, review_win, text_box):
        review = text_box.get("1.0", tk.END).strip()
        if not review:
            messagebox.showwarning("Empty Review", "Please write something.")
            return
        currdate = db_manager.get_current_date()
        write_review(self.username, currdate, review)
        messagebox.showinfo("Thank You", "Your review has been submitted!")
        review_win.destroy()

    def logout(self):
        messagebox.showinfo("Thank You", f"Thank You for visiting {APP_TITLE}!")
        self.window.destroy()
        self.on_logout()

    def run(self):
        self.window.mainloop()