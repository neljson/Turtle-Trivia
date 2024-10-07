
<img src="https://github.com/user-attachments/assets/7728b4e0-2257-44a0-ac22-bce1c939f9e4" width="250" height="250" />

# Turtle-Trivia
Description: A terminal trivia game using Python socket programming

**How to play:**
1. **Start the server:** Run the `server.py` script.
2. **Connect clients:** Run the `client.py` script on two different machines or terminals.
3. **Play the game:** Two players are presented with 10 turtle questions. After 10 rounds, the player with the most correct answers wins!

**Rules and Logistics**
* The game will be interfaced via the terminal. 
* The server will contain a local repository of trivia questions and their correct answers. 
* The game will require the connection of two clients or users in order to play the game
* 10 questions will be presented to both users. The server will wait until both players respond before proceeding. 
* There will be a timeout feature of 30 seconds. If the user has not selected an answer within 30 seconds, that user will not receive any points for that question. The server scores the other responding user and then proceeds to the next question.
* After 10 questions, a winner will be determined by the most number of correct answers.
* A draw will be determined if both users answered the same number of correct answers. Both players will be determined winners. 


**Technologies used:**
* Python
* Sockets

**Additional resources:**
* N/A

-------------

## Sprint 1 (10-06-24)

Sprint 1 accomplishes the creation of a simple Python socket server (`server.py`) and client (`client.py`). The server can handle multiple clients concurrently, and the client can connect to the server to send and receive simple messages. The goal of this sprint is to demonstrate basic client-server communication using sockets in Python, with features such as error handling, logging, and support for multiple simultaneous connections.

### Features

#### Server (`server.py`)
1. **Multi-Client Support**:
   - The server can handle multiple simultaneous client connections, allowing at least two clients to connect at the same time.
   - Uses the `selectors` module to enable I/O multiplexing, ensuring non-blocking and concurrent client communication.

2. **Non-blocking Sockets**:
   - The server uses non-blocking sockets to manage multiple client connections effectively.
   - The main server socket listens for incoming connections, and each client connection is also non-blocking, ensuring no single connection prevents the handling of others.

3. **Logging**:
   - Logs all connection and disconnection events.
   - Logs every message received from each client, making it easy to trace communication events.

4. **Error Handling**:
   - Handles various socket errors such as connection issues and input/output errors.
   - Logs all errors for easy debugging.

#### Client (`client.py`)
1. **Connects to the Server**:
   - The client script connects to the server on a specified host and port.
   - Sends a message to the server and waits for a response.

2. **Message Exchange**:
   - After connecting, the client sends a simple message (`"Hello, Server!"`) and waits for the server to echo the message back.

3. **Error Handling and Logging**:
   - Implements error handling for connection issues, timeouts, and socket errors.
   - Logs connection attempts, successful connections, sent messages, and responses received from the server.

### How to Run

First start the server:

```sh
python3 server.py

Then start the client:

```sh
python3 server.py


