#!/usr/bin/env python3

import socket
import selectors
import logging
import json

# Set up logging for debugging purposes
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize a selector to manage multiple client connections
sel = selectors.DefaultSelector()
players = {}  # Dictionary to keep track of player data
next_player_id = 1  # Incremental player IDs
answers_received = {}  # Track whether each player has submitted an answer


# Function to handle accepting new client connections
def accept_connection(server_socket):
    try:
        client_socket, addr = server_socket.accept()  # Accept a new connection
        logging.info(f"Accepted connection from {addr}")
        client_socket.setblocking(False)  # Set the client socket to non-blocking mode
        sel.register(client_socket, selectors.EVENT_READ, handle_client)  # Register for read events
    except socket.error as e:
        logging.error(f"Error accepting connection: {e}")


# Function to handle client communication and message processing
def handle_client(client_socket):
    global next_player_id

    try:
        data = client_socket.recv(1024)  # Receive data from client
        if data:
            message = json.loads(data.decode('utf-8'))
            logging.info(f"Received message: {message}")

            # Process the incoming message
            msg_type = message["type"]
            if msg_type == "join":
                handle_join(client_socket, message)

            elif msg_type == "answer":
                handle_answer(client_socket, message)

            elif msg_type == "quit":
                handle_quit(client_socket, message)

        else:
            # No data means the client has disconnected
            handle_disconnection(client_socket)
    except socket.error as e:
        logging.error(f"Socket error: {e}")
        handle_disconnection(client_socket)


# Handle a client joining the game
def handle_join(client_socket, message):
    global next_player_id

    player_name = message["content"]
    player_id = next_player_id
    next_player_id += 1

    # Store the player's state (you can extend this to track more game-related info)
    players[player_id] = {
        "socket": client_socket,
        "name": player_name,
        "has_answered": False  # Track whether this player has submitted an answer
    }

    answers_received[player_id] = False  # Initialize to False

    # Acknowledge the join request and send the player their assigned ID
    response = {
        "type": "join",
        "player_id": player_id,
        "content": f"Welcome {player_name}, your Player ID is {player_id}."
    }
    client_socket.sendall((json.dumps(response) + "\n").encode('utf-8'))  # Send the join message to the new player
    logging.info(f"Player {player_name} (ID: {player_id}) joined the game.")

    # Check if this is the first player or second player joining
    if len(players) == 1:
        # If this is the first player, notify them to wait for the second player
        waiting_message = {
            "type": "waiting_for_player",
            "content": "Waiting for another player to join..."
        }
        client_socket.sendall((json.dumps(waiting_message) + "\n").encode('utf-8'))
    else:
        # If this is the second player, notify all players that the game can begin
        broadcast_message(f"Player {player_name} has joined the game!", exclude_player=None)


# Handle a player's answer to a trivia question
def handle_answer(client_socket, message):
    player_id = message["player_id"]
    answer_data = message["content"]

    logging.info(f"Player {player_id} answered: {answer_data}")
    answers_received[player_id] = True  # Mark that this player has answered

    # Check if both players have answered
    if all(answers_received.values()) and len(answers_received) == 2:
        # Reset the answers for both players
        for p_id in answers_received:
            answers_received[p_id] = False

        response = {
            "type": "answer",
            "player_id": player_id,
            "content": "Answer acknowledged. Both players have answered."
        }

        # Notify both players that they can proceed
        for p_id, player_info in players.items():
            player_info["socket"].sendall((json.dumps(response) + "\n") .encode('utf-8'))

    else:
        # Notify the player to wait for the other player
        response = {
            "type": "waiting",
            "player_id": player_id,
            "content": "Waiting for the other player to answer."
        }
        client_socket.sendall((json.dumps(response)+ "\n").encode('utf-8'))


# Handle a player quitting the game
def handle_quit(client_socket, message):
    player_id = message["player_id"]
    player_name = players[player_id]["name"]
    logging.info(f"Player {player_name} has quit the game.")

    # Notify all other players that this player has left
    broadcast_message(f"Player {player_name} has left the game.")
    handle_disconnection(client_socket)


# Broadcast a message to all players except the sender (optional)
def broadcast_message(message, exclude_player=None):
    for player_id, player_info in players.items():
        if player_id != exclude_player:
            try:
                player_info["socket"].sendall((json.dumps({
                    "type": "broadcast",
                    "content": message
                }) + "\n").encode('utf-8'))
            except socket.error as e:
                logging.error(f"Failed to send broadcast to player {player_id}: {e}")


# Handle a client disconnection
def handle_disconnection(client_socket):
    for player_id, player_info in players.items():
        if player_info["socket"] == client_socket:
            logging.info(f"Player {player_info['name']} (ID: {player_id}) disconnected.")
            sel.unregister(client_socket)
            client_socket.close()
            del players[player_id]
            del answers_received[player_id]
            broadcast_message(f"Player {player_info['name']} has disconnected.")
            break


# Set up the server socket
def start_server(host, port):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen()
        server_socket.setblocking(False)
        sel.register(server_socket, selectors.EVENT_READ, accept_connection)
        logging.info(f"Server listening on {host}:{port}")
    except socket.error as e:
        logging.error(f"Failed to set up server socket: {e}")
        return

    try:
        while True:
            events = sel.select(timeout=None)  # Wait for events (blocking call)
            for key, _ in events:
                callback = key.data  # This will be either `accept_connection` or `handle_client`
                try:
                    callback(key.fileobj)  # Call the function associated with the socket
                except Exception as e:
                    logging.error(f"Error during callback: {e}")
    except KeyboardInterrupt:
        logging.info("Server is shutting down due to KeyboardInterrupt...")
    finally:
        sel.close()
        server_socket.close()
        logging.info("Server has been shut down.")


# Entry point to start the server
if __name__ == "__main__":
    import sys

    host = "localhost"
    port = 12345

    # Allow specifying a host and port as command-line arguments
    if len(sys.argv) == 3:
        host = sys.argv[1]
        port = int(sys.argv[2])

    start_server(host, port)
