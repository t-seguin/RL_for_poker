from  Environement import *

BB = 10
player_stack = 300
nb_round = 5
nb_players = 2

P1 = player(name="Alice", chip_stack=player_stack)
P2 = player(name="Bob", chip_stack=player_stack)

table = table(nb_players=2)
table.add_players([P1, P2])

D = deck()

for _ in range(nb_round):

    ## Distibution des cartes
    D.shuffle()
    player_cards = D.distribute(nb_stacks=nb_players, nb_cards=2)
    for i, p in enumerate(table.players):
        p.set_cards(player_cards[i])
    
    ## Blindes & Ante
    id_SB = (table.get_first_to_talk() + 1)%table.nb_players
    id_BB = (id_SB + 1)%table.nb_players
    table.bet_from_player(player_id=id_SB, bet_amount=BB//2)
    table.bet_from_player(player_id=id_BB, bet_amount=BB)
    
    ## Actions de chaque joueurs
    





