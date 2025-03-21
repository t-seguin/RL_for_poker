from .card import Card


class Deck(list):

    def __init__(self):
        """Initialize a standard 52-card deck"""
        super().__init__()
        for suit in range(4):  # 0=hearts, 1=diamonds, 2=clubs, 3=spades
            for rank in range(2, 15):  # 2-14 representing 2 through Ace
                self.append(Card(rank, suit))
        self.shuffle()

    def shuffle(self):
        """Shuffle the deck"""
        from random import shuffle

        shuffle(self)

    def draw(self):
        """Remove and return the top card"""
        if len(self) > 0:
            return super().pop()
        return None
