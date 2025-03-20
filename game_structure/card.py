class Card:
    """Represents a single playing card with rank and suit"""

    RANKS = {
        2: "2",
        3: "3",
        4: "4",
        5: "5",
        6: "6",
        7: "7",
        8: "8",
        9: "9",
        10: "T",
        11: "J",
        12: "Q",
        13: "K",
        14: "A",
    }
    SUITS = {"heart": "♥", "diamond": "♦", "club": "♣", "spade": "♠"}

    def __init__(self, rank: int, suit: str):
        """Initialize a card with rank and suit

        Args:
            rank (int): Card rank (2-14, where 14 is Ace)
            suit (str): Card suit ('heart', 'diamond', 'club', 'spade')
        """
        self.rank = rank
        self.suit = suit

    def __str__(self):
        """Return string representation of the card"""
        return f"{self.RANKS[self.rank]}{self.SUITS[self.suit]}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        """Compare two cards for equality"""
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit

    def __lt__(self, other):
        """Compare two cards for less than"""
        if not isinstance(other, Card):
            return NotImplemented
        return self.rank < other.rank
