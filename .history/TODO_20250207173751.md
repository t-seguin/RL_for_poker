# Main features
## 1. Game structure : OOP to create game simulation, outputing files that contain the full game information (cf pgn for chess).

### 1.1 Create class `Game`.
Create a class `Game` that has different attributes :
The "state" attributes :
- `board` which represent the cards on the table
- `deck` which is the cards deck
- `folded` Which is the folded stack of cards
- `players` that gives all the informations about the players (stack, cards, positions,  ...)
- `parameters` which is the parameters of the game (blinds size, time, name, type, ...)
- `historic` that gives all the historic of previous rounds


The class game should have the following methods :
- play(player, action) : Make the player play the action, modify inplace all the involved attributes. If impossible action, return an error.


## 2. Visualisation : Create a visualization feature of the game. (from a game file).
## 3. Implementation of RL for making player's startegy evoluate.



