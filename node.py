import socket
import threading
import json
import time
import curses

TRACKER_HOST = "localhost"
TRACKER_PORT = 5000  # Fixed tracker port
PEER_UPDATE_INTERVAL = 5  # Refresh peer list every 5 seconds

class ChatNode:
    def __init__(self, username):
        self.username = username
        self.port = self.find_available_port()
        self.peers = {}  # List of other chat nodes
        self.running = True
        self.is_tracker = False  # Will be set to True if acting as tracker
        self.messages = []  # Store chat messages

        # Try connecting to the tracker; if it fails, raise an error
        if not self.connect_to_tracker():
            print("⚠️ No tracker found. Exiting...")
            return

        # Start listening for messages
        threading.Thread(target=self.start_server, daemon=True).start()

        # Periodic peer updates
        threading.Thread(target=self.update_peers, daemon=True).start()

        # Start the chat TUI
        curses.wrapper(self.chat_interface)

    def find_available_port(self):
        """Finds an available port dynamically."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("localhost", 0))
        port = sock.getsockname()[1]
        sock.close()
        return port

    def connect_to_tracker(self):
        """Tries to connect to the tracker and register this node."""
        try:
            tracker_socket = socket.create_connection((TRACKER_HOST, TRACKER_PORT))
            data = {"action": "register", "port": self.port}
            tracker_socket.sendall(json.dumps(data).encode())
            response = tracker_socket.recv(4096).decode()
            tracker_socket.close()

            self.peers = json.loads(response)
            return True
        except ConnectionRefusedError:
            return False  # Unable to connect to the tracker

    def update_peers(self):
        """Periodically fetches the latest peer list from the tracker."""
        while self.running:
            try:
                tracker_socket = socket.create_connection((TRACKER_HOST, TRACKER_PORT))
                data = {"action": "get_peers"}
                tracker_socket.sendall(json.dumps(data).encode())
                response = tracker_socket.recv(4096).decode()
                tracker_socket.close()

                self.peers = json.loads(response)

            except Exception:
                pass

            time.sleep(PEER_UPDATE_INTERVAL)  # Wait before updating again

    def start_server(self):
        """Listens for incoming messages from peers."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("localhost", self.port))
        server_socket.listen(5)

        while self.running:
            try:
                client_socket, _ = server_socket.accept()
                threading.Thread(target=self.handle_message, args=(client_socket,), daemon=True).start()
            except Exception as e:
                print(f"⚠️ Server error: {e}")

    def handle_message(self, client_socket):
        """Processes incoming messages."""
        try:
            message = json.loads(client_socket.recv(1024).decode())

            client_socket.close()

            # Process chat messages
            sender_name = message["username"]
            chat_msg = message["message"]

            formatted_msg = f"💬 {sender_name}: {chat_msg}"
            if formatted_msg not in self.messages:
                self.messages.append(formatted_msg)

        except Exception:
            pass

    def broadcast_message(self, message):
        """Sends a chat message to all peers."""
        chat_msg = json.dumps({"username": self.username, "message": message})

        # Send to all peers
        for peer_port in self.peers.values():
            self.send_message(peer_port, chat_msg)

    def send_message(self, peer_port, message):
        """Sends a message to a specific peer."""
        try:
            with socket.create_connection(("localhost", peer_port)) as sock:
                sock.sendall(message.encode())
        except Exception:
            pass  # Peer might be down

    def chat_interface(self, stdscr):
        """Creates a simple TUI for chatting."""
        stdscr.clear()
        stdscr.nodelay(True)
        curses.curs_set(1)

        input_text = ""

        try:
            while self.running:
                stdscr.clear()
                h, w = stdscr.getmaxyx()

                for i, msg in enumerate(self.messages[-(h-3):]):
                    stdscr.addstr(i, 0, msg)

                stdscr.addstr(h-2, 0, "-" * w)  # Separator line
                stdscr.addstr(h-1, 0, f"{self.username}: {input_text}")

                key = stdscr.getch()
                if key == 10:
                    if input_text.strip():
                        self.broadcast_message(input_text)
                    input_text = ""
                elif key == 127:
                    input_text = input_text[:-1]
                elif key != -1 and key < 256:
                    input_text += chr(key)

                time.sleep(0.1)
        except KeyboardInterrupt:
            self.running = False
            print("\nExiting gracefully...")

def main():
    username = input("Enter your username: ")
    ChatNode(username)

if __name__ == "__main__":
    main()
