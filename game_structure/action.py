from enum import Enum
from typing import Optional


class ActionType(Enum):
    """Enumeration of possible poker actions"""

    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    RAISE = "raise"


class Action:
    """Represents a player action (fold, check, call, raise)"""

    def __init__(
        self, action_type: str | ActionType, amount: Optional[int | str] = None
    ):
        """Initialize an action

        Args:
            action_type (str | ActionType): Type of action as string or ActionType
            amount (Optional[int]): Amount for raise actions
        """
        # Convert string to ActionType if needed
        if isinstance(action_type, str):
            action_type = action_type.lower().strip()
            if action_type not in [t.value for t in ActionType]:
                raise ValueError(f"Invalid action type: {action_type}")
            self.type = ActionType(action_type)
        else:
            self.type = action_type

        if isinstance(amount, str):
            amount = int(amount)

        self.amount = amount

        # Validate action
        if self.type == ActionType.RAISE and amount is None:
            raise ValueError("Raise action requires an amount")
        if self.type != ActionType.RAISE and amount is not None:
            raise ValueError("Amount should only be specified for raise actions")

    @classmethod
    def from_string(cls, action_str: str) -> "Action":
        """Create an action from a string representation

        Args:
            action_str (str): String representation of action (e.g., "fold", "raise 100")

        Returns:
            Action: Created action object
        """
        parts = action_str.lower().strip().split()
        if not parts:
            raise ValueError("Empty action string")

        action_type = parts[0]
        if action_type not in [t.value for t in ActionType]:
            raise ValueError(f"Invalid action type: {action_type}")

        if action_type == ActionType.RAISE.value:
            if len(parts) != 2:
                raise ValueError("Raise action requires an amount")
            try:
                amount = int(parts[1])
                if amount <= 0:
                    raise ValueError("Raise amount must be positive")
                return cls(ActionType.RAISE, amount)
            except ValueError:
                raise ValueError("Invalid raise amount")
        else:
            return cls(ActionType(action_type))

    def __str__(self):
        """Return string representation of the action"""
        if self.type == ActionType.RAISE:
            return f"{self.type.value} {self.amount if self.amount else ''}"
        return self.type.value
