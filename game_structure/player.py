from typing import TYPE_CHECKING
from .hand import Hand
from .action import Action, ActionType

if TYPE_CHECKING:
    from .betting_round import BettingRound


class Player:
    """Represents a player at the table with their chips and position"""

    def __init__(self, name: str, chips: int):
        self.name = name
        self.chips = chips
        self.position = -1
        self.hand: "Hand" = Hand()
        self.is_active = True
        self.current_bet = 0
        self.folded = False
        self.spoke = False
        self.revealed = False

    def place_bet(self, amount: int, blind_bet: bool = False) -> bool:
        """Place a bet of the specified amount

        Args:
            amount (int): Amount to bet

        Returns:
            bool: True if bet was successful, False otherwise
        """
        if amount > self.chips:
            return False
        self.chips -= amount
        self.current_bet += amount
        if not blind_bet:
            self.spoke = True
        return True

    def fold(self):
        """Fold the current hand"""
        self.folded = True
        self.is_active = False
        self.spoke = True

    def reset_hand(self):
        """Reset the player's state for a new hand"""
        self.hand = Hand()
        self.current_bet = 0
        self.folded = False
        self.is_active = True
        self.spoke = False
        self.revealed = False

    def new_stage(self):
        """Reset the player's state for a new stage"""
        self.current_bet = 0
        self.spoke = False

    def speak(self):
        """Set the player's spoke to True"""
        self.spoke = True

    def reveal(self):
        """Set the player's revealed to True"""
        self.revealed = True

    def __str__(self):
        """Return string representation of the player"""
        return f"{self.name} (Position: {self.position}, Chips: {self.chips}, Spoke: {self.spoke})"

    def __repr__(self):
        return self.__str__()


class HumanPlayer(Player):
    """Represents a human player at the table with their chips and position"""

    def __init__(self, name: str, chips: int):
        super().__init__(name, chips)


class AIPlayer(Player):
    """Represents an AI player at the table with their chips and position"""

    def __init__(self, name: str, chips: int, strategy: str = "allways_call"):
        super().__init__(name, chips)
        self.strategy = strategy

    def get_action(self, betting_round: "BettingRound") -> "Action":
        """Get the action for the AI player"""
        if self.strategy == "allways_call":
            if (
                betting_round.current_bet > 0
                and self.current_bet < betting_round.current_bet
            ):
                return Action(ActionType.CALL)
            else:
                return Action(ActionType.CHECK)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
