#!/usr/bin/env python3

import socket
import selectors
import logging
import json
from question_bank import questions  # Import questions from the question bank

# Set up logging for debugging purposes
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize a selector to manage multiple client connections
sel = selectors.DefaultSelector()
players = {}  # Dictionary to keep track of player data
next_player_id = 1  # Incremental player IDs
answers_received = {}  # Track whether each player has submitted an answer
current_question_index = 0  # Track the current question for both players
scores = {1: 0, 2: 0}  # Keep track of each player's score
unanswered_questions = []  # List to store unanswered questions
restart_votes = {}  # Track responses to the restart question


# Score required to end the game
WINNING_SCORE = 5
TOTAL_QUESTIONS = 20

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

            elif msg_type == "restart":
                handle_restart(client_socket, message)

        else:
            # No data means the client has disconnected
            handle_disconnection(client_socket)
    except socket.error as e:
        logging.error(f"Socket error: {e}")
        handle_disconnection(client_socket)

# Handle `restart` responses from players
def handle_restart(client_socket, message):
    player_id = message["player_id"]
    restart_response = message["content"].lower()
    scores[player_id]=0
    answers_received[player_id] =False
    # Record the player's vote
    restart_votes[player_id] = restart_response
    logging.info(f"Player {players[player_id]['name']} chose to {'restart' if restart_response == 'y' else 'quit'}.")

    # Check if all players have responded
    if len(restart_votes) > 1:
        if all(vote == 'y' for vote in restart_votes.values()):
            reset_game()
        else:
            broadcast_message(json.dumps({"type": "end_session", "content": "Thank you for playing! Goodbye."}))

# Reset game state to start a new game session
def reset_game():
    global current_question_index
    restart_votes.clear()
    current_question_index =0
    unanswered_questions.clear() 
    logging.info("Game has been reset. Starting a new game session.")
    send_question_to_players()

# End the game and announce the winner
def end_game():
    # Determine the winner by score
    maxscore = max(scores.values())
    winners = [player_id for player_id, score in scores.items() if score == maxscore]
    if len(winners) == 1:
        # Only one player with the highest score
        winner_name = players[winners[0]]['name']
        broadcast_message(f"{winner_name} is the first to answer 5 questions correctly. {winner_name} wins!")
    else:
        # Multiple players tied with the highest score
        winner_names = " and ".join(players[player_id]['name'] for player_id in winners)
        broadcast_message(f"It's a tie! Both {winner_names} win with the highest score!")
    # Ask if players want to play again
    broadcast_message("Do you wish to play again? (y/n):")

# Handle a client joining the game
def handle_join(client_socket, message):
    global next_player_id
    global current_question_index

    player_name = message["content"]
    player_id = next_player_id
    next_player_id += 1
    scores[player_id] = 0  # player ID can be anything so initilaize it with zero for every player
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
        restart_votes.clear()
        current_question_index =0
        unanswered_questions.clear() 
        for player_id in players:
            answers_received[player_id] = False
            scores[player_id]=0  # Reset answers received
        # If this is the second player, notify all players that the game can begin
        broadcast_message(f"Player {player_name} has joined the game!", exclude_player=None)
        send_question_to_players()

# Function to send the current question to both players
def send_question_to_players():
    global current_question_index

    if current_question_index < TOTAL_QUESTIONS:
        question_data = questions[current_question_index]
        question_message = {
            "type": "question",
            "question": question_data["question"],
            "options":  question_data["options"]
        }
        broadcast_message(json.dumps(question_message))
        logging.info(f"Sent question {current_question_index + 1} to both players.{question_message}")
    else:
        # If all questions are asked, use unanswered questions
        if unanswered_questions:
            question_data = unanswered_questions.pop(0)  # Reuse the first unanswered question
            question_message = {
                "type": "question",
                "question": question_data["question"],
                "options": question_data["options"]
            }
            broadcast_message(json.dumps(question_message))
            logging.info("Reusing an unanswered question for both players.")
        else:
            end_game()  # End the game if no unanswered questions are left

# Handle a player's answer to a trivia question
def handle_answer(client_socket, message):
    global current_question_index
    player_id = message["player_id"]
    answer = message["content"]
    if len(players)>1 : #this condition ensures correctness when other player has left the game before the second one answers.
        logging.info(f"Player {player_id} answered: {answer}")
        # Check if the answer is correct
        correct_answer = questions[current_question_index]["correct_answer"]
        if answer == correct_answer:
            scores[player_id] += 1
            players[player_id]['correct'] = True  # Mark as correct
        else:
            players[player_id]['correct'] = False  # Mark as incorrect
        answers_received[player_id] = True  # Mark that this player has answered
        # Check if both players have answered
        if all(answers_received.values()) and len(answers_received) == 2:
            # Prepare the broadcast message
            current_scores = '\n'.join(f"{players[p_id]['name']}: {scores[p_id]} out of {WINNING_SCORE}" for p_id in players)
            results_message = {
                "type": "score_update",
                "commentary":" ".join(f"{player['name']} answered {'correctly' if player['correct'] else'incorrectly'}!"
                        for _, player in players.items()),
                "currentScore": f"Current Score:\n{current_scores}"
            }
            broadcast_message(json.dumps(results_message))
            # Reset answers for both players
            both_incorrect = True
            for p_id in players.keys():
                if p_id in answers_received and answers_received[p_id]:
                    if answer == correct_answer:  # If at least one player answered correctly
                        both_incorrect = False

            if both_incorrect:
                # If both players answered incorrectly, add the question to unanswered questions
                unanswered_questions.append(questions[current_question_index])

            for p_id in answers_received:
                answers_received[p_id] = False  # Reset answers for the next question
                players[p_id]['correct'] = None  # Reset the correctness
    

            # Check if any player has reached the winning score
            if max(scores.values()) >= WINNING_SCORE:
                end_game()
            else:
                # Move to the next question if no one has won yet
                current_question_index += 1
                send_question_to_players()

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
            disconnection_message ={
                "type": "disconect",
                "content": f"Player {player_info['name']} has disconnected."
            }
            broadcast_message(json.dumps(disconnection_message))
            del players[player_id]
            del answers_received[player_id]
            del scores[player_id]
            del restart_votes[player_id]
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
