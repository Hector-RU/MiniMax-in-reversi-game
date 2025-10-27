import math
from copy import deepcopy
from typing import List, Tuple, Optional
import time
import tracemalloc


from players.player import Player
from game.reversiBoard import ReversiBoard, opponent  # <-- Importamos ReversiBoard Y la función opponent
from game.tokens import Token


class GreedyPlayer(Player):
    
    TYPE_ = "greedy"
    
    def __init__(self, name="greedy", depth=math.inf, max_time=math.inf, 
                enabled_heuristics: Optional[List[str]] = None,
                custom_weights: Optional[dict] = None):
        
        super().__init__(name)
        self.max_depth = depth  
        self.enabled_heuristics = set(enabled_heuristics) if enabled_heuristics else None
        self.custom_weights = custom_weights
        self.max_time = max_time
        self.ejecution_time = 0
        self.nodes_expanded = 0
        self.depth_explored = 0
        self.turns_played = 0
        self.max_ram_usage = 0
        
    def reset(self):
        self.ejecution_time = 0
        self.nodes_expanded = 0
        self.depth_explored = 0
        self.turns_played = 0
        self.max_ram_usage = 0
        
        
    def play(self, board: ReversiBoard) -> Tuple[int, int]:
        """
        Punto de entrada principal. Encuentra el mejor movimiento a profundidad 1.
        """
        tracemalloc.start()
        self.turns_played += 1
        possible_moves = board.posible_movements(self.tokens.color)
        self.time_start = time.time()
        
        
        if not possible_moves:
            return None
        
        best_move = possible_moves[0]
        best_score = -math.inf

        for move in possible_moves:
            x, y = move
            
            child_board = deepcopy(board)
            self.nodes_expanded += 1
            child_board.insert_play(x, y, Token(self.tokens.color))
            
            score = child_board.evaluate(self.tokens.color, enabled_heuristics=self.enabled_heuristics,
                        custom_weights=self.custom_weights)
            
            if score > best_score:
                best_score = score
                best_move = move

        self.depth_explored += 1    
        self.ejecution_time += time.time() - self.time_start
        _, peak_memory = tracemalloc.get_traced_memory()
        self.max_ram_usage += (peak_memory / 1024**2)
        
        tracemalloc.stop()
        print(f"{self.name} elige {best_move} (Puntuación: {best_score:.4f})")
        return best_move