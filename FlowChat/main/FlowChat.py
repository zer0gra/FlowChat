import socket
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog

class ChatApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FlowChat")
        self.root.geometry("500x400")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.message_listbox = tk.Listbox(self.root, width=60, height=20)
        self.message_listbox.pack(padx=10, pady=10)

        self.message_entry = tk.Entry(self.root, width=60)
        self.message_entry.pack(padx=10, pady=5)

        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack(pady=5)

        self.message_entry.bind("<Return>", self.send_message)

        self.client_socket = None

    def send_message(self, event=None):
        message = self.message_entry.get()
        self.message_entry.delete(0, tk.END)
        if message.strip() != "":
            self.client_socket.send(message.encode("utf-8"))

    def receive_message(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode("utf-8")
                if message:
                    self.message_listbox.insert(tk.END, message)
            except Exception as e:
                print("Error receiving message:", e)
                break

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.client_socket.close()
            self.root.destroy()

    def register_user(self):
        self.register_window = tk.Toplevel(self.root)
        self.register_window.title("Register")
        self.register_window.geometry("300x200")

        username_label = tk.Label(self.register_window, text="Username:")
        username_label.pack()
        self.register_username_entry = tk.Entry(self.register_window)
        self.register_username_entry.pack()

        password_label = tk.Label(self.register_window, text="Password:")
        password_label.pack()
        self.register_password_entry = tk.Entry(self.register_window, show="*")
        self.register_password_entry.pack()

        email_label = tk.Label(self.register_window, text="Email:")
        email_label.pack()
        self.register_email_entry = tk.Entry(self.register_window)
        self.register_email_entry.pack()

        register_button = tk.Button(self.register_window, text="Register", command=self.send_registration)
        register_button.pack(pady=5)

    def send_registration(self):
        username = self.register_username_entry.get()
        password = self.register_password_entry.get()
        email = self.register_email_entry.get()

        if username and password and email:
            data = f"REGISTER {username} {password} {email}"
            self.client_socket.send(data.encode("utf-8"))
            self.register_window.destroy()
            self.login_user()  # Show the login window after registration is completed

    def login_user(self):
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Login")
        self.login_window.geometry("300x150")

        username_label = tk.Label(self.login_window, text="Username:")
        username_label.pack()
        self.login_username_entry = tk.Entry(self.login_window)
        self.login_username_entry.pack()

        password_label = tk.Label(self.login_window, text="Password:")
        password_label.pack()
        self.login_password_entry = tk.Entry(self.login_window, show="*")
        self.login_password_entry.pack()

        login_button = tk.Button(self.login_window, text="Login", command=self.send_login)
        login_button.pack(pady=5)

        register_button = tk.Button(self.login_window, text="Register", command=self.register_user)
        register_button.pack(pady=5)

    def send_login(self):
        username = self.login_username_entry.get()
        password = self.login_password_entry.get()

        if username and password:
            data = f"LOGIN {username} {password}"
            self.client_socket.send(data.encode("utf-8"))

    def handle_login_response(self, response):
        if response == "LOGIN_SUCCESS":
            self.root.deiconify()  # Show the main chat window after successful login
            self.login_window.destroy()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
    
    def start_client(self):
        host = "127.0.0.1"
        port = 5000

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        print("Connected to the server.")

        self.root.withdraw()  # Hide the main chat window until login is successful

        threading.Thread(target=self.receive_message).start()
        self.login_user()  # Show the login window after the client has connected to the server

if __name__ == "__main__":
    chat_app = ChatApp()

    threading.Thread(target=chat_app.start_client, daemon=True).start()

    chat_app.root.mainloop()
