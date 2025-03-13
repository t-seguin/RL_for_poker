from .deck import Deck


class Game:

    def __init__(self, name):

        self.players = []
        self.deck = Deck()
        self.board = []
        self.folded = []
        self.parameter = {
            "name": name if name else None,
            # liste of param
        }
