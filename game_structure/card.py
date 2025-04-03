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
SUITS = {0: "♥", 1: "♦", 2: "♣", 3: "♠"}


class Card:
    """Represents a single playing card with rank and suit"""

    def __init__(self, rank: int, suit: int):
        """Initialize a card with rank and suit

        Args:
            rank (int): Card rank (2-14, where 14 is Ace)
            suit (str): Card suit ('heart', 'diamond', 'club', 'spade')
        """
        self.rank = rank
        self.suit = suit

    def to_phn(self) -> str:
        """Return the card representation in phn format"""
        MAPPING_SUITS_PHN = {0: "h", 1: "d", 2: "c", 3: "s"}
        return f"{RANKS[self.rank]}{MAPPING_SUITS_PHN[self.suit]}"

    def __str__(self):
        """Return string representation of the card"""
        return f"{RANKS[self.rank]}{SUITS[self.suit]}"

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
