#!/usr/bin/env python3

import socket
import selectors
import logging

# Set up logging for debugging purposes
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize a selector to manage multiple client connections
sel = selectors.DefaultSelector()


# Function to handle accepting new client connections
def accept_connection(server_socket):
    try:
        client_socket, addr = server_socket.accept()  # Accept a new connection
        logging.info(f"Accepted connection from {addr}")
        client_socket.setblocking(False)  # Set the client socket to non-blocking mode
        sel.register(client_socket, selectors.EVENT_READ, handle_client)  # Register for read events
    except socket.error as e:
        logging.error(f"Error accepting connection: {e}")


# Function to handle client communication
def handle_client(client_socket):
    try:
        data = client_socket.recv(1024)  # Receive data from client
        if data:
            logging.info(f"Received message from {client_socket.getpeername()}: {data.decode('utf-8')}")
            # Echo the message back to the client
            client_socket.sendall(data)
        else:
            # No data means the client has disconnected
            logging.info(f"Client {client_socket.getpeername()} has disconnected")
            sel.unregister(client_socket)
            client_socket.close()
    except socket.error as e:
        logging.error(f"Error handling client {client_socket.getpeername()}: {e}")
        sel.unregister(client_socket)
        client_socket.close()


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

