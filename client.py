import tkinter as tk
from tkinter import messagebox, simpledialog, PhotoImage
import socket
import threading
import json
import time

class ChatClient:
    def __init__(self, host='localhost', port=12345):
        self.server_address = (host, port)
        self.username = None
        self.current_room = None
        self.rooms = []

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.settimeout(2)

        self.root = tk.Tk()
        self.root.title("ChatHive")

        self.logo = PhotoImage(file='assets/logo.png')
        self.root.iconphoto(True, self.logo)

        self.create_widgets()

        self.username = simpledialog.askstring("Username", "Enter your username:", parent=self.root)
        if not self.username:
            self.root.destroy()
            return

        self.register_username()

        self.listen_thread = threading.Thread(target=self.listen_for_messages, daemon=True)
        self.listen_thread.start()

        self.update_rooms_thread = threading.Thread(target=self.request_rooms_update_periodically, daemon=True)
        self.update_rooms_thread.start()

        self.root.mainloop()

    def create_widgets(self):
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.room_listbox = tk.Listbox(self.top_frame, width=50, height=10)
        self.room_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.button_frame = tk.Frame(self.top_frame)
        self.button_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.join_button = tk.Button(self.button_frame, text="Join Room", command=self.join_room)
        self.join_button.pack(padx=5, pady=5)

        self.leave_button = tk.Button(self.button_frame, text="Leave Room", command=self.leave_room)
        self.leave_button.pack(padx=5, pady=5)

        self.message_textbox = tk.Text(self.root, state=tk.DISABLED, width=50, height=20)
        self.message_textbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(padx=10, pady=10, fill=tk.X)

        self.entry_message = tk.Entry(self.bottom_frame, width=40)
        self.entry_message.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        self.entry_message.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.bottom_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=(0, 10), pady=10)
        self.send_button.config(state=tk.DISABLED)

        self.entry_message.bind("<KeyRelease>", self.update_send_button_state)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_send_button_state(self, event=None):
        if self.entry_message.get():
            self.send_button.config(state=tk.NORMAL)
        else:
            self.send_button.config(state=tk.DISABLED)

    def register_username(self):
        message = json.dumps({"type": "register", "username": self.username})
        self.client_socket.sendto(message.encode(), self.server_address)

    def request_rooms_update(self):
        message = json.dumps({"type": "rooms_update_request"})
        self.client_socket.sendto(message.encode(), self.server_address)

    def request_rooms_update_periodically(self):
        while True:
            self.request_rooms_update()
            time.sleep(5)

    def join_room(self):
        selected_room = self.room_listbox.get(tk.ACTIVE)
        if selected_room and self.current_room != selected_room:
            if self.current_room:
                self.leave_room()
            self.current_room = selected_room
            message = json.dumps({"type": "join", "room": selected_room})
            self.client_socket.sendto(message.encode(), self.server_address)

    def leave_room(self):
        if self.current_room:
            message = json.dumps({"type": "leave", "room": self.current_room})
            self.client_socket.sendto(message.encode(), self.server_address)
            self.current_room = None

    def send_message(self, event=None):
        message_text = self.entry_message.get()
        if self.current_room and message_text:
            timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
            message = json.dumps({"type": "message", "room": self.current_room, "message": message_text})
            self.client_socket.sendto(message.encode(), self.server_address)
            self.entry_message.delete(0, tk.END)
            self.update_send_button_state()
            self.display_message(f"{timestamp} you: {message_text}")

    def display_message(self, message):
        self.message_textbox.config(state=tk.NORMAL)
        self.message_textbox.insert(tk.END, message + "\n")
        self.message_textbox.config(state=tk.DISABLED)
        self.message_textbox.see(tk.END)

    def listen_for_messages(self):
        while True:
            try:
                message, _ = self.client_socket.recvfrom(1024)
                self.handle_server_message(message)
            except socket.timeout:
                continue

    def handle_server_message(self, message):
        try:
            data = json.loads(message)
            if data['type'] == 'rooms_update':
                self.update_room_list(data['rooms'])
            elif data['type'] == 'message':
                self.display_message(data['message'])
            elif data['type'] == 'join':
                self.display_message(data['message'])
            elif data['type'] == 'leave':
                self.display_message(data['message'])
            elif data['type'] == 'error':
                messagebox.showerror("Error", data['message'])
        except json.JSONDecodeError:
            print("Invalid message format from server")

    def update_room_list(self, rooms):
        self.rooms = rooms
        self.room_listbox.delete(0, tk.END)
        for room in rooms:
            self.room_listbox.insert(tk.END, room)

    def on_closing(self):
        if self.current_room:
            self.leave_room()
        self.root.destroy()

if __name__ == "__main__":
    ChatClient()
