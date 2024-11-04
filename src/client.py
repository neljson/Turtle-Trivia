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
    question_received = False
    exit_game = False
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
        #logging.info(f"Sent join message: {join_message}")

        buffer = ""

        # Main communication loop
        while not exit_game: 
            # Receive data from the server, appending to buffer
            buffer += client_socket.recv(1024).decode('utf-8')

            # Process all complete messages (split by newline)
            while '\n' in buffer:
                response, buffer = buffer.split('\n', 1)
                response_data = json.loads(response)

                if response_data["type"] == "broadcast":
                    content = response_data['content']
                    if content.startswith('{"type": "question"'):
                        broadcast_content = json.loads(content)  # Parse here
                        print(f"\n[QUESTION]: {broadcast_content["question"]}")
                        print("Options:")   
                        for option in broadcast_content['options']:
                            print(f"- {option}: {broadcast_content['options'][option]}")
                        question_received=True
                    elif content.startswith('{"type": "score_update"'):
                         score_content = json.loads(content)
                         if score_content["type"] == "score_update":
                            # Scores has been received, display options
                            print(f"{score_content['commentary']}")
                            print(f"{score_content['currentScore']}")
                    elif content.startswith('{"type": "disconect"'):
                         print(f"\n[BROADCAST]: {response_data['content']}")
                         player_ready = False #Will wait for second player
                         print("\n[INFO]: Waiting for another player to join...")
                    elif "Do you wish to play again?" in response_data['content']:
                        # print(f"\n[BROADCAST]: {content}")
                        restart_response = input("Do you want to play again? (y/n): ").strip().lower()
                        if restart_response == "y":
                            restart_message = create_message("restart", player_id, "y")
                            client_socket.sendall((restart_message + "\n").encode('utf-8'))
                        else:
                            print("Exiting the game.")
                            quit_message = create_message("quit", player_id, "Goodbye!")
                            client_socket.sendall((quit_message + "\n").encode('utf-8'))
                            exit_game = True  # Set flag to exit both loops
                            break
                    else:
                        # A broadcast message indicates another player has joined
                        print(f"\n[BROADCAST]: {response_data['content']}")
                        #logging.info(f"Broadcast message: {response_data['content']}")
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
                    player_id = response_data['player_id']
                    logging.info(f"Join confirmation: {response_data['content']}")  
                if exit_game:
                    break
            if exit_game:
                break
            # If a second player hasn't joined, don't prompt for action
            if not player_ready or response_data["type"] == "waiting" :
                continue  # Keep waiting for another player to join
            # Only prompt for action if a question has been received
            if player_ready and question_received:
                msg_type = input("Enter action (answer, quit): ").lower()
                if msg_type == "quit":
                    quit_message = create_message("quit", player_id, "Goodbye!")
                    client_socket.sendall((quit_message + "\n").encode('utf-8'))
                    exit_game = True
                    break

                elif msg_type == "answer":
                    answer = input("Enter your answer: ")
                    answer_message = create_message("answer", player_id, answer)
                    client_socket.sendall((answer_message + "\n").encode('utf-8'))

                # Reset the flag for the next question
                question_received = False                          

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
