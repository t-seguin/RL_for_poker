from typing import TYPE_CHECKING
from .hand import Hand
from .action import Action, ActionType

if TYPE_CHECKING:
    from .betting_round import BettingRound


class PlayerActionError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Player:
    """Represents a player at the table with their chips and position"""

    def __init__(self, name: str, chips: int):
        self.name = name
        self.chips = chips
        self.position = -1
        self.hand: "Hand" = Hand()
        self.current_bet = 0
        self.folded = False
        self.spoke = False
        self.revealed = False
        self.is_all_in = False

    def validate_action(self, action: "Action", betting_round: "BettingRound"):
        if (
            action.type in [ActionType.BET, ActionType.RAISE]
            and action.amount != -1
            and action.amount < betting_round.min_bet
        ):
            raise PlayerActionError(
                f"amount must be greter than min bet : {self.current_round.min_bet}"
            )
        if (
            action.type == ActionType.CHECK
            and betting_round.current_bet > self.current_bet
        ):
            raise PlayerActionError("Cannot check when there is a bet to call")
        if self.position != betting_round.current_player_index:
            raise PlayerActionError(f"Not {self.name}'s turn to act")

        if self.folded:
            raise PlayerActionError(f"Player {self.name} has already folded")

        if action.type == ActionType.BET and betting_round.current_bet != 0:
            raise PlayerActionError("A bet can't be done if current bet is not 0")

    def place_bet(self, amount: float, blind_bet: bool = False) -> float:
        """Place a bet of the specified amount"""
        if amount > self.chips or amount <= 0:
            raise PlayerActionError("amount not valid")
        if amount == -1:
            amount = self.chips
        if amount == self.chips:
            self.is_all_in = True
        if not blind_bet:
            self.spoke = True

        self.chips -= amount
        self.current_bet += amount

        return amount

    def fold(self):
        """Fold the current hand"""
        if self.folded or self.spoke:
            raise PlayerActionError("Player already folded or spoke")
        self.folded = True
        self.spoke = True

    def check(self):
        """Handle parameters affected by a check"""
        if self.spoke:
            raise PlayerActionError("Player already spoke")
        self.spoke = True

    def call(self, amount_to_call: float):
        """Handle player call"""
        if amount_to_call <= 0:
            raise PlayerActionError("Player cannot call")
        if amount_to_call > self.chips:
            amount_to_call = self.chips
        self.place_bet(amount_to_call)

    def raise_(self, amount_to_raise: float, blind_posting: bool = False) -> float:
        """Handle player raise"""
        return self.place_bet(amount_to_raise, blind_posting)

    def reveal(self):
        """Set the player's revealed to True"""
        if self.spoke:
            raise PlayerActionError("Player already spoke")
        self.revealed = True
        self.spoke = True

    def hide(self):
        """Set the player to hide status"""
        if self.spoke:
            raise PlayerActionError("Player already spoke")
        self.revealed = False
        self.spoke = True

    def reset_hand(self):
        """Reset the player's state for a new hand"""
        self.hand = Hand()
        self.current_bet = 0
        self.folded = False
        self.spoke = False
        self.revealed = False
        self.is_all_in = False

    def new_stage(self):
        """Reset the player's state for a new stage"""
        self.current_bet = 0
        self.spoke = False

    def to_phn(self) -> str:
        """Convert player to phn format"""
        phn = f"P{self.position}_{self.chips}"
        if self.revealed:
            phn += f"_{''.join([card.to_phn() for card in self.hand.hole_cards])}"

        return phn

    def get_available_actions(self, betting_round: "BettingRound"):
        if betting_round.stage < 4:
            if betting_round.current_bet == 0:
                return [ActionType.BET, ActionType.CHECK]
            else:
                if betting_round.current_bet == self.current_bet:
                    return [ActionType.RAISE, ActionType.CHECK]
                else:
                    return [ActionType.RAISE, ActionType.CALL, ActionType.FOLD]
        else:
            return [ActionType.REVEAL, ActionType.HIDE]

    @classmethod
    def get_action(self, betting_round: "BettingRound") -> "Action":
        pass

    def __str__(self):
        """Return string representation of the player"""
        return f"{self.name} (Position: {self.position}, Chips: {self.chips}, Spoke: {self.spoke})"

    def __repr__(self):
        return self.__str__()


class HumanPlayer(Player):
    """Represents a human player at the table with their chips and position"""

    def __init__(self, name: str, chips: int):
        super().__init__(name, chips)

    def get_action(self, betting_round: "BettingRound") -> "Action":
        """Get the action for the Human player"""
        available_actions = self.get_available_actions(betting_round)
        print(f"Available actions : {[str(a) for a in available_actions]}")
        action = Action(*input("Enter your action: ").lower().strip().split(" "))

        if action.type not in available_actions:
            raise Exception("Action type is not available")

        return action


class AIPlayer(Player):
    """Represents an AI player at the table with their chips and position"""

    def __init__(self, name: str, chips: int, strategy: str = "allways_call"):
        super().__init__(name, chips)
        self.strategy = strategy

    def get_action(self, betting_round: "BettingRound") -> "Action":
        """Get the action for the AI player"""
        available_actions = self.get_available_actions(betting_round)
        if self.strategy == "allways_call":
            if ActionType.CALL in available_actions:
                return Action(ActionType.CALL)
            elif ActionType.CHECK in available_actions:
                return Action(ActionType.CHECK)
            elif ActionType.REVEAL in available_actions:
                return Action(ActionType.REVEAL)
            else:
                raise Exception(f"Cannot do action for the startegy {self.strategy}")
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
