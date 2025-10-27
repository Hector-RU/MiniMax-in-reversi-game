import random
import math
from copy import deepcopy
from concurrent.futures import ProcessPoolExecutor, as_completed
import argparse  # Para leer argumentos de la terminal


from players.player import Player

from game.reversiGame import ReversiGame
from game.reversiBoard import ReversiBoard
from players.minimax import MinimaxPlayer
from players.greedy import GreedyPlayer
from players.randomPlayer import RandomPlayer
from players.badPlayer import BadPlayer  # Importar BadPlayer
from game.tokens import StackToken

HEURISTICAS = ["corner", "mob", "stable", "parity", "pos"]

def calculate_fitness(individual_weights: dict, ga_player_max_time: float, opponent: 'Player') -> float:
    #jugador del GA
    
    player_ga = MinimaxPlayer(
        name="GA_Player",
        max_time=ga_player_max_time, 
        custom_weights=individual_weights
    )
    
    player_opponent = deepcopy(opponent)
    
    game = ReversiGame()
    board = ReversiBoard()
    
    # juego 1
    # GA - azul, oponente - rojo
    game.players(player1=player_ga, player2=player_opponent)
    player_ga.tokens = StackToken("B")
    player_opponent.tokens = StackToken("R")
    
    
    _, final_board_1 = game.play_for_algorithms(deepcopy(board))
    points_1 = final_board_1.points()
    score_1 = points_1[player_ga.token_color] - points_1[player_opponent.token_color]

    #partiida 2
    #oponente azull, ga rojo
    player_ga.reset() 
    player_opponent.reset()
    
    game.players(player1=player_opponent, player2=player_ga)
    player_opponent.tokens = StackToken("B")
    player_ga.tokens = StackToken("R")

    _, final_board_2 = game.play_for_algorithms(deepcopy(board))
    points_2 = final_board_2.points()
    score_2 = points_2[player_ga.token_color] - points_2[player_opponent.token_color]

    return score_1 + score_2

