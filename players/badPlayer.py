import math
from copy import deepcopy
from typing import List, Tuple, Optional
import time
import tracemalloc

from players.player import Player
from game.reversiBoard import ReversiBoard, opponent  # <-- Importamos ReversiBoard Y la función opponent
from game.tokens import Token


class BadPlayer(Player):
    
    TYPE_ = "Bad"
    
    def __init__(self, name="Bad", depth=math.inf, max_time=math.inf, 
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
        Punto de entrada principal. Encuentra el mejor movimiento
        llamando al algoritmo Minimax (con poda alfa-beta).
        """
        tracemalloc.start()
        self.new_depth = 1
        total_depth = None
        depth_counter = 1
        self.turns_played += 1
        possible_moves = board.posible_movements(self.tokens.color)
        self.time_start = time.time()
        
        
        if not possible_moves:
            return None
        
        best_move = possible_moves[0]
        best_score = -math.inf
        alpha = -math.inf
        beta = math.inf
        
        total_nodes_expanded = 0
        total_depth = 0

        self.turn_nodes_expanded = 0
        for depth in range(2, 1000000):
            try:
                self.turn_nodes_expanded = 0
                self.new_depth = 1
                for move in possible_moves:
                    x, y = move
                    
                    child_board = deepcopy(board)
                    self.turn_nodes_expanded += 1
                    child_board.insert_play(x, y, Token(self.tokens.color))
                    
                    #minimax
                    score = self._minimax(child_board, depth - 1, alpha, beta, False, depth_counter)
                    
                    if score < best_score:
                        best_score = score
                        best_move = move
                    
                    alpha = max(alpha, best_score)
                total_nodes_expanded = self.turn_nodes_expanded
                total_depth = self.new_depth
            except StopIteration:
                break
        
        self.nodes_expanded += total_nodes_expanded
        self.depth_explored += total_depth    
        self.ejecution_time += time.time() - self.time_start
        _, peak_memory = tracemalloc.get_traced_memory()
        self.max_ram_usage += (peak_memory / 1024**2)
        
        tracemalloc.stop()
        print(f"{self.name} elige {best_move} (Puntuación: {best_score:.4f})")
        return best_move

    def _minimax(self, board: ReversiBoard, depth: int, alpha: float, beta: float, is_maximizing_player: bool, depth_counter:int=0) -> float:
        """
        Función recursiva de Minimax con poda Alfa-Beta.
        """
        
        if time.time() - self.time_start >= self.max_time:
            raise StopIteration("Out of time!")
        
        if depth == 0 or board.is_terminal():
            return board.evaluate(self.tokens.color, enabled_heuristics=self.enabled_heuristics,
                                custom_weights=self.custom_weights)
            
        if self.new_depth < depth_counter:
            self.new_depth = depth_counter
        
        if is_maximizing_player:
            min_eval = math.inf
            my_color = self.tokens.color
            children_boards = board.childrens(my_color)
            
            if not children_boards:
                #no movimientos
                return self._minimax(board, depth - 1, alpha, beta, False, depth_counter+1)

            for child in children_boards:
                self.turn_nodes_expanded += 1
                eval = self._minimax(child, depth - 1, alpha, beta, False, depth_counter+1)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break 
            return min_eval
            
        else:
            #oponente
            max_eval = -math.inf
            
            
            opponent_color = opponent(self.tokens.color)
            
            children_boards = board.childrens(opponent_color)
            
            
            if not children_boards:
                return self._minimax(board, depth - 1, alpha, beta, True, depth_counter+1)
            
            for child in children_boards:
                self.turn_nodes_expanded += 1
                eval = self._minimax(child, depth - 1, alpha, beta, True, depth_counter+1)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Poda Beta
            
            return max_eval
        
            
        



"""
DEYBBY EL ORDEN IMPORTA, SOLO SI HAY UNA MEJORA CAMBIA ESTE ORDEN
"""