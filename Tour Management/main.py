# main.py - Entry point for VAY Travels

from ui import LoginWindow, SignupWindow, AdminWindow, UserWindow

def main():
    def on_login_success(role, username):
        login_window.window.destroy()
        if role == "admin":
            admin_win = AdminWindow(on_logout)
            admin_win.run()
        elif role == "user":
            user_win = UserWindow(username, on_logout)
            user_win.run()

    def on_signup():
        SignupWindow(login_window.window, lambda: None)

    def on_logout():
        main()  # Restart login

    login_window = LoginWindow(on_login_success, on_signup)
    login_window.run()

if __name__ == "__main__":
    main()