class GeneticAlgorithm:
    
    def __init__(self,
                 population_size,
                 generations,
                 elitism_count,
                 tournament_size,
                 mutation_rate,
                 mutation_strength,
                 ga_player_max_time,
                 opponent,
                 max_workers=8):
        
        self.population_size = population_size
        self.generations = generations
        self.elitism_count = elitism_count
        self.tournament_size = tournament_size
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength
        self.heuristics = HEURISTICAS

        self.ga_player_max_time = ga_player_max_time
        self.opponent = opponent
        self.max_workers = max_workers
            
        self.population = []


    def _create_individual(self) -> dict:
        return {
            'apertura': {h: random.random() for h in self.heuristics},
            'medio':    {h: random.random() for h in self.heuristics},
            'final':    {h: random.random() for h in self.heuristics}
        }

    def _create_population(self) -> list[dict]:
        #poblacion aleatoria
        return [self._create_individual() for _ in range(self.population_size)]

    def _tournament_selection(self, population: list[dict], fitnesses: dict) -> dict:
        tournament_indices = random.sample(range(len(population)), self.tournament_size)
        best_index = max(tournament_indices, key=lambda i: fitnesses[i])
        return population[best_index]

    def _crossover(self, parent1: dict, parent2: dict) -> dict:
        #cruce promedio
        child_weights = {
            'apertura': {},
            'medio':    {},
            'final':    {}
        }
        
        for phase in ['apertura', 'medio', 'final']:
            for h in self.heuristics:
                child_weights[phase][h] = (parent1[phase][h] + parent2[phase][h]) / 2.0
                
        return child_weights

    def _mutate(self, individual: dict) -> dict:
        #mutacion aleatorio




        mutated_weights = deepcopy(individual) 
        
        for phase in ['apertura', 'medio', 'final']:
            for h in self.heuristics:
                if random.random() < self.mutation_rate:
                    change = random.uniform(-self.mutation_strength, self.mutation_strength)
                    mutated_weights[phase][h] = max(0.0, mutated_weights[phase][h] + change)
                    
        return mutated_weights


    def run(self):

        print(f"Población: {self.population_size}, Generaciones: {self.generations}, Tiempo/Mov: {self.ga_player_max_time}s")
        print(f"Oponente: {self.opponent.name}\n")

        self.population = self._create_population()

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            
            for gen in range(self.generations):
                print(f"--- Generación {gen + 1}/{self.generations} ---")
                
                #Fitness
                futures = {
                    executor.submit(calculate_fitness, ind, self.ga_player_max_time, self.opponent): i 
                    for i, ind in enumerate(self.population)
                }
                
                fitnesses = {}
                for future in as_completed(futures):
                    individual_index = futures[future]
                    try:
                        fit_score = future.result()
                        fitnesses[individual_index] = fit_score
                        print(f"  Individuo {individual_index:02d}: Fitness = {fit_score:5.1f}")
                    except Exception as e:
                        print(f"Error calculando fitness para individuo {individual_index}: {e}")
                        fitnesses[individual_index] = -math.inf 
                
                sorted_indices = sorted(fitnesses, key=fitnesses.get, reverse=True)
                best_fitness = fitnesses[sorted_indices[0]]
                best_individual = self.population[sorted_indices[0]]
                print(f"\n  Mejor Fitness de la Gen: {best_fitness:.2f}")
                print(f"  Mejores Pesos: {best_individual}\n")

                next_generation = []

                for i in range(self.elitism_count):
                    elite_index = sorted_indices[i]
                    next_generation.append(self.population[elite_index])

                #ruce/mutación
                while len(next_generation) < self.population_size:
                    parent1 = self._tournament_selection(self.population, fitnesses)
                    parent2 = self._tournament_selection(self.population, fitnesses)
                    
                    child = self._crossover(parent1, parent2)
                    child = self._mutate(child)
                    
                    next_generation.append(child)

                self.population = next_generation
        

        final_fitnesses = {}






        
        with ProcessPoolExecutor(max_workers=self.max_workers) as final_executor:
            futures = {
                final_executor.submit(calculate_fitness, ind, self.ga_player_max_time, self.opponent): i 
                for i, ind in enumerate(self.population)
            }
            for future in as_completed(futures):
                i = futures[future]
                final_fitnesses[i] = future.result()

        sorted_indices = sorted(final_fitnesses, key=final_fitnesses.get, reverse=True)
        best_individual = self.population[sorted_indices[0]]
        best_fitness = final_fitnesses[sorted_indices[0]]

        print(f"Mejor Fitness Total: {best_fitness:.2f}")
        print(f"Mejores Pesos: {best_individual}")
        
        return best_individual



#hectro está por terminal
if __name__ == "__main__":

    opponent_map = {
        "greedy": GreedyPlayer(name="BaselineGreedy"),
        "random": RandomPlayer(name="BaselineRandom"),
        "minimax": MinimaxPlayer(name="BaselineMinimax", max_time=0.05),
        "bad": BadPlayer(name="BaselineBad", max_time=0.05)
    }

    parser = argparse.ArgumentParser(description="pone al algoritmo Genético a buscar los pesos")
    parser.add_argument(
        "-o", "--opponent",  
        type=str,
        choices=opponent_map.keys(), 
        default="minimax",           
        help="Elige el oponente"
    )
    args = parser.parse_args()

    OPPONENTE = opponent_map[args.opponent]

    ga = GeneticAlgorithm(
        population_size=20,
        generations=30,
        elitism_count=2,
        tournament_size=3,
        mutation_rate=0.1,
        mutation_strength=0.2,
        ga_player_max_time=1.0,
        opponent=OPPONENTE,
        max_workers=8
    )
    
    mejores_pesos = ga.run()







    dummy_board = ReversiBoard()
    
    pesos_apertura_b = dummy_board._normalize(mejores_pesos['apertura'])
    pesos_medio_b = dummy_board._normalize(mejores_pesos['medio'])
    pesos_final_b = dummy_board._normalize(mejores_pesos['final'])
    
    print(f"Apertura: {pesos_apertura_b}")
    print(f"Medio:    {pesos_medio_b}")
    print(f"Final:    {pesos_final_b}")