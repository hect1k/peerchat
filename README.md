# PeerChat

PeerChat is a decentralized peer-to-peer chat room system implemented in Python. This project allows multiple nodes to communicate with each other without the need for a central server. Each node can join the network, send messages, and if the tracker node goes offline, it can elect a new tracker using the Bully Election algorithm. The application provides a simple, text-based user interface (TUI) to send and receive messages.

---

## **Features**

- **Decentralized communication**: Nodes connect to each other without relying on a central server.
- **Tracker system**: One node can act as the tracker and coordinate communication between peers.
- **Automatic tracker election**: If the tracker goes offline, nodes automatically elect a new tracker.
- **Message broadcast**: When a node sends a message, it is broadcast to all connected peers.
- **Text-based User Interface (TUI)**: A simple terminal interface to view messages and interact with other peers.

---

## **Installation**

To run **PeerChat**, ensure that you have Python 3.x installed on your machine. The project is built using standard Python libraries, so no external dependencies are required.

### 1. **Clone the Repository**

```bash
git clone https://github.com/nnisarggada/peerchat.git
cd peerchat
```

### 2. **Run the Tracker**

The tracker acts as the entry point for the nodes. Run the following command to start the tracker:

```bash
python tracker.py
```

By default, the tracker runs on port 5000. You can modify the port inside `tracker.py` if necessary.

### 3. **Run the Nodes**

Each node will need to connect to the tracker and register. To run a node, execute the following:

```bash
python node.py
```

- The node will prompt you to enter a username.
- If the tracker is offline, the node will act as the tracker and will listen on port 5000.
- If the tracker is online, the node will connect to it and join the chat room.

### 4. **Join the Chat**

After running the node, the terminal will display a text-based interface where you can chat with other peers. Type your messages and hit Enter to send. You can press **q** to quit the chat.

---

## **How It Works**

1. **Tracker Node**: The tracker is a central node that maintains a list of all connected peers. Nodes that join the chat room register with the tracker and get the list of other peers.
   
2. **Peer Nodes**: Each node represents a peer in the chat room. Nodes can send messages to other peers, and all messages are broadcast to every connected node.

3. **Bully Election**: If the tracker node goes offline, nodes will elect a new tracker using the Bully Election algorithm. The node with the highest port number becomes the new tracker.

4. **Message Broadcast**: When a node sends a message, it is broadcast to all connected peers. The messages are displayed in a simple TUI where each node can see the incoming and outgoing messages.

---

## **File Structure**

```
PeerChat/
│
├── node.py          # Node implementation with chat interface
├── tracker.py       # Tracker implementation
├── README.md        # This README file
```

---

## **Usage**

1. **Start the tracker**: Run `python tracker.py` on a terminal.
2. **Start nodes**: Run `python node.py` in multiple terminals (with different usernames).
3. **Chat**: Type and send messages. All connected peers will see the messages.

---

## **Troubleshooting**

- **"Connection Refused" Error**: Ensure the tracker is running before starting any nodes.
- **Unexpected Disconnects**: If nodes stop receiving messages, ensure the tracker node is online or has been elected properly.
- **UI glitches**: The text-based user interface is designed for simple use cases. If you encounter issues, feel free to open a bug report or submit a fix.

---

## **Contributing**

We welcome contributions to improve PeerChat. If you have any ideas, bugs, or fixes, please feel free to open an issue or submit a pull request.

## **License**

This project is licensed under the GNU General Public License v3 - see the [LICENSE](LICENSE.md) file for details.

---

## **Future Improvements**

- Add better error handling for network issues.
- Implement encryption for secure messages.
- Support for more advanced features like group chats or file transfers.

