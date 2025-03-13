from .deck import Deck


class Game:

    def __init__(
        self,
    ):

        self.players = []
        self.deck = Deck()
        self.board = []
        self.folded = []
        self.parameter = {
            # liste of param
        }
