<p align="center">
	<br>
    <img src="https://i.imgur.com/cPa9CCo.png" alt="ChatHive Logo" width="100">
    <h3 align="center">ChatHive</h3>
    <br>
</p>

**ChatHive** is a powerful chat application that enables users to communicate in multiple rooms through a interface. Built using **Python** with a **Tkinter GUI** for the client and **socket programming** for server-client communication, ChatHive offers a seamless chat experience.

## Features 🌟

### 🏠 Multiple Chat Rooms
- **Create Rooms**: Easily add new chat rooms.
- **Remove Rooms**: Delete existing chat rooms.
- **Join/Leave Rooms**: Users can join and leave chat rooms at any time.
- **List Rooms**: View a list of available chat rooms.

### 📡 Real-Time Communication
- **Message Broadcasting**: Send messages to all users in a room.
- **Room Updates**: Automatic updates when rooms are created or removed.
- **User Notifications**: Inform users when they join or leave rooms.

### 🔒 Thread-Safe Operations
- **Threading**: Efficient handling of multiple clients with threading.
- **Locks**: Ensure data consistency with thread-safe operations.

## Getting Started 🚀

### Prerequisites
Ensure you have the following installed:
- Python 3.x
- Tkinter (usually included with Python)
- A terminal or command prompt for running the server

### Installation

1. **Clone the Repository:**
    ```sh
    git clone https://github.com/mihainiculai/ChatHive.git
    cd ChatHive
    ```

2. **Run the Server:**
    ```sh
    python server.py
    ```

3. **Run the Client:**
    ```sh
    python client.py
    ```

### Usage 📘

1. **Starting the Server:**
   - Run the server script to start listening for client connections.

2. **Client Operations:**
   - Open the client GUI, enter your username, and start chatting by joining available rooms.

3. **Server Commands:**
   - Add, remove, and list rooms using commands in the server terminal:
     - `add <room_name>`
     - `remove <room_name>`
     - `list`

## Project Structure 📂

- **server.py**: Handles server-side operations, room management, and client communication.
- **client.py**: Manages the client-side GUI and communication with the server.

## Dependencies 📦

Ensure you have the necessary Python libraries:
- `socket`
- `threading`
- `json`
- `datetime`
- `tkinter` (for GUI)

## License ⚖️

This project is licensed under the [MIT License](LICENSE).