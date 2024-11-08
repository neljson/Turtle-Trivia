
<img src="https://github.com/user-attachments/assets/7728b4e0-2257-44a0-ac22-bce1c939f9e4" width="250" height="250" />

# Turtle-Trivia
Description: A terminal trivia game using Python socket programming

## How to Run

First start the server then run the client. If you run the client without any command-line arguments, it will default to connecting to `localhost` on `port 12345`. However, you may also choose 
to run the client and server by specifying a host and port number:

```sh
python3 server.py <host> <port>
python3 client.py <host> <port>
```

Example of starting the server:

```sh
 python3 server.py 127.0.0.1 8080
```
Example of starting the client:

```sh
python3 client.py 127.0.0.1 8080
```

**How to play:**
1. **Start the server:** Run the `server.py` script.
2. **Connect clients:** Run the `client.py` script on two different machines or terminals.
3. **Play the game:** Two players are presented with 10 turtle questions. After 10 rounds, the player with the most correct answers wins!

**Rules and Logistics**
* The game will be interfaced via the terminal. 
* The server will contain a local repository of trivia questions and their correct answers. 
* The game will require the connection of two clients or users in order to play the game
* The same question will be presented to both clients. The server will wait until both players respond before proceeding. 
* There will be a timeout feature of 30 seconds. If the user has not selected an answer within 30 seconds, that user will not receive any points for that question. The server scores the other responding user and then proceeds to the next question.
* The first player to get 5 questions correct will be declared the winner. 
* A draw will be determined if both users reached 5 correct answers at the same time. 


**Technologies used:**
* Python
* Sockets

**Additional resources:**
* N/A

-------------

## Sprint 3 (11-03-24)

Features added in Sprint 3:

1. Synchronized Turn Actions
- The server enforces turn-based gameplay, where each player must wait for the other to answer before proceeding to the next action. This is achieved by setting a flag, `answers_received`, which tracks whether both players have answered. Players cannot proceed until both responses are received.

3. Game State Synchronization.
- Score Updates: After each trivia question, the server broadcasts the current game score tally, keeping both players up-to-date on each other's scores and progress.

4. Disconnection Alerts
- Player Disconnection: If one player disconnects during gameplay, the server alerts the other player after their next action with the message `"Player {player_name} has left the game."` This notification ensures the remaining player knows the game's status. The player must wait for a new player to join if they wish to continue playing the game.

5. Player Identification
- Username and Player ID: When joining the game, each player can enter their chosen username, which is displayed to both players. Additionally, each player is assigned a unique Player ID.

6. Win Condition Tracking
- Winning the Game: The server actively tracks each player's score, with the first player to answer 5 questions correctly declared the winner. Once a player wins, the game concludes, and the server announces the winner to both players.

7. Game Lobby:
- If one player joins first, a broadcast message is displayed `Waiting for another player to join...`. The first joining player will need to wait until the other player has joined before proceeding. Once both players are connected, the game proceeds.

8. Repository of trivia questions
- A separate python file called `question_bank.py`  was created to hold a list of trivia questions, 4 choices (a,b,c,d), and the correct answer. The server picks questions sequentially starting from question 1. It uses the variable `current_question_index` to track the current question, which is incremented after each question is asked. This means that players will receive questions in the order they appear in the questions list from `question_bank.py`

#### TODO 
1. Currently, I've only researched and created 6 turtle trivia questions along with their resulting answers and answer choice options. For the rest of the questions in the `question_bank.py`, I've placed placeholder text. The rest of the questions and answer choices will be filled out in the future.
2. The game should broadcast an introductory and welcome message to both players at the very start of the game to describe the game and establish rules so both players know how to play the game.
3. Currently, both players can only give an action input of either 'answer' to proceed with answering the question or 'quit' to quit the game. It is not able to handle inputs other than these two choices. For the future, will need to provide error handling/input validation and re-prompt the user should they enter a response other than 'answer' or 'quit'.
4. A timeout feature needs to be added should one of the players take an excessively long to answer a question.
5. Remove bug where server broadcasts its JSON object along with the normal player disconnect broadcast message.

-------------

## Sprint 2 (10-20-24)

Added functionality and accomplishments in Sprint 2:
### Structure and Format of Messages Exchanged
- Messages between the server and the clients are structured in JSON format. Each message contains the following elements:

- Type: This specifies the type of action or event, such as "join," "answer," "quit," etc.
- Player ID: This is used to identify the player sending or receiving the message.
- Content: The main body of the message, which includes the actual data being sent (e.g., player name, answer, broadcast message).
### Message Types and Data Fields
Used a set of well-defined message types to handle different interactions between the server and clients including join, waiting_for_player, broadcast, answer, and quit. 

### JSON Protocol for Serialization and Deserialization
- Used JSON as the format for both serialization (converting data to a format for transmission) and deserialization (reconstructing data after receiving it).
- Serialization: Before sending a message from the client to the server (or vice versa), use Python’s json.dumps() function to serialize the message into a JSON string.
- Deserialization: Upon receiving a message, use json.loads() to deserialize the JSON string back into a Python dictionary for processing.

#### Server (`server.py`)
- The server handles multiple client connections and maintains game state for each player as shown as printed output.
- The server broadcasts messages to all clients when a player joins or leaves the game.
- This ensures that Client 1 cannot proceed until Client 2 has joined the game.
#### Client (`client.py`)
1. Client 1:
- Upon entering their name, Client 1 will receive a message informing them to wait for another player before proceeding with any actions.
- Once Client 2 joins, Client 1 can then proceed to the action prompt (e.g., answering trivia questions or quitting the game).
2. Client 2:
- After joining, Client 2 immediately proceeds to the action prompt.
3. Quit Action
- When either player enters the action "quit", the other player will receive a broadcast message that the first player has quit the game.
- This broadcast message is only shown to the other player after they proceed through another action (such as answering a trivia question). - It will not immediately interrupt their current action.
#### TODO - Synchronizing Answer Actions
Had a lot of trouble this sprint accomplishing synchronizing between answer action prompts between clients. The next planned feature in the next sprint is to sync the answer actions between the two clients. The goal is to:

- Ensure that once a player answers a trivia question, they must wait for the other player to answer before proceeding.
- Players will not be allowed to proceed to the next prompt until both players have submitted their answers.
- Each client will see a notification message such as "Waiting for the other player to answer..." until the second player has responded.

#### TODO - Trivia Action Prompts
- The action prompts for the question ID and answer in the current implementation are just placeholders. Players are asked to enter a question ID and an answer, but these do not correspond to real trivia questions yet.

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
