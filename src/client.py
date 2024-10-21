#!/usr/bin/env python3

import socket
import sys
import logging
import json

# Set up logging for debugging purposes
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


# Helper function to serialize a message to JSON
def create_message(msg_type, player_id=None, content=None):
    message = {
        "type": msg_type,
        "player_id": player_id,
        "content": content
    }
    return json.dumps(message)


# Function to connect to the server and exchange messages
def start_client(host, port):
    client_socket = None
    player_id = None  # This will be assigned by the server on join
    player_ready = False  # This flag indicates when a second player has joined

    try:
        # Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(None)  # Allow waiting for server messages without timeout
        logging.info(f"Attempting to connect to {host}:{port}")
        client_socket.connect((host, port))  # Attempt to connect to the server
        logging.info(f"Connected to {host}:{port}")

        # Join the game by sending a "join" message
        player_name = input("Enter your player name: ")
        join_message = create_message("join", None, player_name)
        client_socket.sendall((join_message + "\n").encode('utf-8'))
        logging.info(f"Sent join message: {join_message}")

        buffer = ""

        # Main communication loop
        while True:
            # Receive data from the server, appending to buffer
            buffer += client_socket.recv(1024).decode('utf-8')

            # Process all complete messages (split by newline)
            while '\n' in buffer:
                response, buffer = buffer.split('\n', 1)
                response_data = json.loads(response)

                if response_data["type"] == "broadcast":
                    # A broadcast message indicates another player has joined
                    print(f"\n[BROADCAST]: {response_data['content']}")
                    logging.info(f"Broadcast message: {response_data['content']}")
                    player_ready = True  # Second player has joined, allow actions

                elif response_data["type"] == "waiting":
                    print("\n[INFO]: Waiting for the other player to answer...")

                elif response_data["type"] == "answer":
                    print("\n[INFO]: Both players have answered. You can proceed.")

                elif response_data["type"] == "waiting_for_player":
                    # Display the "waiting for player" message immediately after joining
                    print("\n[INFO]: Waiting for another player to join...")

                elif response_data["type"] == "join":
                    # Confirmation message that the player has joined successfully
                    print(f"\n[INFO]: {response_data['content']}")
                    logging.info(f"Join confirmation: {response_data['content']}")

            # If a second player hasn't joined, don't prompt for action
            if not player_ready:
                continue  # Keep waiting for another player to join

            # Get the next action (answer or quit)
            msg_type = input("Enter action (answer, quit): ").lower()
            if msg_type == "quit":
                quit_message = create_message("quit", player_id, "Goodbye!")
                client_socket.sendall((quit_message + "\n").encode('utf-8'))
                logging.info(f"Sent quit message: {quit_message}")
                break  # Exit the loop and quit the game

            elif msg_type == "answer":
                question_id = input("Enter question ID: ")
                answer = input("Enter your answer: ")
                answer_message = create_message("answer", player_id, {"question_id": question_id, "answer": answer})
                client_socket.sendall((answer_message + "\n").encode('utf-8'))
                logging.info(f"Sent answer message: {answer_message}")

    except socket.error as e:
        logging.error(f"Socket error occurred: {e}")

    finally:
        # Close the connection if it was opened
        if client_socket:
            logging.info(f"Disconnecting from {host}:{port}")
            client_socket.close()


if __name__ == "__main__":
    host = "localhost"
    port = 12345

    # Allow an optional argument for the host and port
    if len(sys.argv) == 3:
        host = sys.argv[1]
        port = int(sys.argv[2])

    start_client(host, port)
