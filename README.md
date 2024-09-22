
![Uploading 08f85ae5-2564-437c-a3d6-3f00916cacab.jpg…]()

# Turtle-Trivia
Description: A terminal trivia game using Python socket programming

**How to play:**
1. **Start the server:** Run the `server.py` script.
2. **Connect clients:** Run the `client.py` script on two different machines or terminals.
3. **Play the game:** Two players are presented with 10 turtle questions. After 10 rounds, the player with the most correct answers wins!

**Rules and Logistics**
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
    
