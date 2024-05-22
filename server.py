import socket
import threading
import json
from datetime import datetime

class ChatServer:
    def __init__(self, host='localhost', port=12345):
        self.server_address = (host, port)
        self.rooms = {}
        self.clients = {}
        self.lock = threading.Lock()

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(self.server_address)

    def handle_commands(self):
        while True:
            command = input("Enter command (add <room>, remove <room>, list): ")
            parts = command.split()
            if len(parts) < 1:
                continue
            cmd = parts[0]
            if cmd == "add" and len(parts) == 2:
                self.add_room(parts[1])
            elif cmd == "remove" and len(parts) == 2:
                self.remove_room(parts[1])
            elif cmd == "list":
                self.list_rooms()
            else:
                print("Invalid command")

    def add_room(self, room_name):
        with self.lock:
            if room_name not in self.rooms:
                self.rooms[room_name] = []
                self.broadcast_rooms_update()
                print(f"Room '{room_name}' added.")
            else:
                print(f"Room '{room_name}' already exists.")

    def remove_room(self, room_name):
        with self.lock:
            if room_name in self.rooms:
                clients_to_disconnect = self.rooms.pop(room_name)
                for client in clients_to_disconnect:
                    self.send_message(client, {"type": "leave", "room": room_name, "message": "Room has been deleted."})
                self.broadcast_rooms_update()
                print(f"Room '{room_name}' removed.")
            else:
                print(f"Room '{room_name}' does not exist.")

    def list_rooms(self):
        with self.lock:
            print("Rooms:")
            for room in self.rooms:
                print(f" - {room}")

    def broadcast_rooms_update(self):
        rooms_list = list(self.rooms.keys())
        message = json.dumps({"type": "rooms_update", "rooms": rooms_list})
        all_clients = set(self.clients.keys())
        for client in all_clients:
            self.server_socket.sendto(message.encode(), client)

    def handle_client_message(self, message, client_address):
        try:
            data = json.loads(message)
            if data['type'] == 'join':
                self.join_room(data['room'], client_address)
            elif data['type'] == 'leave':
                self.leave_room(data['room'], client_address)
            elif data['type'] == 'message':
                self.send_room_message(data['room'], data['message'], client_address)
            elif data['type'] == 'rooms_update_request':
                self.send_rooms_update(client_address)
            elif data['type'] == 'register':
                self.register_client(data['username'], client_address)
        except json.JSONDecodeError:
            print("Invalid message format")

    def register_client(self, username, client_address):
        with self.lock:
            self.clients[client_address] = username
            self.send_rooms_update(client_address)

    def join_room(self, room_name, client_address):
        with self.lock:
            if room_name in self.rooms:
                if client_address not in self.rooms[room_name]:
                    self.rooms[room_name].append(client_address)
                    self.send_message(client_address, {"type": "join", "room": room_name, "message": f"Joined room '{room_name}'."})
                else:
                    self.send_message(client_address, {"type": "join", "room": room_name, "message": f"Already in room '{room_name}'."})
            else:
                self.send_message(client_address, {"type": "error", "message": f"Room '{room_name}' does not exist."})

    def leave_room(self, room_name, client_address):
        with self.lock:
            if room_name in self.rooms:
                if client_address in self.rooms[room_name]:
                    self.rooms[room_name].remove(client_address)
                    self.send_message(client_address, {"type": "leave", "room": room_name, "message": f"Left room '{room_name}'."})
                else:
                    self.send_message(client_address, {"type": "leave", "room": room_name, "message": f"Not in room '{room_name}'."})
            else:
                self.send_message(client_address, {"type": "error", "message": f"Room '{room_name}' does not exist."})

    def send_room_message(self, room_name, message, client_address):
        with self.lock:
            if room_name in self.rooms:
                username = self.clients.get(client_address, "Unknown")
                timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
                full_message = f"{timestamp} {username}: {message}"
                for client in self.rooms[room_name]:
                    if client != client_address:
                        self.send_message(client, {"type": "message", "room": room_name, "message": full_message})

    def send_message(self, client_address, message):
        self.server_socket.sendto(json.dumps(message).encode(), client_address)

    def send_rooms_update(self, client_address):
        rooms_list = list(self.rooms.keys())
        message = json.dumps({"type": "rooms_update", "rooms": rooms_list})
        self.server_socket.sendto(message.encode(), client_address)

    def start(self):
        print("Server started...")
        threading.Thread(target=self.handle_commands, daemon=True).start()
        while True:
            message, client_address = self.server_socket.recvfrom(1024)
            threading.Thread(target=self.handle_client_message, args=(message, client_address), daemon=True).start()

if __name__ == "__main__":
    server = ChatServer()
    server.start()
