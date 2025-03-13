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
    
    def show_card(self):
        print(self.__cards)

    def set_cards(self, pair_of_cards: list[tuple]):
        self.__cards = pair_of_cards
    
    def get_cards(self):
        return self.__cards


class table():
    #plusieurs joueurs, un pot, un board, un deck, le bouton
    def __init__(self, nb_max_players=6):
        self.players = {}
        self.dealer = 0
        self.board = []
        self.bin = []
        self.pot = 0
        self.nb_players=2
        self.players_bet = {}
        self.player_to_speak = self.get_first_to_talk()
        self.__nb_max_players=nb_max_players
    
    def add_players(self, players:list[player] or player):
        if type(players) != list:
            players=[players]
        for i, p in enumerate(players):
            self.players[i] = p
            self.players_bet[i] = 0
            self.nb_players = len(self.players)

    def remove_player(self):
        pass ## TO COMPLETE

    def get_first_to_talk(self):
        return (self.dealer + 3)%self.nb_players
    
    def is_bet_over(self):
        pass ##TO COMPLETE

    def bet_from_player(self, player_id, bet_amount):
        self.players_bet[player_id] = bet_amount
        self.players[player_id].chip_stack -= bet_amount
    
    def next(self):
        self.player_to_speak += 1
        self.player_to_speak%self.nb_players


    def print_table(self):
        board_length = 5 + 15*self.nb_players
        print('+'+board_length*'-'+'+')
        # print(f'| BB : {self.BB:<boad_lenght-6}|')   PEUT ETRE FAIRE UNE CLASSE "GAME" POUR AVOIR self.BB
        print('|'+board_length*' '+'|')
        print('|'+f'POT : {self.pot}'.center(board_length, ' ')+'|')
        print('|'+board_length*' '+ '|')
        print('|'+f'CARDS : {self.board}'.center(board_length, ' ')+'|')
        print('|'+ board_length*' '+'|')
        print('|     ', end='')
        for i in range(self.nb_players): 
            print(f'{self.players_bet[i]}'.center(10, ' ')+5*' ', end='') 
        print('|')
        print('|'+board_length*' '+'|')
        print('|     ', end='')
        for i in range(self.nb_players):
            print(f'{self.players[i].name}'.center(10, ' ')+5*' ', end='')
        print('|')
        print('|     ', end='')
        for i in range(self.nb_players):
            print(f'{self.players[i].chip_stack}'.center(10, ' ')+5*' ', end='')
        print('|')
        gap_length = 9 + board_length*self.player_to_speak//self.nb_players - self.player_to_speak
        print('|'+gap_length*' '+'^'+(board_length-gap_length-1)*' '+'|')
        print('|     ', end='')
        for i in range(self.nb_players):
            if self.dealer == i:
                print('Dealer'.center(10, ' ')+5*' ', end='')
            elif self.dealer == i-1:
                print('SB'.center(10, ' ')+5*' ', end='')
            elif self.dealer == i-2:
                print('BB'.center(10, ' ')+5*' ', end='')
            else:
                print(15*' ', end='')
        print('|')
        print('+'+board_length*'-'+'+')
    

if __name__ == "__main__":

    P1 = player(name="Alice", chip_stack=200)
    P2 = player(name="Bob", chip_stack=200)
    P3 = player(name="Carl", chip_stack=100)
    P4 = player(name="Dany", chip_stack=1000)
    P5 = player(name="Emma", chip_stack=300)
    P6 = player(name="Fernand", chip_stack=50)
    T = table()
    T.add_players([P1, P2, P3, P4, P5, P6])
    T.player_to_speak = 1
    T.print_table()