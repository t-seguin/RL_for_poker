from typing import List, Optional
from .deck import Deck
from .player import Player
from .betting_round import BettingRound
from .action import Action, ActionType
from .game_state import GameState
import time


class Game:
    """Main game controller coordinating all components"""

    def __init__(self, name: str = None, pov: int = -1):
        """Initialize a poker game

        Args:
            name (str, optional): Name of the game
            pov (int, optional): Point of view player position (-1 for omniscient)
        """
        self.name = name
        self.pov = pov
        self.deck = Deck()
        self.players: List[Player] = []
        self.dealer_position = 0
        self.small_blind_position = 1  # TODO create a class that handle player position
        self.big_blind_position = 2
        self.current_round: Optional[BettingRound] = None
        self.hand_number = 0
        self.game_over = False
        self.game_state = GameState()
        self.parameter = {"small_blind": 1, "big_blind": 2}

    def add_player(self, player: Player):
        """Add a player to the game"""
        player.position = len(self.players)
        self.players.append(player)

    def set_pov(self, player_name: str):
        """Set the point of view player"""
        self.pov = [p.name for p in self.players].index(player_name)

    def remove_player(self, player: Player):
        """Remove a player from the game"""
        if player in self.players:
            removed_pos = player.position
            self.players.remove(player)
            for p in self.players:
                if p.position > removed_pos:
                    p.position -= 1

    def start_new_hand(self):
        """Initialize a new hand"""
        self.hand_number += 1
        self.deck = Deck()
        self.deck.shuffle()
        self._rotate_positions()

        # Reset player states
        for player in self.players:
            player.reset_hand()

        # Initialize betting round before posting blinds
        self.current_round = BettingRound(stage=0)
        self.current_round.current_player_index = self._get_first_to_act()

        # Post blinds
        self._post_blinds()

        # Update betting round with blinds
        self.current_round.pot = (
            self.parameter["small_blind"] + self.parameter["big_blind"]
        )
        self.current_round.current_bet = self.parameter["big_blind"]

        # Deal cards
        self._deal_cards()

    def _rotate_positions(self):
        """Rotate dealer and blind positions after each hand"""
        num_players = len(self.players)
        self.dealer_position = (self.dealer_position + 1) % num_players
        self.small_blind_position = (self.small_blind_position + 1) % num_players
        self.big_blind_position = (self.big_blind_position + 1) % num_players

    def _post_blinds(self):
        """Post small and big blinds"""
        sb_player = self.players[self.small_blind_position]
        bb_player = self.players[self.big_blind_position]

        # Post small blind
        sb_amount = self.parameter["small_blind"]
        sb_player.place_bet(sb_amount, blind_bet=True)

        # Post big blind
        bb_amount = self.parameter["big_blind"]
        bb_player.place_bet(bb_amount, blind_bet=True)

        self.current_round.set_current_bet(bb_amount)

    def _deal_cards(self):
        """Deal cards to players"""
        # Deal hole cards
        for _ in range(2):
            for player in self.players:
                card = self.deck.draw()
                player.hand.add_hole_card(card)

    def _get_first_to_act(self) -> int:
        """Determine first player to act"""
        if self.current_round.stage == 0:  # Pre-flop
            return (self.big_blind_position + 1) % len(self.players)
        return self.small_blind_position

    def handle_action(self, player: Player, action: Action) -> bool:
        """Handle a player's action

        Args:
            player (Player): Player making the action
            action (Action): Action to perform

        Returns:
            bool: True if action was successful
        """
        if not self._validate_action(player, action):
            return False

        success = False
        if action.type == ActionType.FOLD:
            success = self._handle_fold(player)
        elif action.type == ActionType.CHECK:
            success = self._handle_check(player)
        elif action.type == ActionType.CALL:
            success = self._handle_call(player)
        elif action.type == ActionType.RAISE:
            success = self._handle_raise(player, action.amount)
        else:
            raise print(f"Invalid action type: {action.type}")

        if success:
            self._advance_game_state()

        return success

    def _validate_action(self, player: Player, action: Action) -> bool:
        """Validate if an action is legal

        Args:
            player (Player): Player making the action
            action (Action): Action to validate

        Returns:
            bool: True if action is valid
        """
        if player.position != self.current_round.current_player_index:
            print(f"Not {player.name}'s turn to act")
            return False

        if player.folded:
            print(f"Player {player.name} has already folded")
            return False

        if action.type == ActionType.RAISE:
            if action.amount <= self.current_round.current_bet and action.amount != -1:
                print("Raise amount must be greater than current bet")
                return False
            if action.amount > player.chips + player.current_bet:
                print("Not enough chips to raise")
                return False

        return True

    def _handle_fold(self, player: Player) -> bool:
        """Handle fold action, return False if the player cannot fold and True if success"""
        player.fold()
        self.game_state.add_to_history(f"{player.name} folds")
        return True

    def _handle_check(self, player: Player) -> bool:
        """Handle check action, return False if the player cannot check and True if success"""
        if self.current_round.current_bet > player.current_bet:
            print("Cannot check when there is a bet to call")
            return False
        player.speak()
        self.game_state.add_to_history(f"{player.name} checks")
        return True

    def _handle_call(self, player: Player) -> bool:
        """Handle call action, return False if the player cannot call and True if success"""
        amount_to_call = self.current_round.current_bet - player.current_bet

        if amount_to_call > player.chips:
            amount_to_call = player.chips

        if (
            not self.current_round.current_bet > player.current_bet
            or not player.place_bet(amount_to_call)
        ):
            return False

        self.current_round.update_pot(amount_to_call)
        self.game_state.add_to_history(f"{player.name} calls {amount_to_call}")
        return True

    def _handle_raise(self, player: Player, amount: int) -> bool:
        """Handle raise action, return False if the player cannot raise and True if success

        Args:
            player (Player): Player making the raise
            amount (int): Amount to raise. If = -1, the player raise to all-in

        Returns:
            bool: True if raise was successful
        """
        if amount == -1:
            amount = player.chips

        if not player.place_bet(amount):
            return False

        self.current_round.update_pot(
            player.current_bet - self.current_round.current_bet
        )
        self.current_round.set_current_bet(player.current_bet)
        self.game_state.add_to_history(f"{player.name} raises to {player.current_bet}")
        return True

    def _handle_reveal(self, player: Player) -> bool:
        """When the hand is over, reveal the player's hand if no other player has revealed a
        stronger hand.

        Args:
            player (Player): Player revealing their hand

        Returns:
            bool: True if reveal was successful
        """
        hand_value = player.hand.evaluate()
        revealed_players = [p for p in self.players if p.revealed]
        if any(
            hand_value < other_hand_value
            for other_hand_value in [p.hand.evaluate() for p in revealed_players]
        ):
            return False
        player.reveal()
        self.game_state.add_to_history(
            f"{player.name} reveals {player.hand} ({self.game_state._get_hand_name(hand_value)})"
        )
        return True

    def _advance_game_state(self):
        """
        Advance the game state based on current conditions. Either move to the next player,
        advance the stage or end the hand
        """
        active_players = [p for p in self.players if not p.folded]

        if len(active_players) == 1:
            self._end_hand(active_players)

        elif self.current_round.is_complete(self.players):
            if self.current_round.stage < 3:
                self._advance_stage()
            else:
                self._end_hand(self._determine_winners(active_players))
        else:
            self._get_next_player()

    def _get_next_player(self):
        """Get the next player to act"""
        self.current_round.current_player_index = (
            self.current_round.current_player_index + 1
        ) % len(self.players)

    def _advance_stage(self):
        """Advance to the next stage of the game"""
        self.current_round.next_stage()
        for player in self.players:
            player.new_stage()

        # Deal community cards
        if self.current_round.stage == 1:  # Flop
            for _ in range(3):
                card = self.deck.draw()
                for player in self.players:
                    player.hand.add_community_card(card)

        elif self.current_round.stage in [2, 3]:  # Turn or River
            card = self.deck.draw()
            for player in self.players:
                player.hand.add_community_card(card)

        self.current_round.current_player_index = self._get_first_to_act()

    def _determine_winners(self, active_players: List[Player]) -> List[Player]:
        """Determine the winner(s) of the hand"""
        if len(active_players) == 1:
            return active_players

        best_hand = -1
        winners = []

        for player in active_players:
            hand_value = player.hand.evaluate()
            if hand_value > best_hand:
                best_hand = hand_value
                winners = [player]
            elif hand_value == best_hand:
                winners.append(player)

        return winners

    def _end_hand(self, winners: List[Player]) -> str:
        """End the current hand and distribute pot"""
        active_players = [p for p in self.players if not p.folded]
        for player in active_players:
            self._handle_reveal(player)

        pot = self.current_round.pot
        for winner in winners:
            winner.chips += pot // len(winners)

        # TODO handle the case when a player is in all-in
        message = f"{', '.join([winner.name for winner in winners])} win {pot//len(winners)} chips"

        self.game_state.add_to_history(message)
        self.game_over = True

        return message

    def _update_game_state(self):
        """Update the game state for display"""
        community_cards = self.players[0].hand.community_cards if self.players else []

        self.game_state.update(
            players=self.players,
            community_cards=community_cards,
            current_round=self.current_round,
            dealer_position=self.dealer_position,
            small_blind_position=self.small_blind_position,
            big_blind_position=self.big_blind_position,
            hand_number=self.hand_number,
            game_over=self.game_over,
            pov=self.pov,
        )

    def __str__(self):
        """Return string representation of the game"""
        self._update_game_state()
        return str(self.game_state)

    def start_interactive_hand(self, debug_mode=False):
        """Start an interactive game session

        Args:
            debug_mode (bool): If True, allows controlling all players. If False, only controls POV
                player.
        """
        print("\nStarting new poker hand...")
        self.start_new_hand()
        print(self)

        while not self.game_over:
            current_player = next(
                p
                for p in self.players
                if p.position == self.current_round.current_player_index
            )

            # Check if current player should be controlled by user
            is_user_control = debug_mode or (
                not debug_mode and current_player.position == self.pov
            )

            if is_user_control:
                # Get user input for action
                print(f"\n{current_player.name}'s turn")
                print(f"Current bet: {self.current_round.current_bet}")
                print(f"Your chips: {current_player.chips}")
                print("Available actions: fold, check, call, raise")

                while True:
                    action = Action(
                        *input("Enter your action: ").lower().strip().split(" ")
                    )
                    success = self.handle_action(current_player, action)
                    if success:
                        print(action)
                        break
                    else:
                        print("Action not allowed, try again")
            else:
                # Placeholder for AI/automatic player actions
                print(f"\n{current_player.name} thinking...")
                time.sleep(1)
                action = current_player.get_action(self.current_round)
                success = self.handle_action(current_player, action)
                if success:
                    print(action)
                else:
                    raise ValueError(f"Invalid action: {action}")
                time.sleep(1)

            print(self)  # Show updated game state

            # Check if hand is over
            if self.game_over:
                break

        print("\nHand complete!")
        with open("historic.txt", "w") as f:
            f.write(self.game_state.historic)
