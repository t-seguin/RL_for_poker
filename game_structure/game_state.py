from typing import List, TYPE_CHECKING
from .betting_round import BettingRound


if TYPE_CHECKING:
    from .player import Player
    from .card import Card


class GameState:
    """Tracks the current state of the game for UI/display purposes"""

    def __init__(self):
        self.players: List["Player"] = []
        self.community_cards: List["Card"] = []
        self.hand_number = 0
        self.game_over = False
        self.historic = ""
        self.dealer_position = 0
        self.small_blind_position = 1
        self.big_blind_position = 2
        self.current_round: "BettingRound" = BettingRound(0)
        self.pov = -1  # Position of the player of view

    def update(
        self,
        players: List["Player"],
        community_cards: List["Card"],
        hand_number: int,
        game_over: bool,
        dealer_position: int,
        small_blind_position: int,
        big_blind_position: int,
        current_round: "BettingRound",
        pov: int,
    ):
        """Update the game state

        Args:
            stage (int): Current game stage
            players (List[Player]): List of players
            community_cards (List[Card]): List of community cards
            hand_number (int): Current hand number
            game_over (bool): Whether the game is over
            dealer_position (int): Position of the dealer
            small_blind_position (int): Position of the small blind
            big_blind_position (int): Position of the big blind
            current_round (BettingRound): Current betting round
            pov (int): Position of the player of view
        """
        self.players = players
        self.community_cards = community_cards
        self.hand_number = hand_number
        self.game_over = game_over
        self.dealer_position = dealer_position
        self.small_blind_position = small_blind_position
        self.big_blind_position = big_blind_position
        self.current_round = current_round
        self.pov = pov

    def add_to_history(self, action_str: str):
        """Add an action to the game history

        Args:
            action_str (str): String representation of the action
        """
        self.historic += f"{action_str}\n"

    def get_stage_name(self) -> str:
        """Get the name of the current stage

        Returns:
            str: Name of the current stage
        """
        stage_names = ["Pre-flop", "Flop", "Turn", "River"]
        return stage_names[self.current_round.stage]

    def get_position_name(self, position: int) -> str:
        """Get the name of a position based on total players and position number"""
        num_players = len(self.players)

        if position == self.dealer_position:
            return "BTN"
        elif position == self.small_blind_position:
            return "SB"
        elif position == self.big_blind_position:
            return "BB"

        # Calculate positions between BB and BTN
        positions_between = (self.dealer_position - position) % num_players

        if positions_between == 1:
            return "CO"
        elif positions_between == 2:
            return "HJ"
        elif positions_between == 3:
            return "LJ"
        elif position == (self.big_blind_position + 1) % num_players:
            return "UTG"
        else:
            utg_plus = num_players - 3 - positions_between
            return f"UTG+{utg_plus}"

    def __str__(self):
        """Return string representation of the game state"""
        output = []

        # Game info header
        output.append(f"\n{'='*50}")
        output.append(f"Hand #: {self.hand_number}")
        output.append(f"Stage: {self.get_stage_name()}")
        output.append(f"Pot: {self.current_round.pot}")
        output.append(f"Current Bet: {self.current_round.current_bet}")

        # Community cards
        community_str = " ".join(str(card) for card in self.community_cards)
        output.append(
            f"\nCommunity Cards: {community_str if community_str else 'No cards'}"
        )

        # Player information
        output.append("\nPlayers:")
        for i, player in enumerate(self.players):
            status = "FOLDED" if player.folded else "ACTIVE"
            position = self.get_position_name(player.position)
            current_indicator = (
                "-> "
                if player.position == self.current_round.current_player_index
                else "   "
            )
            player_cards = (
                str(player.hand.hole_cards)
                if i == self.pov or self.pov == -1
                else "[XX, XX]"
            )
            player_str = (
                f"{current_indicator}"
                f"{player.name:<15} "
                f"[{position+']':<4} "
                f"Cards: {player_cards:<10} "
                f"Chips: {player.chips:<6} "
                f"Status: {status:<8} "
                f"Spoke: {player.spoke}"
            )
            output.append(player_str)

        output.append(f"{'='*50}\n")
        return "\n".join(output)
