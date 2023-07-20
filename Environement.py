import random

ALL_CARDS = [(i, c) for c in ['Ca', 'Co', 'Pi', 'Tr'] for i in range(1, 14)]

class deck():
    def __init__(self):
        self.stack = ALL_CARDS.copy()
        self.distribuated_cards = []
        self.nb_remaining_cards = 52

    def reset(self):
        self.__init__()

    def shuffle(self):
        random.shuffle(self.stack)
    
    def distribute(self, nb_stacks, nb_cards):
        dist_stacks = [[] for _ in range(nb_stacks)]
        if self.nb_remaining_cards <= nb_cards*nb_stacks:
            print("Le nombre de cartes restantes dans le paquet n'est pas suffisant")
        
        else:
            for _ in range(nb_cards):
                for j in range(nb_stacks):
                    dist_card = self.stack.pop()
                    dist_stacks[j].append(dist_card)
                    self.distribuated_cards.append(dist_card)
                    self.nb_remaining_cards -= 1

        return dist_stacks


class player():
    def __init__(self, name="", chip_stack=100):
        self.name = name
        self.__cards = []
        self.chip_stack = chip_stack
        self.bet = 0
    
    def show_card(self):
        print(self.__cards)

    def set_cards(self, pair_of_cards: list[tuple]):
        self.__cards = pair_of_cards
    
    def get_cards(self):
        return self.__cards

    
class board():
    # Objet possedant : pot + cartes + défausse
    def __init__(self):
        self.cards = []
        self.bin = []
        self.pot = 0


class table():
    #plusieurs joueurs, un pot, un board, un deck,..
    def __init__(self) -> None:
        pass

class game():
    # Objet possédant les valeur des blindes, les prix, ect
    def __init__(self) -> None:
        pass