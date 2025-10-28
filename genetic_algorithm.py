import random
from copy import deepcopy
from concurrent.futures import ProcessPoolExecutor, as_completed
import argparse  # Para leer argumentos de la terminal
from decimal import Decimal, ROUND_HALF_UP

from players.player import Player

from game.reversiGame import ReversiGame
from game.reversiBoard import ReversiBoard
from players.minimax import MinimaxPlayer
from game.tokens import StackToken

HEURISTICAS = ["corner", "mob", "stable", "parity", "pos"]

def fitness(winner:bool, points:int):
    
    return 1 + 1/points if winner else - 1/points

def calculate_fitness(weights_1: dict, ga_player_max_time: float) -> float:
    player_1 = MinimaxPlayer(
        name=weights_1,
        max_time=ga_player_max_time, 
        custom_weights=weights_1
    )
    
    oponent = MinimaxPlayer(
        max_time=1
    )
    
    game = ReversiGame()
    board = ReversiBoard()
    
    game.players(player1=player_1, player2=oponent)
    player_1.tokens = StackToken("B")
    oponent.tokens = StackToken("R")
    
    
    winner, points = game.play_for_algorithms(deepcopy(board))
    if not winner:
        player_1_score = 1/points
    else:
        player_1_score = fitness(winner= winner == player_1.name, points=points)
    
    print("Ganador:", winner)
    return player_1_score
    
    

class GeneticAlgorithm:
    
    def __init__(self,
                 population_size,
                 generations,
                 elitism_count,
                 mutation_rate,
                 mutation_strength,
                 ga_player_max_time,
                 max_workers=8):
        
        self.population_size = population_size
        self.generations = generations
        self.elitism_count = elitism_count
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength
        self.heuristics = HEURISTICAS
        self.ga_player_max_time = ga_player_max_time
        # self.oponent_weights = oponent_weights
        self.max_workers = max_workers
            
        self.population = []


    def _create_individual(self) -> dict:
        return {
            'apertura': {h: round(random.random(), 4) for h in self.heuristics},
            'medio':    {h: round(random.random(), 4) for h in self.heuristics},
            'final':    {h: round(random.random(), 4) for h in self.heuristics}
        }

    def _create_population(self) -> list[dict]:
        #poblacion aleatoria
        return [self._create_individual() for _ in range(self.population_size)]

    def _tournament_selection(self, population: list[dict]) -> dict:

        tournament_indices = random.sample(range(len(population)), 2)

        best1, best2 = tournament_indices
        return population[best1], population[best2]

    def _crossover(self, parent1: dict, parent2: dict) -> dict:
        #cruce promedio
        child_weights = {
            'apertura': {},
            'medio':    {},
            'final':    {}
        }
        
        for phase in ['apertura', 'medio', 'final']:
            for h in self.heuristics:
                child_weights[phase][h] = float(
                    Decimal((parent1[phase][h] + parent2[phase][h]) / 2)
                    .quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
                )
                
        return child_weights

    def _mutate(self, individual: dict) -> dict:
        #mutacion aleatorio
        mutated_weights = deepcopy(individual) 
        if random.random() > self.mutation_rate:
            return mutated_weights
        
        for phase in ['apertura', 'medio', 'final']:
            for h in self.heuristics:
                if random.random() < 0.25:
                    change = random.uniform(-self.mutation_strength, self.mutation_strength)
                    mutated_weights[phase][h] = max(0.0, mutated_weights[phase][h] + change)
                    return mutated_weights


    def run(self):

        print(f"Población: {self.population_size}, Generaciones: {self.generations}, Tiempo/Mov: {self.ga_player_max_time}s")

        self.population = self._create_population()

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            
            for gen in range(self.generations):
                print(f"--- Generación {gen + 1}/{self.generations} ---")
                
                # Divide the gens in pair
                pares = [(self.population[i], self.population[i+1]) for i in range(0, len(self.population), 2)]
                

                #Fitness
                futures = {
                    executor.submit(calculate_fitness, ind, self.ga_player_max_time): i 
                    for i, ind in enumerate(self.population)
                }
                
                fitnesses = {}
                for future in as_completed(futures):
                    individual_index = futures[future]
                    fit_score = future.result()
                    fitnesses[individual_index] = fit_score

                sorted_indices = sorted(fitnesses, key=fitnesses.get, reverse=True)
                best_fitness = fitnesses[sorted_indices[0]]
                best_individual = self.population[sorted_indices[0]]
                print(f"\n  Mejor Fitness de la Gen: {best_fitness:.2f}")
                print(f"  Mejores Pesos: {best_individual}\n")

                next_generation = []

                for i in range(self.elitism_count):
                    elite_index = sorted_indices[i]
                    next_generation.append(self.population[elite_index])

                #Cruce/mutación
                while len(next_generation) < self.population_size:
                    parent1, parent2 = self._tournament_selection(self.population)
                    
                    child = self._crossover(parent1, parent2)
                    child = self._mutate(child)
                    
                    next_generation.append(child)

                self.population = next_generation
        

        final_fitnesses = {}






        
        with ProcessPoolExecutor(max_workers=self.max_workers) as final_executor:
            # Divide the gens in pair
                pares = [(self.population[i], self.population[i+1]) for i in range(0, len(self.population), 2)]
                
                print(len(self.population))
                #Fitness
                futures = {
                    final_executor.submit(calculate_fitness, ind, self.ga_player_max_time): i 
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
    
    ga = GeneticAlgorithm(
        population_size=16,
        generations=10,
        elitism_count=8,
        mutation_rate=0.2,
        mutation_strength=0.2,
        ga_player_max_time=1,
        max_workers=16
    )
    
    mejores_pesos = ga.run()

    # dummy_board = ReversiBoard()
    
    # pesos_apertura_b = dummy_board._normalize(mejores_pesos['apertura'])
    # pesos_medio_b = dummy_board._normalize(mejores_pesos['medio'])
    # pesos_final_b = dummy_board._normalize(mejores_pesos['final'])
    
    # print(f"Apertura: {pesos_apertura_b}")
    # print(f"Medio:    {pesos_medio_b}")
    # print(f"Final:    {pesos_final_b}")