import random
import math
from biosim.core.constants import BARRIER

class Grid:
    def __init__(self, size):
        self.size = size
        # data: 0=Empty, -1=Barrier, >0=AgentID
        self.data = [[0 for _ in range(size)] for _ in range(size)]
        self.safe_zones = [[False for _ in range(size)] for _ in range(size)]
        # Pheromones: Float 0.0 - 1.0
        self.pheromones = [[0.0 for _ in range(size)] for _ in range(size)]

    def is_empty(self, x, y):
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.data[x][y] == 0
        return False
    
    def is_barrier(self, x, y):
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.data[x][y] == BARRIER
        return False
        
    def is_safe_tile(self, x, y):
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.safe_zones[x][y]
        return False
    
    def is_agent(self, x, y):
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.data[x][y] > 0
        return False

    def set(self, x, y, val):
        if 0 <= x < self.size and 0 <= y < self.size:
            self.data[x][y] = val

    def set_safe(self, x, y, is_safe):
        if 0 <= x < self.size and 0 <= y < self.size:
            self.safe_zones[x][y] = is_safe

    def clear(self, x, y):
        if 0 <= x < self.size and 0 <= y < self.size:
            self.data[x][y] = 0
            
    # --- Pheromone Logic ---
    def add_pheromone(self, x, y, amount):
        if 0 <= x < self.size and 0 <= y < self.size:
            # Cap at 1.0
            self.pheromones[x][y] = min(1.0, self.pheromones[x][y] + amount)
            
    def get_pheromone(self, x, y):
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.pheromones[x][y]
        return 0.0
        
    def update_pheromones(self):
        """Decay all pheromones."""
        decay_rate = 0.95
        # Optimized loop? In pure python 128x128 = 16k is borderline.
        # We might need to skip empty cells if possible, but we don't know which are empty.
        # Let's try raw iteration.
        for x in range(self.size):
            for y in range(self.size):
                if self.pheromones[x][y] > 0.01: # Optimization: Ignore negligible values
                    self.pheromones[x][y] *= decay_rate
                else:
                    self.pheromones[x][y] = 0.0

    def find_empty_location(self):
        for _ in range(100): 
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            if self.data[x][y] == 0:
                return x, y
        return None

def is_safe(agent, grid):
    return grid.is_safe_tile(agent.x, agent.y)