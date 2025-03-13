from .deck import Deck
from .player import Player


class Table:
    def __init__(self):
        self.players = []
        self.dealer_position = 0  # Track dealer position
        self.small_blind_position = 1  # Small blind is left of dealer
        self.big_blind_position = 2  # Big blind is left of small blind

    def add_player(self, player: Player):
        """Add a player to the table"""
        player.position = len(self.players)  # Assign position when adding player
        self.players.append(player)

    def remove_player(self, player: Player):
        """Remove a player from the table"""
        if player in self.players:
            removed_pos = player.position
            self.players.remove(player)
            # Update positions of remaining players
            for p in self.players:
                if p.position > removed_pos:
                    p.position -= 1

    def get_first_to_act_preflop(self):
        """Determine first player to act pre-flop based on number of players"""
        num_players = len(self.players)
        # Position after BB is first to act
        return (self.big_blind_position + 1) % num_players

    def rotate_positions(self):
        """Rotate dealer and blind positions after each hand"""
        num_players = len(self.players)
        self.dealer_position = (self.dealer_position + 1) % num_players
        self.small_blind_position = (self.small_blind_position + 1) % num_players
        self.big_blind_position = (self.big_blind_position + 1) % num_players

    def get_position_name(self, position):
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


class Game:
    def __init__(self, table: Table, name: str = None):
        self.table = table
        self.deck = Deck()
        self.board = []
        self.folded = []
        self.parameter = {
            "name": name,
            "small_blind": 1,  # Default small blind amount
            "big_blind": 2,  # Default big blind amount
        }
        self.historic = ""
        self.current_player = -1
        self.pot = 0
        self.min_bet = 0
        self.current_bet = 0
        self.hand_number = 0  # Number of hands played
        self.stage = 0  # 0=preflop, 1=flop, 2=turn, 3=river
        self.game_over = False

    def __str__(self):
        """Return a string representation of the current game state"""
        output = []

        # Game info header
        output.append(f"\n{'='*50}")
        output.append(f"Game: {self.parameter['name']}")
        output.append(f"Hand #: {self.hand_number}")
        stage_names = ["Pre-flop", "Flop", "Turn", "River"]
        output.append(f"Stage: {stage_names[self.stage]}")
        output.append(f"Pot: {self.pot}")
        output.append(f"Current Bet: {self.current_bet}")

        # Board cards
        board_str = (
            " ".join([str(card) for card in self.board]) if self.board else "No cards"
        )
        output.append(f"\nBoard: {board_str}")

        # Player information
        output.append("\nPlayers:")
        for player in self.table.players:
            position_name = self.table.get_position_name(player.position)
            position_str = f"[{position_name}]" if position_name else ""

            status = "FOLDED" if player.folded else "ACTIVE"

            # Format cards with brackets and better spacing
            if player.hand:
                cards = f"[{str(player.hand[0])+']':<4} [{str(player.hand[1])}]"
            else:
                cards = "[XX] [XX]"

            # Format player info with aligned columns
            player_str = (
                f"{player.name:<15} "  # Name left-aligned, 15 chars
                f"{position_str:<7} "  # Position left-aligned, 6 chars
                f"Chips: {player.chips:<6} "  # Chips left-aligned, 6 chars
                f"Cards: {cards:<12} "  # Cards left-aligned, 15 chars
                f"Status: {status}"
            )

            if player.position == self.current_player:
                player_str = f"-> {player_str:<{len(player_str)}}"
            else:
                player_str = f"   {player_str:<{len(player_str)}}"
            output.append(player_str)

        output.append(f"{'='*50}\n")
        return "\n".join(output)

    def __repr__(self):
        return self.__str__()

    def _deal_cards(self):
        """Deal initial cards to players and post blinds"""
        self.deck.shuffle()  # Shuffle deck before dealing

        # Post blinds
        small_blind_player = next(
            p
            for p in self.table.players
            if p.position == self.table.small_blind_position
        )
        big_blind_player = next(
            p for p in self.table.players if p.position == self.table.big_blind_position
        )

        # Take small blind
        sb_amount = self.parameter["small_blind"]
        small_blind_player.chips -= sb_amount
        small_blind_player.current_bet = sb_amount
        self.pot += sb_amount

        # Take big blind
        bb_amount = self.parameter["big_blind"]
        big_blind_player.chips -= bb_amount
        big_blind_player.current_bet = bb_amount
        self.pot += bb_amount
        self.current_bet = bb_amount

        # Start dealing from small blind position
        current_pos = self.table.small_blind_position
        for _ in range(len(self.table.players)):
            player = next(p for p in self.table.players if p.position == current_pos)
            player.hand = []
            for _ in range(2):  # Assuming Texas Hold'em
                if self.deck:
                    player.hand.append(self.deck.pop())
            current_pos = (current_pos + 1) % len(self.table.players)

    def _deal_board(self, count=1):
        """Deal cards to the board"""
        for _ in range(count):
            if self.deck:
                self.board.append(self.deck.pop())

    def _get_winners(self):
        """Determine the winner(s) of the game"""
        active_players = [p for p in self.table.players if p not in self.folded]
        if len(active_players) == 1:
            return active_players

        # Compare hands of active players
        best_hand = -1
        winners = []
        for player in active_players:
            # Calculate hand value based on player's hole cards and board cards
            hand_value = self._evaluate_hand(player.hand + self.board)
            if hand_value > best_hand:
                best_hand = hand_value
                winners = [player]
            elif hand_value == best_hand:
                winners.append(player)

        # Distribute pot to winners
        self._distribute_pot(winners)
        return winners

    def _distribute_pot(self, winners):
        """Distribute the pot among winners"""
        if winners:
            split_amount = self.pot // len(winners)
            for player in winners:
                player.chips += split_amount
            # Handle remainder chips if any
            remainder = self.pot % len(winners)
            if remainder > 0:
                winners[0].chips += remainder
            self.pot = 0

    def _evaluate_hand(self, hand):
        """Evaluate a hand using a poker hand evaluator"""
        # Sort cards by rank
        sorted_hand = sorted(hand, key=lambda x: x.rank, reverse=True)

        # Check for flush
        suits = [card.suit for card in sorted_hand]
        is_flush = len(set(suits)) == 1

        # Check for straight
        ranks = [card.rank for card in sorted_hand]
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

    def _validate_player_turn(self, player: Player) -> bool:
        """Validate if it's the player's turn to act"""
        if player.position != self.current_player:
            print(f"Not {player.name}'s turn to act")
            return False
        if player.folded:
            print(f"Player {player.name} has already folded")
            return False
        return True

    def _validate_preflop_action(self, player_position: int) -> bool:
        """Validate pre-flop specific rules"""
        if self.stage == 0:
            if (
                player_position <= self.table.big_blind_position
                and self.current_bet == 0
            ):
                print("Cannot act before big blind posts in pre-flop")
                return False
        return True

    def _handle_fold(self, player: Player) -> bool:
        """Handle fold action"""
        player.folded = True
        return True

    def _handle_check(self, player: Player) -> bool:
        """Handle check action"""
        if self.current_bet == 0 or (
            player.position == self.table.big_blind_position
            and self.current_bet == player.current_bet
        ):
            return True
        print(
            f"Cannot check when there is a bet to call (current bet: {self.current_bet})"
        )
        return False

    def _handle_call(self, player: Player) -> bool:
        """Handle call action"""
        amount_to_call = self.current_bet - player.current_bet
        if amount_to_call > player.chips:
            print(
                f"Not enough chips to call. Need {amount_to_call} but only has {player.chips}"
            )
            return False
        player.chips -= amount_to_call
        self.pot += amount_to_call
        player.current_bet = self.current_bet
        return True

    def _handle_raise(self, player: Player, raise_to_amount: int) -> bool:
        """Handle raise action"""
        min_raise = self.current_bet * 2
        if self.stage == 0:  # Pre-flop
            if player.position == self.table.small_blind_position:
                min_raise = self.parameter.get("small_blind", 1)
            elif player.position == self.table.big_blind_position:
                min_raise = self.parameter.get("big_blind", 2)

        if raise_to_amount < min_raise:
            print(
                f"Raise amount {raise_to_amount} is below minimum raise of {min_raise}"
            )
            return False
        if raise_to_amount > player.chips + player.current_bet:
            print(
                f"Not enough chips to raise. Trying to raise to {raise_to_amount} but only has "
                f"{player.chips + player.current_bet} total"
            )
            return False

        amount_to_add = raise_to_amount - player.current_bet
        player.chips -= amount_to_add
        self.pot += amount_to_add
        self.current_bet = raise_to_amount
        player.current_bet = raise_to_amount
        return True

    def _should_advance_stage(self, active_players: list) -> bool:
        """Determine if betting round is complete and stage should advance"""
        all_bets_matched = all(
            p.current_bet == self.current_bet for p in active_players
        )
        if not all_bets_matched:
            return False

        # All stages, the last player to speak has the right to act
        if self.current_player == active_players[-1].position:
            return False

        # Pre-flop: big blind gets to act even if bets are matched
        if self.stage == 0 and self.current_player == self.table.big_blind_position:
            return False

        # Post-flop: small blind gets to act even if bets are matched
        if self.stage >= 1 and self.current_player == self.table.small_blind_position:
            return False

        return True

    def _advance_stage(self):
        """Handle advancing to next stage of the game"""
        # Reset betting amounts
        for p in self.table.players:
            p.current_bet = 0
        self.current_bet = 0

        # Deal appropriate cards for each stage
        if self.stage == 0:  # Pre-flop -> Flop
            self.stage = 1
            for _ in range(3):
                self.board.append(self.deck.draw())
        elif self.stage == 1:  # Flop -> Turn
            self.stage = 2
            self.board.append(self.deck.draw())
        elif self.stage == 2:  # Turn -> River
            self.stage = 3
            self.board.append(self.deck.draw())
        elif self.stage == 3:  # River -> End hand
            self.finish_hand()

        # Reset to first active player after dealer
        next_position = (self.table.dealer_position + 1) % len(self.table.players)
        while True:
            if not self.table.players[next_position].folded:
                self.current_player = next_position
                break
            next_position = (next_position + 1) % len(self.table.players)

    def _move_to_next_active_player(self, current_position: int):
        """Move to next non-folded player"""
        next_position = (current_position + 1) % len(self.table.players)
        while next_position != current_position:
            if not self.table.players[next_position].folded:
                self.current_player = next_position
                break
            next_position = (next_position + 1) % len(self.table.players)

    def _get_current_player(self):
        """Get the current player based on stage and position"""
        if self.stage == 0:  # Pre-flop
            return self.table.get_first_to_act_preflop()
        else:
            return self.table.small_blind_position

    def start_game(self, rotate_positions=True):
        """Initialize the game state"""
        # Randomly rotate initial positions
        import random

        if rotate_positions:
            random_rotation = random.randint(0, len(self.table.players) - 1)
            for _ in range(random_rotation):
                self.table.rotate_positions()

        self.current_player = self._get_current_player()
        self._deal_cards()

    def play(self, player: Player, action: dict) -> bool:
        """
        Execute a player's action in the poker game.

        Args:
            player (Player): The player making the action
            action (dict): Dictionary containing action type and amount
                         {'type': 'fold'|'check'|'call'|'raise', 'amount': int}

        Returns:
            bool: True if action was valid and executed, False otherwise
        """
        # Validate the action
        if not self._validate_player_turn(player):
            return False

        if not self._validate_preflop_action(player.position):
            return False

        # Handle the action
        action_type = action["type"].lower()
        action_success = False

        if action_type == "fold":
            action_success = self._handle_fold(player)
        elif action_type == "check":
            action_success = self._handle_check(player)
        elif action_type == "call":
            action_success = self._handle_call(player)
        elif action_type == "raise":
            action_success = self._handle_raise(player, action["amount"])
        else:
            print(f"Invalid action type: {action_type}")

        # Handle progression if action was successful
        if action_success:
            active_players = [p for p in self.table.players if not p.folded]

            if self._should_advance_stage(active_players):
                self._advance_stage()
            else:
                self._move_to_next_active_player(player.position)

        return action_success

    def finish_hand(self):
        """Distribute pot among winners and move to next hand"""
        # Get winners and distribute pot
        winners = self._get_winners()
        self._distribute_pot(winners)

    def new_hand(self):
        """Reset the hand state"""
        self.current_bet = 0
        self.min_bet = 0
        self.folded = []
        self.stage = 0  # Reset to pre-flop
        self.hand_number += 1  # Increment hand count

        # New hand
        self.deck = Deck()  # New shuffled deck
        self.board = []  # Clear board
        self.pot = 0  # Reset pot

        # Reset player states
        for player in self.table.players:
            player.folded = False
            player.hand = []
            player.current_bet = 0

        self.table.rotate_positions()  # Rotate dealer

        # Set current player based on stage and position
        self.current_player = self._get_current_player()

        self._deal_cards()  # Deal new hands and post blinds
