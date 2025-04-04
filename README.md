# Poker Application
This is an experimental project to explore reinforcement learning applied to poker game.

### 1. Game structure : OOP to create game simulation, outputing files that contain the full game information (cf pgn for chess).

#### Key classes, attributes and methods :

- `Game`: 
    **Atrributes**
    - `infos` (GameInfo): class containing all unsefull informations about the game : blinds, name, format, ...
    - `table` (Table): class containing the players, 
    - `deck` : cards deck
    - `players` : 
    - `parameters` : is the parameters of the game (blinds size, time, name, type, ...)
    - `historic` that gives all the historic of previous rounds


#### 1.1 Create class `Game`
Create a class `Game` that has different attributes:

**State Attributes:**
- `board` which represent the cards on the table
- `table` which represent the table with the players
- `deck` which is the cards deck  
- `folded` Which is the folded stack of cards
- `players` that gives all the informations about the players (stack, cards, positions, ...)
- `parameters` which is the parameters of the game (blinds size, time, name, type, ...)
- `historic` that gives all the historic of previous rounds

**Core Methods:**
- `add/remove_player(player)` : To add or remove a player
- `play(player, action)` : Make the player play the action, modify inplace all the involved attributes. If impossible action, return an error.
- 

### 2. Visualization
Create a visualization feature of the game (from a game file).

#### 2.1 Historic format : 
The historic format will be the following :
```
    Stage number :
        0: pre-flop
        1: flop
        2: turn
        3: river 

    Object format :
        B: board
        P*: player *

    Possible actions :
        cl: call
        ch: check
        fd: fold
        rs: raise
        wn: win
        rv: reveal

    Historic format : 
        Informal part
        
        [StageNum]. [Object].[Action].[Value]

    Example of historic for one hand :

    [Hand# 1]
    [BigBlind 4]
    [Players]
        [P1 "michel"]
        [P2 "alice"]
    [Positions] 
        [BB P2]
        [SB P1]
    [Chips]
        [P1 100]
        [P2 100]
    [Termination "P2 wins 60"]

    0. P1.cl P2.rs.20 P1.cl B.rv.Q♥ B.rv.4♥ B.rv.K♣ 1. P1.ch P2.rs.20 P1.fd P2.wn.60
```

### 3. Implementation of RL for making player's strategy evolve

**Neural Network Architecture**

Each player is modelized as a neural network taking in the input layer the differents information:

**Game State Inputs:**
- Hole cards: Strength of the player's private cards
- Community cards: Cards on the board, affecting potential hand combinations
- Pot odds: Ratio of the current bet to the potential winnings in the pot
- Opponent actions: Betting patterns (e.g., raise, call, fold)
- Stack sizes: Remaining chips for all players
- Position: Whether the player acts early, middle, or late in the betting round
- Round stage: Pre-flop, flop, turn, or river

**Player Trait Inputs:**
- Aggressiveness
- Bluff frequency
- Memory depth
- Learning rate
- Strategy profile
- Opponent tracking data

**Current Output Layer:**
- Fold
- Call
- Raise
- Bluff

**Future Output Layer Consideration:**
- Fold
- Call
- Raise
- Amount

**Loss Function Requirements:**
- evaluate how different is the behavior with the input traits (Using behavior evaluation function)
- variate regarding the win/loose amount

**Training Steps:**
1 step = one hand played
