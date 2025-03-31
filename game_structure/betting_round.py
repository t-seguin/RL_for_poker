from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player


class BettingRound:
    """Manages a single betting round (preflop, flop, turn, river)"""

    def __init__(self, stage: int):
        self.stage = stage  # 0=preflop, 1=flop, 2=turn, 3=river
        self.min_bet = 0
        self.current_bet = 0
        self.pot = 0
        self.current_player_index = -1

    def is_complete(self, players: List["Player"]) -> bool:
        """Check if betting round is complete

        Args:
            active_players (List[Player]): List of players who haven't folded

        Returns:
            bool: True if betting round is complete
        """
        active_players = [p for p in players if not p.folded]
        if len(active_players) == 1:
            return True

        # Check if all bets are matched
        all_bets_matched = all(
            p.current_bet == self.current_bet for p in active_players
        )
        all_players_spoke = all(p.spoke for p in active_players)

        if all_bets_matched and all_players_spoke:
            return True

        else:
            return False

    def reset(self):
        """Reset the betting round state"""
        self.current_bet = 0
        self.min_bet = 0
        self.pot = 0

    def update_pot(self, amount: int):
        """Update the pot with new bet amount

        Args:
            amount (int): Amount to add to pot
        """
        self.pot += amount

    def set_min_bet(self, amount: int):
        """Set the minimum bet amount

        Args:
            amount (int): Minimum bet amount
        """
        self.min_bet = amount

    def set_current_bet(self, amount: int):
        """Set the current bet amount

        Args:
            amount (int): Current bet amount
        """
        self.current_bet = amount

    def next_stage(self):
        """Advance to the next stage of the betting round"""
        self.stage += 1
        self.current_bet = 0
        self.min_bet = 0
