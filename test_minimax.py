from game.reversiGame import ReversiGame
from game.reversiBoard import ReversiBoard
from players.minimax import MinimaxPlayer
from players.badPlayer import BadPlayer
from players.greedy import GreedyPlayer
from game.tokens import StackToken


minimax = MinimaxPlayer(
    name="minimax_base",
    max_time=1,
)

weights_1 = MinimaxPlayer(
    name="weights_1",
    max_time=1,
    custom_weights={
        "apertura": {
            "corner": 0.6785,
            "mob": 0.5875,
            "stable": 0.5912,
            "parity": 0.5108,
            "pos": 0.6347,
        },
        "medio": {
            "corner": 0.3812,
            "mob": 0.5799,
            "stable": 0.3923,
            "parity": 0.4637,
            "pos": 0.5751,
        },
        "final": {
            "corner": 0.5735,
            "mob": 0.4327,
            "stable": 0.7425,
            "parity": 0.7244,
            "pos": 0.5869,
        },
    },
)

weights_2 = MinimaxPlayer(
    name="weights_2",
    max_time=1,
    custom_weights={
        "apertura": {
            "corner": 0.3226,
            "mob": 0.661,
            "stable": 0.4443,
            "parity": 0.2362,
            "pos": 0.5166,
        },
        "medio": {
            "corner": 0.6096,
            "mob": 0.4591,
            "stable": 0.4478,
            "parity": 0.6536,
            "pos": 0.5919,
        },
        "final": {
            "corner": 0.398,
            "mob": 0.689,
            "stable": 0.1431,
            "parity": 0.6418,
            "pos": 0.3218,
        },
    },
)

heuristic_1 = MinimaxPlayer(
    name="heuristic_1",
    max_time=1,
    custom_weights={
        "apertura": {"corner": 1, "mob": 0, "stable": 0, "parity": 0, "pos": 0},
        "medio": {"corner": 1, "mob": 0, "stable": 0, "parity": 0, "pos": 0},
        "final": {"corner": 1, "mob": 0, "stable": 0, "parity": 0, "pos": 0},
    },
)

heuristic_2 = MinimaxPlayer(
    name="heuristic_2",
    max_time=1,
    custom_weights={
        "apertura": {"corner": 1, "mob": 1, "stable": 0, "parity": 0, "pos": 0},
        "medio": {"corner": 1, "mob": 1, "stable": 0, "parity": 0, "pos": 0},
        "final": {"corner": 1, "mob": 1, "stable": 0, "parity": 0, "pos": 0},
    },
)

heuristic_3 = MinimaxPlayer(
    name="heuristic_3",
    max_time=1,
    custom_weights={
        "apertura": {"corner": 1, "mob": 1, "stable": 1, "parity": 0, "pos": 0},
        "medio": {"corner": 1, "mob": 1, "stable": 1, "parity": 0, "pos": 0},
        "final": {"corner": 1, "mob": 1, "stable": 1, "parity": 0, "pos": 0},
    },
)

heuristic_4 = MinimaxPlayer(
    name="heuristic_4",
    max_time=1,
    custom_weights={
        "apertura": {"corner": 1, "mob": 1, "stable": 1, "parity": 1, "pos": 0},
        "medio": {"corner": 1, "mob": 1, "stable": 1, "parity": 1, "pos": 0},
        "final": {"corner": 1, "mob": 1, "stable": 1, "parity": 1, "pos": 0},
    },
)

heuristic_5 = MinimaxPlayer(
    name="heuristic_5",
    max_time=1,
    custom_weights={
        "apertura": {"corner": 1, "mob": 1, "stable": 1, "parity": 1, "pos": 1},
        "medio": {"corner": 1, "mob": 1, "stable": 1, "parity": 1, "pos": 1},
        "final": {"corner": 1, "mob": 1, "stable": 1, "parity": 1, "pos": 1},
    },
)

time_3 = MinimaxPlayer(
    name="time_3",
    max_time=10,
)

time_10 = MinimaxPlayer(
    name="time_10",
    max_time=10,
)

greedy = GreedyPlayer(
    name="greedy"
)

bad = BadPlayer(
    name="bad_player",
    max_time=1
)

all_players = [weights_1, weights_2, heuristic_1, heuristic_2, heuristic_3, heuristic_4, heuristic_5, time_3, time_10]
oponents = [minimax, greedy, bad]

for player in all_players:
    for oponent in oponents+all_players:
        
        if player.name == oponent.name:
            continue
        
        game = ReversiGame()
        board = ReversiBoard()

        game.players(player1=player, player2=oponent)
        player.tokens = StackToken("B")
        oponent.tokens = StackToken("R")
        
        game.play_for_algorithms(board)
