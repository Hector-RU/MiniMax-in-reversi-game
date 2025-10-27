from players.player import Player
import random

class RandomPlayer(Player):
    
    TYPE_ = "random"
    
    def __init__(self, name="random"):
        super().__init__(name)

    def reset(self):
        pass
             
    def play(self, board):
        
        print("Movimientos posibles:", board.posible_movements(self.tokens.color))
        position = random.choice(board.posible_movements(self.tokens.color))
        return position
    
    
if __name__ == "__main__":
    player = RandomPlayer("Alice")
    print(player.name)  # Output: Alice
    print(player.TYPE_)  # Output: human