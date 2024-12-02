#!/usr/bin/env python3

import socket
import sys
import logging
import json
import argparse
import time
import select

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
# Set up logging for debugging purposes
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Shared symmetric key (both client and server must use the same key)
SECRET_KEY = b'1234567890abcdef'  # 16 bytes for AES-128
TIMEOUT = 20
# AES block size
BLOCK_SIZE = 128

def encrypt_message(message: str) -> bytes:
    # Encrypt the message using AES
    iv = os.urandom(16)  # Generate a random IV
    cipher = Cipher(algorithms.AES(SECRET_KEY), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(BLOCK_SIZE).padder()

    padded_data = padder.update(message.encode()) + padder.finalize()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # Return IV + ciphertext (IV is needed for decryption)
    return iv + ciphertext

def decrypt_message(encrypted_message: bytes) -> str:
    # Decrypt the message using AES
    iv = encrypted_message[:16]  # Extract IV
    ciphertext = encrypted_message[16:]  # Extract ciphertext
    cipher = Cipher(algorithms.AES(SECRET_KEY), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(BLOCK_SIZE).unpadder()

    plaintext = unpadder.update(padded_data) + unpadder.finalize()
    return plaintext.decode('utf-8', errors='ignore')

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
    global SECRET_KEY
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
        encrypted_join_message = encrypt_message(join_message)
        client_socket.sendall(encrypted_join_message)
        buffer = b""  # Initialize buffer to store encrypted data

        # Main communication loop
        while not exit_game: 
            # Receive data from the server, appending to buffer
            encrypted_data = client_socket.recv(1024)
            ## print encrypted date for demo purposes only:
            # print("encrypted data is below")
            # print(encrypted_data)
            if encrypted_data:
                buffer += encrypted_data
            decrypted_message = decrypt_message(buffer)
            ## print decrypted data for demo purposes only:
            # print("now decrypting this buffer we get")
            # print(decrypted_message)
            # Process all complete messages (split by newline)
            while '||END||' in decrypted_message:
                message, decrypted_message = decrypted_message.split('||END||', 1)
                if decrypted_message:
                    processed_length = len(encrypt_message(message + "||END||"))
                    buffer = buffer[processed_length:]
                else:
                    buffer = b""
                # print("getting message after split")
                # print(message)
                try:
                   response_data = json.loads(message)
                except json.decoder.JSONDecodeError:
                   continue  # Skip invalid responses
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
                         player_ready = False # wait for second player
                         print("\n[INFO]: Waiting for another player to join...")
                    elif "Do you wish to play again?" in response_data['content']:

                        while True:
                            restart_response = input("Do you want to play again? (y/n): ").strip().lower()
                            if restart_response == "y":
                                restart_message = create_message("restart", player_id, "y")
                                encrypted_restart_message = encrypt_message(restart_message)
                                client_socket.sendall(encrypted_restart_message)
                                break
                            elif restart_response == "n":
                                print("Exiting the game.")
                                restart_message = create_message("restart", player_id, "n")
                                encrypted_restart_message = encrypt_message(restart_message)
                                client_socket.sendall(encrypted_restart_message)
                                time.sleep(0.1)  # Adds a 100ms delay to ensure message is processed
                                quit_message = create_message("quit", player_id, "Goodbye!")
                                encrypted_quit_message = encrypt_message(quit_message)
                                client_socket.sendall(encrypted_quit_message)
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
                    print("\nEnter your answer (‘quit’ to exit game; ‘help’ for rules): ", end="", flush=True)
                    # Wait for input with a timeout
                    ready, _, _ = select.select([sys.stdin], [], [], TIMEOUT)  # timeout set to get the response.
                    if ready:  # If the user provides input
                        msg_type = sys.stdin.readline().strip().lower()
                        if msg_type == "quit":
                            quit_message = create_message("quit", player_id, "Goodbye!")
                            encrypted_quit_message = encrypt_message(quit_message)
                            client_socket.sendall(encrypted_quit_message)
                            exit_game = True
                            break
                        elif msg_type in ['a', 'b', 'c', 'd']:
                            answer_message = create_message("answer", player_id, msg_type)
                            encrypted_answer_message = encrypt_message(answer_message)
                            client_socket.sendall(encrypted_answer_message)
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
                    else :  # Timeout occurred
                        print("\n[INFO]: Time's up! You didn't respond in time. You lose this round.")
                        # Send a message to the server indicating the player lost this round
                        timeout_message = create_message("answer", player_id, "timeout")
                        encrypted_timeout_message = encrypt_message(timeout_message)
                        client_socket.sendall(encrypted_timeout_message)
                        break

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
