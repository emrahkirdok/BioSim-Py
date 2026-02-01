import math
import random
from biosim.core.constants import *
from biosim.core.genome import make_random_gene

class Agent:
    __slots__ = ('x', 'y', 'genome', 'connections', 'neurons', 'last_move', 'color', 'id')
    def __init__(self, x, y, genome=None, genome_length=12, agent_id=0):
        self.x = x
        self.y = y
        self.id = agent_id
        self.last_move = (0, 0) 
        
        if genome is None:
            self.genome = [make_random_gene() for _ in range(genome_length)]
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

    def get_sensor(self, index, grid, time_step):
        if index == S_LOC_X: return self.x / grid.size
        if index == S_LOC_Y: return self.y / grid.size
        if index == S_RANDOM: return random.random()
        if index == S_LAST_MOVE_X: return (self.last_move[0] + 1) / 2
        if index == S_LAST_MOVE_Y: return (self.last_move[1] + 1) / 2
        if index == S_OSC: return (math.sin(time_step * 0.1) + 1) / 2
        
        # Pheromone Sensors
        if index == S_SMELL:
            return grid.get_pheromone(self.x, self.y)
        
        dx, dy = self.last_move
        if dx == 0 and dy == 0: dx, dy = 1, 0
        
        if index == S_SMELL_FWD:
            return grid.get_pheromone(self.x + dx, self.y + dy)
            
        if index == S_SMELL_LR:
            # "Antennae" logic: smell to the left and right of forward direction
            # Rotate dx, dy by 90 degrees
            lx, ly = -dy, dx # Left
            rx, ry = dy, -dx # Right
            left_scent = grid.get_pheromone(self.x + dx + lx, self.y + dy + ly)
            right_scent = grid.get_pheromone(self.x + dx + rx, self.y + dy + ry)
            # Return relative difference: 0.5 is neutral, >0.5 is stronger left
            return 0.5 + (left_scent - right_scent)
        
        # Vision Sensors
        probe_dist = 10
        if index == S_DIST_BARRIER_FWD:
            for d in range(1, probe_dist + 1):
                nx, ny = self.x + dx * d, self.y + dy * d
                if not (0 <= nx < grid.size and 0 <= ny < grid.size): return (probe_dist - d) / probe_dist 
                if grid.is_barrier(nx, ny): return (probe_dist - d) / probe_dist 
            return 0.0
            
        if index == S_DIST_SAFE_FWD:
            for d in range(1, probe_dist + 1):
                nx, ny = self.x + dx * d, self.y + dy * d
                if 0 <= nx < grid.size and 0 <= ny < grid.size:
                    if grid.is_safe_tile(nx, ny): return (probe_dist - d) / probe_dist
            return 0.0

        if index == S_DENS_AGENTS_FWD:
            count = 0
            for d in range(1, probe_dist + 1):
                nx, ny = self.x + dx * d, self.y + dy * d
                if grid.is_agent(nx, ny): count += 1
            return count / probe_dist

        return 0.0

    def think(self, grid, time_step):
        action_levels = [0.0] * NUM_ACTIONS
        next_neurons = [0.0] * MAX_NEURONS
        for src_t, src_id, sink_t, sink_id, w in self.connections:
            val = self.get_sensor(src_id, grid, time_step) if src_t == 1 else self.neurons[src_id]
            output = val * w
            if sink_t == 1: action_levels[sink_id] += output
            else: next_neurons[sink_id] += output
        for i in range(MAX_NEURONS): self.neurons[i] = math.tanh(next_neurons[i])
        move_x, move_y = math.tanh(action_levels[A_MOVE_X]), math.tanh(action_levels[A_MOVE_Y])
        emit_val = math.tanh(action_levels[A_EMIT])
        if emit_val > 0: grid.add_pheromone(self.x, self.y, emit_val * 0.5)
        
        dx, dy = 0, 0
        if random.random() < abs(move_x): dx = 1 if move_x > 0 else -1
        if random.random() < abs(move_y): dy = 1 if move_y > 0 else -1
        return dx, dy, action_levels