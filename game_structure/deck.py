class Deck(list):

    def __init__(self):
        """Initialize a standard 52-card deck"""
        super().__init__()
        for suit in range(4):  # 0=hearts, 1=diamonds, 2=clubs, 3=spades
            for rank in range(2, 15):  # 2-14 representing 2 through Ace
                self.append(Card(suit, rank))
        self.shuffle()

    def shuffle(self):
        """Shuffle the deck"""
        from random import shuffle

        shuffle(self)

    def pop(self):
        """Remove and return the top card"""
        if len(self) > 0:
            return super().pop()
        return None


class Card(tuple):
    # Class constants for suits
    HEARTS = 0
    DIAMONDS = 1
    CLUBS = 2
    SPADES = 3

    # Mapping for string representation
    SUIT_NAMES = {
        HEARTS: "hearts",
        DIAMONDS: "diamonds",
        CLUBS: "clubs",
        SPADES: "spades",
    }

    def __new__(cls, suit, rank):
        """Initialize a playing card

        Args:
            suit (int): The card suit (0-3 representing hearts, diamonds, clubs, spades)
            rank (int): The card rank (2-14, where 14 is Ace)
        """
        return super().__new__(cls, (suit, rank))

    @property
    def suit(self):
        return self[0]

    @property
    def rank(self):
        return self[1]

    def __str__(self):
        """String representation of the card"""
        ranks = {11: "Jack", 12: "Queen", 13: "King", 14: "Ace"}
        rank_str = ranks.get(self.rank, str(self.rank))
        return f"{rank_str} of {self.SUIT_NAMES[self.suit]}"

    def __repr__(self):
        return self.__str__()
