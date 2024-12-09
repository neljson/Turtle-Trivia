
<img src="https://github.com/user-attachments/assets/7728b4e0-2257-44a0-ac22-bce1c939f9e4" width="250" height="250" />

# Turtle-Trivia
Description: A terminal trivia game using Python socket programming

## How to Run

Make sure cryptography library is installed as the game uses symmetric encryption between client and server:
```sh
pip3 install cryptography
```

First start the server then run the client by simply running:

```sh
python3 server.py
python3 client.py
```
By default, if you run the client without any command-line arguments, it will default to connecting to `0.0.0.0` on `port 12345`. However, you may also choose 
to run the client and server by specifying a host and port number with following options and their respective arguments:

```sh
  -p PORT, --port PORT  Port number the server should listen on (default is 12345)
  -i IP, --ip IP        IP address the server should bind to (default is localhost)
  -n DNS, --dns DNS     DNS name of the server (option only available to the client)
  -h , --help           Display a description of all options and their proper usage
```

Example of starting the server:

```sh
 python3 server.py -p 8080
```
Example of starting the client listening on a specified IP address, in this case localhost 127.0.0.1, on port 8080:

```sh
python3 client.py -i 127.0.0.1 -p 8080
```
Additionally, the client may connect to a specified DNS server name:

```sh
python3 client.py -n localhost
```

**How to play:**
1. **Start the server:** Run the `server.py` script.
2. **Connect clients:** Run the `client.py` script on two different machines or terminals.
3. **Play the game:** Two players are presented with turtle trivia questions. Each player must wait for the other player to respond before proceeding to the next round. The first player to asnwer 5 correct answers wins! A tie will also be announced if both players reach 5 correct answers at the same time. Game will prompt both players to play again.

**Rules and Logistics**
* All game interactions are within the terminal. 
* The server will contain a local repository of trivia questions and their correct answers. 
* The game will require the connection of two clients or users in order to play the game
* The same question will be presented to both clients. The server will wait until both players respond before proceeding. 
* There will be a timeout feature of 20 seconds. If the user has not selected an answer within 20 seconds, that user will not receive any points for that question. The server scores the other responding user and then proceeds to the next question.
* The first player to get 5 questions correct will be declared the winner. 
* A draw will be determined if both users reached 5 correct answers at the same time. 

**Implemented Feautres**
* Server will wait until two players (clients) are connected before game can proceed. The initial player to join will receive a broadcast message, indicating the game is waiting for a second player to join
* Game will assign a player ID and prompt each user to enter their name
* Players can enter "help" during the answer prompt if they forget the rules of the game
* Players can quit at any time by entering "quit" in the answer prompt. The remaining player will be notified that the other player has disconnected.
* Players will be notified of invalid responses and prompted to enter again
* After each round of questions, the server will broadcast the current game score of each player as well as the correct answer to the previous question
* A timer of 20 seconds is given to each player to answer. Failure to answer question within 20 seconds will result in an automatic loss of that round. 
* Upon a win or tie, each player will be notified of the winner.
* Game will prompt each player if they wish to play again.
* If both players consent, game will restart.
* If one player consents and the other wishes to exit, the game will notify the remaining player that it is waiting for a new player to join. When a new player has joined, the game will restart.

**Retrospectives**
* What went well:
    * I did well in pacing myself throughout the sprints. In particular I had gone a little bit ahead in sprint 3, which made sprint 4 a lot more manageable toward the end of the semester. I also think I did pretty well in thinking about the user-facing experience and what would make a game more user friendly and responsive. There shouldn't be any confusion from the player's perspective what is happening with the game state. For example, when one player answers a question, I knew it would be important to broadcast to that player that the server is still waiting for the other player to respond. This is analgous to how an online form on a properly designed website would have a loading bar or some visual indication to the user that their form has been submitted and is in the state of processing. This is particularly important for an online multiplayer game, where I wanted it to feel like the other player really was playing with a live person and as such should be notified accordingly with the opposing player's actions. 
* What could be improved on:
    * The biggest limitation to the game is the amount of questions in the question bank (20 questions) and the scope of the questions (turtle/tortoise only). My primary reason for choosing turtles was mostly arbitrary as I thought 'Turtle' and 'Trivia' was a nice form of alliteration. I also like cute things and I think turtles are cute. However, cute things is not what a good project makes. Forcing myself to these scope of the questions was far too narrow and limited my ability to create enough unique questions should the game go longer than anticipated for both players. In retrospect, the scope and subject matter of the trivia questions should be broadened. I also somewhat regret taking on implementing symmetric encryption before I had fully finished my game. Adding symmetric encryption broke a lot of communication between my client and server. I took too much time trying to fix and debug it that I think my time was better spent on adding more features to the game. 

