from .card import Card
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player


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

    def _draw(self):
        """Remove and return the top card"""
        if len(self) > 0:
            return super().pop()
        return None

    def deal_cards(self, players: list["Player"]):
        """Deal cards to players"""
        for _ in range(2):
            for player in players:
                card = self._draw()
                player.hand.add_hole_card(card)

    def draw_flop(self) -> list[Card]:
        drawn_cards = []
        for _ in range(3):
            drawn_cards.append(self._draw())
        return drawn_cards

    def draw_turn_or_river(self) -> list[Card]:
        return [self._draw()]
