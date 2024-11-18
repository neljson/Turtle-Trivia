#!/usr/bin/env python3

import socket
import sys
import logging
import json
import argparse
import time

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
                        print(f"\n[QUESTION]: {broadcast_content['question']}")
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
                         player_ready = False #Will wait for second player
                         print("\n[INFO]: Waiting for another player to join...")
                    elif "Do you wish to play again?" in response_data['content']:
                        # print(f"\n[BROADCAST]: {content}")
                        while True:
                            restart_response = input("Do you want to play again? (y/n): ").strip().lower()
                            if restart_response == "y":
                                restart_message = create_message("restart", player_id, "y")
                                client_socket.sendall((restart_message + "\n").encode('utf-8'))
                                break
                            elif restart_response == "n":
                                print("Exiting the game.")
                                restart_message = create_message("restart", player_id, "n")
                                client_socket.sendall((restart_message + "\n").encode('utf-8'))
                                time.sleep(0.1)  # Adds a 100ms delay to ensure message is processed
                                quit_message = create_message("quit", player_id, "Goodbye!")
                                client_socket.sendall((quit_message + "\n").encode('utf-8'))
                                exit_game = True  # Set flag to exit both loops
                                break
                            else :
                                print("Invalid input. Please enter 'y' or 'n'.")
                    elif "has joined the game" in response_data['content']:
                        # Indicates another player has joined
                        print("\n 🐢 Welcome to Turtle Trivia 🐢")
                        print("\nFirst player to answer 5 questions correctly wins!\n")
                        print(f"\n[BROADCAST]: {response_data['content']}")
                        player_ready = True  # Second player has joined, allow actions
                    else:
                        print(f"\n[BROADCAST]: {response_data['content']}")

                elif response_data["type"] == "waiting":
                    print(f"\n[INFO]: {response_data['content']}")

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
                while True:
                    msg_type = input("\nEnter your answer (‘quit’ to exit game; ‘help’ for rules): ").strip().lower()
                    if msg_type == "quit":
                        quit_message = create_message("quit", player_id, "Goodbye!")
                        client_socket.sendall((quit_message + "\n").encode('utf-8'))
                        exit_game = True
                        break
                    elif msg_type in ['a', 'b', 'c', 'd']:
                        answer_message = create_message("answer", player_id, msg_type)
                        client_socket.sendall((answer_message + "\n").encode('utf-8'))
                        break
                    elif msg_type == "help":
                        print("""
                        [HELP]: Rules of the game:
                        - Each player will be presented with the same question.
                        - Players must wait until the other player has answered before the game can proceed.
                        - You can quit the game at any time by entering 'quit' after each question prompt.
                        - The first player to answer 5 questions correctly wins.
                        """)
                        # Reprompt the user after displaying help text
                    else :
                        print("Invalid input. Please enter 'a', 'b', 'c', 'd', 'help', or 'quit'.")

                # Reset the flag for the next question
                question_received = False  
                if exit_game:
                    break                        

    except socket.error as e:
        logging.error(f"Socket error occurred: {e}")

    finally:
        # Close the connection if it was opened
        if client_socket:
            logging.info(f"Disconnecting from {host}:{port}")
            client_socket.close()


# Function to handle command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Turtle Trivia Game Client")

    # IP address argument
    parser.add_argument("-i", "--ip", type=str, help="IP address of the server")

    # Port argument
    parser.add_argument("-p", "--port", type=int, default=12345, help="Listening port of the server (default: 12345)")

    # DNS name argument
    parser.add_argument("-n", "--dns", type=str, default="localhost", help="DNS name of the server")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    host = args.ip if args.ip else args.dns
    port = args.port

    start_client(host, port)
