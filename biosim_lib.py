import random
import math
import copy

# --- Constants ---
MAX_NEURONS = 10
S_LOC_X, S_LOC_Y, S_RANDOM, S_LAST_MOVE_X, S_LAST_MOVE_Y, S_OSC = range(6)
NUM_SENSORS = 6
A_MOVE_X, A_MOVE_Y, A_MOVE_FWD, A_COLOR_R, A_COLOR_G, A_COLOR_B = range(6)
NUM_ACTIONS = 6

class Gene:
    __slots__ = ('source_type', 'source_num', 'sink_type', 'sink_num', 'weight')
    def __init__(self):
        self.source_type = 0 
        self.source_num = 0
        self.sink_type = 0   
        self.sink_num = 0
        self.weight = 0.0
    
    def copy(self):
        g = Gene()
        g.source_type = self.source_type
        g.source_num = self.source_num
        g.sink_type = self.sink_type
        g.sink_num = self.sink_num
        g.weight = self.weight
        return g

def make_random_gene():
    g = Gene()
    g.source_type = random.choice([0, 1])
    g.source_num = random.randint(0, 127)
    g.sink_type = random.choice([0, 1])
    g.sink_num = random.randint(0, 127)
    g.weight = (random.random() * 8.0) - 4.0
    return g

def mutate_genome(genome, mutation_rate=0.01):
    for gene in genome:
        if random.random() < mutation_rate:
            trait = random.randint(0, 4)
            if trait == 0: gene.source_type ^= 1
            elif trait == 1: gene.source_num ^= random.randint(1, 127)
            elif trait == 2: gene.sink_type ^= 1
            elif trait == 3: gene.sink_num ^= random.randint(1, 127)
            elif trait == 4: gene.weight += (random.random() - 0.5) * 2.0
    if random.random() < 0.05:
        if random.random() < 0.5 and len(genome) > 1:
            del genome[random.randint(0, len(genome)-1)]
        else:
            genome.append(make_random_gene())

def crossover_genomes(g1, g2):
    if len(g1) == 0: return [g.copy() for g in g2]
    if len(g2) == 0: return [g.copy() for g in g1]
    child_genome = []
    pivot = random.randint(0, min(len(g1), len(g2)))
    for i in range(pivot): child_genome.append(g1[i].copy())
    for i in range(pivot, len(g2)): child_genome.append(g2[i].copy())
    return child_genome

class Grid:
    """Manages spatial occupancy to prevent overlaps."""
    def __init__(self, size):
        self.size = size
        # 0 means empty, otherwise contains agent_id
        self.data = [[0 for _ in range(size)] for _ in range(size)]

    def is_empty(self, x, y):
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.data[x][y] == 0
        return False

    def set(self, x, y, val):
        if 0 <= x < self.size and 0 <= y < self.size:
            self.data[x][y] = val

    def clear(self, x, y):
        if 0 <= x < self.size and 0 <= y < self.size:
            self.data[x][y] = 0

    def find_empty_location(self):
        for _ in range(100): # Try 100 times
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            if self.data[x][y] == 0:
                return x, y
        return None # Should handle this in population init

class Agent:
    __slots__ = ('x', 'y', 'genome', 'connections', 'neurons', 'last_move', 'color', 'id')
    def __init__(self, x, y, genome=None, agent_id=0):
        self.x = x
        self.y = y
        self.id = agent_id
        self.last_move = (0, 0)
        
        if genome is None:
            self.genome = [make_random_gene() for _ in range(12)]
        else:
            self.genome = genome
            
        self.compile_brain()
        self.update_color()

    def update_color(self):
        h = abs(hash(str([(g.source_num, g.sink_num) for g in self.genome])))
        self.color = [h % 255, (h // 255) % 255, (h // 65025) % 255]

    def compile_brain(self):
        self.connections = []
        self.neurons = [0.0] * MAX_NEURONS
        for g in self.genome:
            src_t, sink_t = g.source_type, g.sink_type
            src_id = g.source_num % (MAX_NEURONS if src_t == 0 else NUM_SENSORS)
            sink_id = g.sink_num % (MAX_NEURONS if sink_t == 0 else NUM_ACTIONS)
            self.connections.append((src_t, src_id, sink_t, sink_id, g.weight))

    def get_sensor(self, index, grid_size, time_step):
        if index == S_LOC_X: return self.x / grid_size
        if index == S_LOC_Y: return self.y / grid_size
        if index == S_RANDOM: return random.random()
        if index == S_LAST_MOVE_X: return (self.last_move[0] + 1) / 2
        if index == S_LAST_MOVE_Y: return (self.last_move[1] + 1) / 2
        if index == S_OSC: return (math.sin(time_step * 0.1) + 1) / 2
        return 0.0

    def think(self, grid_size, time_step):
        action_levels = [0.0] * NUM_ACTIONS
        next_neurons = [0.0] * MAX_NEURONS
        
        for src_t, src_id, sink_t, sink_id, w in self.connections:
            val = self.get_sensor(src_id, grid_size, time_step) if src_t == 1 else self.neurons[src_id]
            output = val * w
            if sink_t == 1: action_levels[sink_id] += output
            else: next_neurons[sink_id] += output
        
        for i in range(MAX_NEURONS): self.neurons[i] = math.tanh(next_neurons[i])
        
        # Determine intended movement
        move_x = math.tanh(action_levels[A_MOVE_X])
        move_y = math.tanh(action_levels[A_MOVE_Y])
        
        dx = 0
        dy = 0
        if random.random() < abs(move_x): dx = 1 if move_x > 0 else -1
        if random.random() < abs(move_y): dy = 1 if move_y > 0 else -1
        
        return dx, dy, action_levels