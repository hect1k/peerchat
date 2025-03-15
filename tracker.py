import socket
import threading
import json

TRACKER_HOST = "localhost"
TRACKER_PORT = 5000
PEERS = {}

def handle_peer_connection(client_socket):
    """Handles peer connection and registration."""
    try:
        data = client_socket.recv(1024).decode()
        if data:
            message = json.loads(data)
            action = message.get("action")

            if action == "register":
                port = message["port"]
                PEERS[str(port)] = port  # Add node to peers
                print(f"💻 Node {port} registered.")
                client_socket.sendall(json.dumps(PEERS).encode())  # Send updated peer list

            elif action == "get_peers":
                client_socket.sendall(json.dumps(PEERS).encode())  # Send current peers

            else:
                print(f"⚠️ Unknown action: {action}")
    except Exception as e:
        print(f"⚠️ Error: {e}")
    finally:
        client_socket.close()

def start_tracker():
    """Starts the tracker server to listen for incoming node registrations."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((TRACKER_HOST, TRACKER_PORT))
    server_socket.listen(5)

    print(f"🌍 Tracker running on {TRACKER_HOST}:{TRACKER_PORT}...")

    while True:
        client_socket, _ = server_socket.accept()
        threading.Thread(target=handle_peer_connection, args=(client_socket,), daemon=True).start()

if __name__ == "__main__":
    start_tracker()
