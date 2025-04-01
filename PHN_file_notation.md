
## This file describe how a PHN (Poker Hand Notation) file is structured.

```
Historic format : 
    [Informal part]
    
    # pre-hand player status :
    [PlayerId]_[ChipsValue(in bb)]_[CardValue(if pov allow to see cards)]
    
    # during the hand :
    [StageNum]. [PlayerId]_[Action]_[Value(in bb for an amount)]|... B_[CardReaveled] P_[PotValue]

    # end of the hand status:
    [PlayerId]_[ChipsValue(in bb)]_[CardValue(if pov allow to see cards or player reveal)]

PlayerId : P1, P2, ...
ChipsValue|PotValue : float **expressed in bb** or "-1" if player all-in
CardValue : [2|3|...|J|Q|..][s|c|d|h]
CardReaveled = [CardValue][CardValue]...
StageNum :
    0: pre-flop
    1: flop
    2: turn
    3: river
    4: showdown
Object : either the PlayerId or "B" for board
Action :
    bt: bet
    cl: call
    ch: check
    fd: fold
    rs: raise
    rv: reveal
    hd: hide
Value : either ChipsValue or CardValue
```

Check `PHN_file_examples/poker_hand_example*.phn` for examples