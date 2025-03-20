from game_structure import Game, HumanPlayer, AIPlayer

game = Game(name="test")

game.add_player(HumanPlayer("theo", 100))
game.add_player(AIPlayer("catalina", 100))
game.add_player(AIPlayer("alex", 100))

game.set_pov("theo")

game.start_interactive_hand(debug_mode=False)
