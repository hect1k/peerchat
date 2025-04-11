import socket
import threading
import json
import time
import curses
import subprocess

TRACKER_HOST = "localhost"
TRACKER_PORT = 5000
PEER_UPDATE_INTERVAL = 5
ELECTION_TIMEOUT = 3


class ChatNode:
    def __init__(self, username):
        self.username = username
        self.port = self.find_available_port()
        self.peers = {}
        self.running = True
        self.messages = []

        if not self.connect_to_tracker():
            print("⚠️ No tracker found. Initiating election...")
            self.start_election()

        threading.Thread(target=self.start_server, daemon=True).start()
        threading.Thread(target=self.update_peers, daemon=True).start()
        curses.wrapper(self.chat_interface)

    def find_available_port(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("localhost", 0))
        port = sock.getsockname()[1]
        sock.close()
        return port

    def connect_to_tracker(self):
        try:
            tracker_socket = socket.create_connection((TRACKER_HOST, TRACKER_PORT), timeout=2)
            data = {"action": "register", "port": self.port}
            tracker_socket.sendall(json.dumps(data).encode())
            response = tracker_socket.recv(4096).decode()
            tracker_socket.close()
            self.peers = json.loads(response)
            return True
        except Exception:
            return False

    def update_peers(self):
        while self.running:
            try:
                tracker_socket = socket.create_connection((TRACKER_HOST, TRACKER_PORT), timeout=2)
                data = {"action": "get_peers"}
                tracker_socket.sendall(json.dumps(data).encode())
                response = tracker_socket.recv(4096).decode()
                tracker_socket.close()
                self.peers = json.loads(response)
            except Exception:
                print("⚠️ Lost connection to tracker. Initiating election...")
                self.start_election()
            time.sleep(PEER_UPDATE_INTERVAL)

    def start_server(self):
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
        try:
            message = json.loads(client_socket.recv(1024).decode())

            if message.get("type") == "election":
                client_socket.sendall(b"ok")
                threading.Thread(target=self.start_election, daemon=True).start()
                return

            sender_name = message.get("username", "System")
            chat_msg = message.get("message", "")
            formatted_msg = f"💬 {sender_name}: {chat_msg}"
            if formatted_msg not in self.messages:
                self.messages.append(formatted_msg)

        except Exception:
            pass
        finally:
            client_socket.close()

    def broadcast_message(self, message):
        formatted_msg = f"💬 {self.username}: {message}"
        if formatted_msg not in self.messages:
            self.messages.append(formatted_msg)

        chat_msg = json.dumps({"username": self.username, "message": message})
        for peer_port in self.peers.values():
            self.send_message(peer_port, chat_msg)

    def send_message(self, peer_port, message):
        try:
            with socket.create_connection(("localhost", peer_port), timeout=2) as sock:
                sock.sendall(message.encode())
        except Exception:
            pass

    def chat_interface(self, stdscr):
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

                stdscr.addstr(h-2, 0, "-" * w)
                stdscr.addstr(h-1, 0, f"{self.username}: {input_text}")

                key = stdscr.getch()
                if key == 10:
                    if input_text.strip():
                        self.broadcast_message(input_text)
                    input_text = ""
                elif key == 127 or key == curses.KEY_BACKSPACE:
                    input_text = input_text[:-1]
                elif key != -1 and key < 256:
                    input_text += chr(key)

                time.sleep(0.1)
        except KeyboardInterrupt:
            self.running = False
            print("\nExiting gracefully...")

    def start_election(self):
        higher_ports = [int(p) for p in self.peers.values() if int(p) > self.port]
        responded = False

        for peer_port in higher_ports:
            try:
                with socket.create_connection(("localhost", peer_port), timeout=1) as sock:
                    sock.sendall(json.dumps({"type": "election"}).encode())
                    sock.settimeout(ELECTION_TIMEOUT)
                    if sock.recv(1024):
                        responded = True
                        break
            except Exception:
                continue

        if not responded:
            print("👑 No higher node responded. I am elected leader.")
            self.start_new_tracker_process()
            self.announce_leader()

    def start_new_tracker_process(self):
        # Start tracker in background
        try:
            subprocess.Popen(["python", "tracker.py"])
            time.sleep(1)  # Give it a moment to boot
        except Exception as e:
            print(f"❌ Failed to start tracker: {e}")
            return

        # Populate the tracker with known peers
        try:
            tracker_socket = socket.create_connection((TRACKER_HOST, TRACKER_PORT), timeout=2)
            data = {"action": "populate", "peers": self.peers}
            tracker_socket.sendall(json.dumps(data).encode())
            tracker_socket.close()
        except Exception as e:
            print(f"⚠️ Failed to populate tracker: {e}")

    def announce_leader(self):
        announcement = f"👑 Node {self.port} elected leader. New tracker started."
        self.messages.append(announcement)

        chat_msg = json.dumps({"username": "System", "message": announcement})
        for peer_port in self.peers.values():
            if peer_port != self.port:
                self.send_message(peer_port, chat_msg)


def main():
    username = input("Enter your username: ")
    ChatNode(username)

if __name__ == "__main__":
    main()
