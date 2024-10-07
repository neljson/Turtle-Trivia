#!/usr/bin/env python3

import socket
import sys
import logging

# Set up logging for debugging purposes
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


# Function to connect to the server and exchange messages
def start_client(host, port):
    try:
        # Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)  # Set a timeout for connection attempts
        logging.info(f"Attempting to connect to {host}:{port}")
        client_socket.connect((host, port))  # Attempt to connect to the server
        logging.info(f"Connected to {host}:{port}")

        # Send a simple message to the server
        message = "Hello, Server!"
        logging.info(f"Sending message: {message}")
        client_socket.sendall(message.encode('utf-8'))

        # Wait for the response from the server
        response = client_socket.recv(1024)
        logging.info(f"Received response from server: {response.decode('utf-8')}")

    except socket.timeout:
        logging.error(f"Connection to {host}:{port} timed out.")
    except ConnectionRefusedError:
        logging.error(f"Connection to {host}:{port} failed. Is the server running?")
    except socket.error as e:
        logging.error(f"Socket error occurred: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        # Close the connection if it was opened
        if 'client_socket' in locals():
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

