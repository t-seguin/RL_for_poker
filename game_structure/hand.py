from typing import List
from .card import Card


class Hand:
    """Represents a poker hand (hole cards + community cards)"""

    def __init__(self):
        self.hole_cards: List[Card] = []
        self.community_cards: List[Card] = []

    def add_hole_card(self, card: Card):
        """Add a hole card to the hand"""
        if len(self.hole_cards) < 2:
            self.hole_cards.append(card)
        else:
            raise ValueError("Cannot add more than 2 hole cards")

    def add_community_card(self, card: Card):
        """Add a community card to the hand"""
        if len(self.community_cards) < 5:
            self.community_cards.append(card)
        else:
            raise ValueError("Cannot add more than 5 community cards")

    def get_all_cards(self) -> List[Card]:
        """Get all cards in the hand (hole cards + community cards)"""
        return self.hole_cards + self.community_cards

    def evaluate(self) -> int:
        """Evaluate the hand strength

        Returns:
            int: Hand strength value (higher is better)
        """
        if len(self.hole_cards) != 2:
            return 0

        all_cards = self.get_all_cards()
        if len(all_cards) < 5:
            return 0

        # Sort cards by rank
        sorted_cards = sorted(all_cards, reverse=True)

        # Check for flush
        suits = [card.suit for card in sorted_cards]
        is_flush = len(set(suits)) == 1

        # Check for straight
        ranks = [card.rank for card in sorted_cards]
        is_straight = False
        for i in range(len(ranks) - 4):
            if ranks[i] - ranks[i + 4] == 4:
                is_straight = True
                break

        # Count rank frequencies
        rank_counts = {}
        for rank in ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1

        # Determine hand value
        if is_straight and is_flush:
            return 8000000 + max(ranks)  # Straight flush
        elif 4 in rank_counts.values():
            return 7000000 + max(
                r for r, c in rank_counts.items() if c == 4
            )  # Four of a kind
        elif 3 in rank_counts.values() and 2 in rank_counts.values():
            return 6000000 + max(
                r for r, c in rank_counts.items() if c == 3
            )  # Full house
        elif is_flush:
            return 5000000 + max(ranks)  # Flush
        elif is_straight:
            return 4000000 + max(ranks)  # Straight
        elif 3 in rank_counts.values():
            return 3000000 + max(
                r for r, c in rank_counts.items() if c == 3
            )  # Three of a kind
        elif list(rank_counts.values()).count(2) == 2:
            return 2000000 + max(
                r for r, c in rank_counts.items() if c == 2
            )  # Two pair
        elif 2 in rank_counts.values():
            return 1000000 + max(
                r for r, c in rank_counts.items() if c == 2
            )  # One pair
        else:
            return max(ranks)  # High card

    def __str__(self):
        """Return string representation of the hand"""
        hole_cards_str = " ".join(str(card) for card in self.hole_cards)
        community_cards_str = " ".join(str(card) for card in self.community_cards)
        return f"Hole cards: {hole_cards_str} | Community cards: {community_cards_str}"
