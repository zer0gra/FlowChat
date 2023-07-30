import socket
import sqlite3
import threading

def handle_client(client_socket):
    # Handle the registration and login requests
    request = client_socket.recv(1024).decode("utf-8")
    if request.startswith("REGISTER"):
        _, username, password, email = request.split(" ")
        if register_user(username, password, email):
            client_socket.send("REGISTER_SUCCESS".encode("utf-8"))
        else:
            client_socket.send("REGISTER_FAILED".encode("utf-8"))
    elif request.startswith("LOGIN"):
        _, username, password = request.split(" ")
        if login_user(username, password):
            client_socket.send("LOGIN_SUCCESS".encode("utf-8"))
        else:
            client_socket.send("LOGIN_FAILED".encode("utf-8"))

    client_socket.close()

def register_user(username, password, email):
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Create the users table if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                          id INTEGER PRIMARY KEY,
                          username TEXT NOT NULL,
                          password TEXT NOT NULL,
                          email TEXT NOT NULL)''')

        # Check if the username already exists in the database
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        if user:
            return False  # Username already exists, registration failed

        # Insert the new user data into the database
        cursor.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", (username, password, email))

        # Commit the changes to the database and close the connection
        conn.commit()
        conn.close()

        return True  # Registration successful

    except sqlite3.Error as e:
        print("Error during registration:", e)
        return False  # Registration failed

def login_user(username, password):
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Check if the username and password match in the database
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        if user:
            return True  # Login successful

        return False  # Login failed

    except sqlite3.Error as e:
        print("Error during login:", e)
        return False  # Login failed

def start_server():
    host = "127.0.0.1"
    port = 5000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print("Server listening on {}:{}".format(host, port))

    while True:
        client_socket, addr = server_socket.accept()
        print("[SERVER] New connection from:", addr)

        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_server()

    