**Roadmap**
* My biggest roadmap for the game is to build out a visual UI for the game. A terminal game made sense for the scope of my project, especially since I was working solo. Making an aesthetically pleasing UI itself is a pretty large task, let alone integrating it with the server. For my UI, I think I would add some whimsical music to the background to fit the light heartedness of the game. Because my game is a trivia game, there is not much in features to be added to my UI, except for audio. A silent game I think isn't very appealing and all games that I've ever played always have some kind of background music or sounds. My first focus for the UI would be too add audio. I would probably build the frontend out in Javascript as it is the lingua franca of the web. I am not too familar with how to connect the backend, which is written in Python, to a frontend written in Javascript. Preliminary research tells me I should use Websockets to establish realtime communication between Javascript and a backend Python server. 
  
**Known Bugs**
* There aren't any bugs that I can think of except that when I was adding symmetric encryption, it did break many communications between the client and server. I have since tested and fixed those weird behaviors, but if any further weird behavior is observed it is mostly likely my implementation of encryption that is breaking it. 

**Technologies used:**
* Python
* Sockets

**Additional libraries needed:**
* cryptography

-------------
## Sprint 5 (12-02-24)

**Features added this sprint:**
1. **Timeout feature**
   - if player does not answer within 30 seconds, they immediately lose that round
2. **Symmetric encryption**
   - client and server share the same key and messages between client and server are encrypted
3. **Error logs**
   - Errors are logged to an `error_logs` file, saved in the current directory of the server and client files. 
5. **Question bank completed**
   - 20 trivia question bank has been completed
6. **Correct answer display**
   - After each round, in addition to the game score being displayed, the correct answer is also displayed to each player after each round
  
**Security issues and concerns**
* A key security issue in my client and server implementation lies in the lack of input validation and sanitization. For example, user-supplied data like player names, answers, or other content sent in JSON messages are directly processed without validation, making the application vulnerable to malformed inputs or potential exploits like denial-of-service (DoS) attacks or injection attacks. Additionally, the server trusts all data received from clients without verification, which could allow spoofed or malicious messages to disrupt the game state. To address these aforementioned issues, I need to implement robust input validation on both the client and server sides to ensure that all incoming data conforms to expected formats and constraints. Additionally, I would enforce rate limiting or message size limits to prevent flooding attacks, and introduce session management to verify the authenticity of connected clients and maintain a secure state.
  
## Sprint 4 (11-17-24)

**Features added this sprint:**

1. **CLI options**
  
- When running server.py and client.py, the "-h" option may be passed in the CLI. Upon doing so, the user will be greeted with:
  ```sh
    -p PORT, --port PORT  Port number the server should listen on (default is 12345)
    -i IP, --ip IP        IP address the server should bind to (default is localhost)
    -n DNS, --dns DNS     DNS name of the server (option only available to the client)
  ```
  Example of starting the server:
  
  ```sh
   python3 server.py -p 8080
  ```
  Example of starting the client listening on a specified IP address, in this case 0.0.0.0, on port 8080:
  
  ```sh
  python3 client.py -i 0.0.0.0 -p 8080
  ```
  Additionally, the client may connect to a specified DNS server name:
  
  ```sh
  python3 client.py -n localhost
  ```
- The user can still run the server and client without passing any options/CLI arguments. ```python3 server.py``` and ```python3 client.py``` will default to running on ```localhost``` (IP of ```0.0.0.0.0```) on port ```12345```
  
2. **User friendly experience/quality of life improvement**
- Win condition checking, player status, game state tracking, and score tally display info were already added in the previous sprint. However, in order to improve user experience, the 'action' prompt has now been removed. Instead, the player can enter their answer immediately after each question prompt.

4. **UX improment: re-connect play again status**
- In the previous iteration, each user can enter 'y' to play again once the game has ended. However, the terminal hangs upon player input. Now a visual feedback is displayed to users that the game has received their input and is awaiting for the other player to input their response.

5. **Help rules option and Quit option added**
- After each question prompt, the user now can ask for help by entering 'help' to display the rules of the game. If the user wishes the quit the game, they can also enter 'quit'
  
6. **Input handling**
- Previously, if the user enters anything but a valid input at each question prompt the terminal hangs and the game becomes frozen. Now, input validation checks have been added. If the user enters an invalid input, they will be re-prompted to enter a valid input: ```Invalid input. Please enter 'a', 'b', 'c', 'd', 'help', or 'quit'.```
- Input handling has also been added upon the game over screen. Each player can only respond using 'y' or 'n' when asked if they wish to play again. Entering a respond other than these two options will also result in a display output re-prompting the user to enter a valid input. 

**TODO**
1. Ran out of time this sprint to make any forward progress since last sprint on trivia question bank. Intend to finish researching and creating questions on the last sprint.
2. After each question prompt, the game should display the correct answer to each user
3. A 30 second timer will need to implemented. If the player takes longer than 30 seconds to answer a question, they will automatically be given an incorrect score.
4. Fix minor display output issue with welcome message displaying in wrong order when the following conditions are met: one player wishes to continue playing the game, other player quits, a new player rejoins the game. New player correctly receives welcome broadcast message before question prompt; however, original player receives the welcome message after their question prompt. 

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
