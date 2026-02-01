import random
import math
import numpy as np
from biosim.core.constants import BARRIER

class Grid:
    def __init__(self, size):
        self.size = size
        # data: 0=Empty, -1=Barrier, >0=AgentID
        self.data = [[0 for _ in range(size)] for _ in range(size)]
        self.safe_zones = [[False for _ in range(size)] for _ in range(size)]
        
        # Pheromones: NumPy float array for performance
        self.pheromones = np.zeros((size, size), dtype=np.float32)

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
            
    # --- Pheromone Logic (Vectorized) ---
    def add_pheromone(self, x, y, amount):
        if 0 <= x < self.size and 0 <= y < self.size:
            self.pheromones[x][y] = min(1.0, self.pheromones[x][y] + amount)
            
    def get_pheromone(self, x, y):
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.pheromones[x][y]
        return 0.0
        
    def update_pheromones(self):
        """Vectorized Decay and Diffusion using NumPy."""
        decay_factor = 0.98
        self.pheromones *= decay_factor
        
        diff = 0.1 
        neighbor_sum = np.zeros_like(self.pheromones)
        neighbor_sum[1:-1, 1:-1] = (
            self.pheromones[:-2, 1:-1] +  # Top
            self.pheromones[2:, 1:-1] +   # Bottom
            self.pheromones[1:-1, :-2] +  # Left
            self.pheromones[1:-1, 2:] +   # Right
            self.pheromones[:-2, :-2] +   # Top-Left
            self.pheromones[:-2, 2:] +    # Top-Right
            self.pheromones[2:, :-2] +    # Bottom-Left
            self.pheromones[2:, 2:]       # Bottom-Right
        ) / 8.0
        
        self.pheromones = (1.0 - diff) * self.pheromones + diff * neighbor_sum
        self.pheromones = np.clip(self.pheromones, 0, 1.0)

    def find_empty_location(self, avoid_safe=False, margin=0):
        """
        Finds a random unoccupied location.
        avoid_safe: If True, tries to find a tile that is not safe.
        margin: Distance from any safe tile if avoid_safe is True.
        """
        for _ in range(1000): # More attempts for restricted spawning
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            
            if self.data[x][y] == 0:
                if not avoid_safe:
                    return x, y
                
                # Logic to avoid safe zones with margin
                is_near_safe = False
                if margin == 0:
                    is_near_safe = self.is_safe_tile(x, y)
                else:
                    # Check neighborhood
                    for dx in range(-margin, margin + 1):
                        for dy in range(-margin, margin + 1):
                            if self.is_safe_tile(x + dx, y + dy):
                                is_near_safe = True
                                break
                        if is_near_safe: break
                
                if not is_near_safe:
                    return x, y
                    
        # Fallback if too crowded/hard
        return None

def is_safe(agent, grid):
    return grid.is_safe_tile(agent.x, agent.y)