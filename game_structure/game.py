from .deck import Deck
from .player import Player


class Game:

    def __init__(self, name: str = None):

        self.players = []
        self.deck = Deck()
        self.board = []
        self.folded = []
        self.parameter = {
            "name": name,
            # ... list of parameters
        }
        self.historic = ""
        self.current_player = 0
        self.pot = 0
        self.min_bet = 0
        self.current_bet = 0
        self.round = 0
        self.game_over = False
        self.dealer_position = 0  # Track dealer position
        self.small_blind_position = 1  # Small blind is left of dealer
        self.big_blind_position = 2  # Big blind is left of small blind

    def add_player(self, player: Player):
        """Add a player to the game"""
        player.position = len(self.players)  # Assign position when adding player
        self.players.append(player)

    def remove_player(self, player: Player):
        """Remove a player from the game"""
        if player in self.players:
            removed_pos = player.position
            self.players.remove(player)
            # Update positions of remaining players
            for p in self.players:
                if p.position > removed_pos:
                    p.position -= 1

    def rotate_positions(self):
        """Rotate dealer and blind positions after each hand"""
        num_players = len(self.players)
        self.dealer_position = (self.dealer_position + 1) % num_players
        self.small_blind_position = (self.dealer_position + 1) % num_players
        self.big_blind_position = (self.dealer_position + 2) % num_players

    def deal_cards(self):
        """Deal initial cards to players"""
        # Start dealing from small blind position
        current_pos = self.small_blind_position
        for _ in range(len(self.players)):
            player = next(p for p in self.players if p.position == current_pos)
            player.hand = []
            for _ in range(2):  # Assuming Texas Hold'em
                if self.deck:
                    player.hand.append(self.deck.pop())
            current_pos = (current_pos + 1) % len(self.players)

    def deal_board(self, count=1):
        """Deal cards to the board"""
        for _ in range(count):
            if self.deck:
                self.board.append(self.deck.pop())

    def next_player(self):
        """Move to the next active player"""
        # Start from player left of big blind in first round
        if self.round == 0 and self.current_player == 0:
            self.current_player = (self.big_blind_position + 1) % len(self.players)
        else:
            self.current_player = (self.current_player + 1) % len(self.players)

        while self.players[self.current_player] in self.folded:
            self.current_player = (self.current_player + 1) % len(self.players)

    def place_bet(self, amount):
        """Place a bet for the current player"""
        player = self.players[self.current_player]
        if player.chips >= amount:
            player.chips -= amount
            self.pot += amount
            self.current_bet = max(self.current_bet, amount)
            return True
        return False

    def fold_current_player(self):
        """Current player folds"""
        self.folded.append(self.players[self.current_player])
        self.next_player()

    def reset_round(self):
        """Reset the round state"""
        self.current_bet = 0
        self.min_bet = 0
        self.folded = []
        self.round += 1
        if self.round == 0:  # New hand
            self.rotate_positions()

    def check_game_over(self):
        """Check if the game is over"""
        active_players = [p for p in self.players if p not in self.folded]
        if len(active_players) == 1:
            self.game_over = True
            return True
        return False

    def get_winners(self):
        """Determine the winner(s) of the game"""
        active_players = [p for p in self.players if p not in self.folded]
        if len(active_players) == 1:
            return active_players
        # Compare hands of active players
        best_hand = -1
        winners = []
        for player in active_players:
            # Calculate hand value based on player's hole cards and board cards
            hand_value = self.evaluate_hand(player.hand + self.board)
            if hand_value > best_hand:
                best_hand = hand_value
                winners = [player]
            elif hand_value == best_hand:
                winners.append(player)
        return winners

    def distribute_pot(self, winners):
        """Distribute the pot among winners"""
        if winners:
            split_amount = self.pot // len(winners)
            for player in winners:
                player.chips += split_amount
            self.pot = 0

    def evaluate_hand(self, hand):
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

    def play(self, player, action):
        """
        Execute a player's action in the poker game.

        Args:
            player (Player): The player making the action
            action (dict): Dictionary containing action type and amount
                         {'type': 'fold'|'check'|'call'|'raise', 'amount': int}

        Returns:
            bool: True if action was valid and executed, False otherwise
        """
        if player.folded:
            return False

        action_type = action["type"].lower()
        player_position = player.position

        # Validate player's turn based on position
        if self.round == 0:  # Pre-flop
            if player_position <= self.big_blind_position and self.current_bet == 0:
                return False  # Can't act before big blind posts

        if action_type == "fold":
            player.folded = True
            return True

        elif action_type == "check":
            # Check is only valid if no bets to call
            if self.current_bet == 0:
                return True
            return False

        elif action_type == "call":
            amount_to_call = self.current_bet - player.current_bet
            if amount_to_call > player.chips:
                return False
            player.chips -= amount_to_call
            self.pot += amount_to_call
            player.current_bet = self.current_bet
            return True

        elif action_type == "raise":
            raise_amount = action["amount"]
            # Minimum raise rules vary by position and round
            min_raise = self.current_bet * 2
            if self.round == 0:  # Pre-flop
                if player_position == self.small_blind_position:
                    min_raise = self.parameter.get("small_blind", 1)
                elif player_position == self.big_blind_position:
                    min_raise = self.parameter.get("big_blind", 2)

            if raise_amount < min_raise:
                return False
            if raise_amount > player.chips:
                return False

            player.chips -= raise_amount
            self.pot += raise_amount
            self.current_bet = raise_amount
            player.current_bet = raise_amount
            return True

        return False

    def __str__(self):
        """Return a string representation of the current game state"""
        output = []

        # Game info header
        output.append(f"\n{'='*50}")
        output.append(f"Game: {self.parameter['name']}")
        output.append(f"Round: {self.round}")
        output.append(f"Pot: {self.pot}")
        output.append(f"Current Bet: {self.current_bet}")

        # Board cards
        board_str = (
            " ".join([str(card) for card in self.board]) if self.board else "No cards"
        )
        output.append(f"\nBoard: {board_str}")

        # Player information
        output.append("\nPlayers:")
        for player in self.players:
            position_labels = []
            if player.position == self.dealer_position:
                position_labels.append("D")
            if player.position == self.small_blind_position:
                position_labels.append("SB")
            if player.position == self.big_blind_position:
                position_labels.append("BB")

            position_str = f"[{', '.join(position_labels)}]" if position_labels else ""

            status = "FOLDED" if player.folded else "ACTIVE"
            cards = (
                " ".join([str(card) for card in player.hand])
                if player.hand
                else "XX XX"
            )

            player_str = (
                f"{player.name} {position_str}: "
                f"Chips: {player.chips} "
                f"Cards: {cards} "
                f"Status: {status}"
            )

            if player.position == self.current_player:
                player_str = "-> " + player_str
            output.append(player_str)

        output.append(f"{'='*50}\n")
        return "\n".join(output)

    def __repr__(self):
        return self.__str__()
