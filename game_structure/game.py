from typing import List, Optional
from .deck import Deck
from .player import Player, PlayerActionError
from .betting_round import BettingRound
from .action import Action, ActionType
from .game_state import GameState
from .utils import convert_amount_in_bb


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
        for player in self.players:
            self.game_state.add_to_history(f"{player.to_phn()} ")
        self.game_state.add_to_history("\n0. ")

        # Post blinds
        self._post_blinds()

        # Update betting round with blinds
        self.current_round.pot = (
            self.parameter["small_blind"] + self.parameter["big_blind"]
        )
        self.current_round.current_bet = self.parameter["big_blind"]

        # Deal cards
        self.deck.deal_cards(self.players)

    def handle_action(self, player: Player, action: Action):
        """Handle a player's action

        Args:
            player (Player): Player making the action
            action (Action): Action to perform
        """
        player.validate_action(action, self.current_round)

        if action.type == ActionType.FOLD:
            player.fold()
        elif action.type == ActionType.CHECK:
            player.check()
        elif action.type == ActionType.CALL:
            amount_to_call = self.current_round.current_bet - player.current_bet
            player.call(amount_to_call)
            self.current_round.update_pot(amount_to_call)
        elif action.type == ActionType.BET:
            amount = player.place_bet(action.amount, action.blind_posting)
            self.current_round.update_pot(amount)
            self.current_round.set_current_bet(player.current_bet)
        elif action.type == ActionType.RAISE:
            amount = player.raise_(action.amount, action.blind_posting)
            self.current_round.update_pot(amount)
            self.current_round.set_current_bet(player.current_bet)
        elif action.type == ActionType.REVEAL:
            player.reveal()
        elif action.type == ActionType.HIDE:
            player.hide()
        else:
            raise print(f"Invalid action type: {action.type}")

        self.game_state.add_to_history(f"P{player.position}_{action.to_phn()} ")
        self._advance_game_state()

    def end_hand(self):
        """End the current hand and distribute pot"""
        winners = self._determine_winners()
        pot = self.current_round.pot
        for winner in winners:
            winner.chips += pot // len(winners)

        # TODO handle pot splitting when a player is in all-in and win

        self.game_state.add_to_history("\n")
        for player in self.players:
            self.game_state.add_to_history(f"{player.to_phn()} ")

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

            print(f"\n{current_player.name}'s turn")
            action = current_player.get_action(self.current_round)
            i = 10
            while i <= 10:
                try:
                    self.handle_action(current_player, action)
                except PlayerActionError as e:
                    i += 1
                    print(e)

            print(action)
            print(self)  # Show updated game state

        print("\nHand complete!")
        self.end_hand()

        with open("historic.txt", "w") as f:
            f.write(self.game_state.historic)

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

        for blind, player, action_type in zip(
            ["small_blind", "big_blind"],
            [sb_player, bb_player],
            [ActionType.BET, ActionType.RAISE],
        ):
            self.handle_action(
                player,
                Action(
                    action_type=action_type,
                    amount=self.parameter[blind],
                    blind_posting=True,
                ),
            )

        self.current_round.set_current_bet(self.parameter["big_blind"])

    def _get_first_to_act(self) -> int:
        """Determine first player to act"""
        return self.small_blind_position

    def _advance_game_state(self):
        """
        Advance the game state based on current conditions. Either move to the next player,
        advance the stage or end the hand
        """
        active_players = [p for p in self.players if not p.folded]

        if len(active_players) == 1 or all([p.is_all_in for p in active_players]):
            # Directly go to show down
            for _ in range(4 - self.current_round.stage):
                self._advance_stage()

        elif self.current_round.is_completed(self.players):
            if self.current_round.stage < 4:
                self._advance_stage()
            else:
                self.game_over = True
        else:
            self._get_next_player()

    def _get_next_player(self):
        """Get the next player to act"""
        self.current_round.current_player_index = (
            self.current_round.current_player_index + 1
        ) % len(self.players)

    def _advance_stage(self):
        """Advance to the next stage of the game and draw cards on the board"""
        self.current_round.next_stage()
        for player in self.players:
            player.new_stage()

        # Deal community cards
        if self.current_round.stage == 1:  # Flop
            cards = self.deck.draw_flop()
            self.game_state.add_to_history(f"|B_{''.join([c.to_phn() for c in cards])}")
            for player in self.players:
                player.hand.add_community_card(cards)

        elif self.current_round.stage in [2, 3]:  # Turn or River
            cards = self.deck.draw_turn_or_river()
            self.game_state.add_to_history(f"|B_{''.join([c.to_phn() for c in cards])}")
            for player in self.players:
                player.hand.add_community_card(cards)

        elif self.current_round.stage == 4:
            self.game_state.add_to_history("|")

        self.game_state.add_to_history(
            f"|P_{convert_amount_in_bb(self.current_round.pot, self.parameter['big_blind'])}\n"
        )
        self.game_state.add_to_history(f"{self.current_round.stage}. ")

        self.current_round.current_player_index = self._get_first_to_act()

    def _determine_winners(self) -> List[Player]:
        """Determine the winner(s) of the hand"""
        active_players = [p for p in self.players if not p.folded]
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


# TODO convert amount in blinds
# TODO fix player positions management
# TODO fix evalutation function (say straight when not having straight)
# TODO test when players fold
