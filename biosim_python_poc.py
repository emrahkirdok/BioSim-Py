import random
import time
import math
import copy

# --- Config ---
WORLD_SIZE = 64
POPULATION = 20
STEPS = 100

# --- Constants ---
# Sensor Indices
S_LOC_X = 0
S_LOC_Y = 1
S_RANDOM = 2
S_LAST_MOVE_X = 3
S_LAST_MOVE_Y = 4
NUM_SENSORS = 5

# Action Indices
A_MOVE_X = 0
A_MOVE_Y = 1
A_MOVE_FWD = 2
NUM_ACTIONS = 3

MAX_NEURONS = 10 # Internal neurons

# --- Genome Logic (The "Brain" Builder) ---
class Gene:
    def __init__(self):
        self.source_type = 0 # 0:Neuron, 1:Sensor
        self.source_num = 0
        self.sink_type = 0   # 0:Neuron, 1:Action
        self.sink_num = 0
        self.weight = 0.0

def make_random_gene():
    g = Gene()
    g.source_type = random.choice([0, 1])
    g.source_num = random.randint(0, 127)
    g.sink_type = random.choice([0, 1])
    g.sink_num = random.randint(0, 127)
    g.weight = (random.random() * 8.0) - 4.0
    return g

class NeuralNet:
    def __init__(self):
        self.connections = [] # List of (src_type, src_id, sink_type, sink_id, weight)
        self.neurons = []     # List of current values for internal neurons

def compile_genome(genome):
    """Simplified compilation logic from previous step."""
    net = NeuralNet()
    # Simplified: Direct mapping without advanced culling for this demo
    mapping = {} 
    
    # Map internal neurons to 0..MAX_NEURONS
    # Map sensors/actions to their counts
    for gene in genome:
        src_t, sink_t = gene.source_type, gene.sink_type
        src_id = gene.source_num % (MAX_NEURONS if src_t == 0 else NUM_SENSORS)
        sink_id = gene.sink_num % (MAX_NEURONS if sink_t == 0 else NUM_ACTIONS)
        
        net.connections.append({
            'src_t': src_t, 'src_id': src_id,
            'sink_t': sink_t, 'sink_id': sink_id,
            'w': gene.weight
        })
    
    # Initialize internal neuron states
    net.neurons = [0.0] * MAX_NEURONS
    return net

# --- The Agent ---
class Agent:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.last_move_x = 0
        self.last_move_y = 0
        self.genome = [make_random_gene() for _ in range(12)] # 12 random genes
        self.brain = compile_genome(self.genome)
        self.id = random.randint(1000, 9999)

    def get_sensor_value(self, sensor_idx):
        """Reading the World (Input)"""
        if sensor_idx == S_LOC_X:
            return self.x / WORLD_SIZE
        elif sensor_idx == S_LOC_Y:
            return self.y / WORLD_SIZE
        elif sensor_idx == S_RANDOM:
            return random.random()
        elif sensor_idx == S_LAST_MOVE_X:
            return (self.last_move_x + 1) / 2 # Normalize -1..1 to 0..1
        elif sensor_idx == S_LAST_MOVE_Y:
            return (self.last_move_y + 1) / 2
        return 0.0

    def think(self):
        """Feed Forward Neural Net"""
        # 1. Reset Actions Accumulators
        action_levels = [0.0] * NUM_ACTIONS
        
        # 2. Reset Internal Neurons (Simulate basic decay or reset)
        # In full biosim, they might retain state. Here we reset for simplicity.
        next_neuron_states = [0.0] * MAX_NEURONS

        # 3. Process Connections
        # In a real graph, order matters. Here we do a simple pass.
        for conn in self.brain.connections:
            # Get Input Value
            input_val = 0.0
            if conn['src_t'] == 1: # SENSOR
                input_val = self.get_sensor_value(conn['src_id'])
            else: # NEURON
                input_val = self.brain.neurons[conn['src_id']]
            
            # Apply Weight
            weighted_val = input_val * conn['w']

            # Add to Output
            if conn['sink_t'] == 1: # ACTION
                action_levels[conn['sink_id']] += weighted_val
            else: # NEURON
                next_neuron_states[conn['sink_id']] += weighted_val
        
        # 4. Activation Function (Tanh) and Update State
        self.brain.neurons = [math.tanh(v) for v in next_neuron_states]
        final_actions = [math.tanh(v) for v in action_levels]
        
        return final_actions

    def act(self, action_levels):
        """Executing Actions (Output)"""
        # Interpretation of outputs
        move_x = action_levels[A_MOVE_X] # Range -1 to 1
        move_y = action_levels[A_MOVE_Y]
        
        # Probabilistic movement (biosim4 style)
        dx = 0
        dy = 0
        
        if random.random() < abs(move_x):
            dx = 1 if move_x > 0 else -1
        
        if random.random() < abs(move_y):
            dy = 1 if move_y > 0 else -1

        # Apply movement
        new_x = (self.x + dx) % WORLD_SIZE # Wrap around world
        new_y = (self.y + dy) % WORLD_SIZE
        
        self.last_move_x = dx
        self.last_move_y = dy
        self.x = new_x
        self.y = new_y

# --- Main Simulation Loop ---
def run_simulation():
    # 1. Initialize Population
    agents = [Agent(random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE)) for _ in range(POPULATION)]
    
    print(f"Simulation Started: {POPULATION} agents, {WORLD_SIZE}x{WORLD_SIZE} grid.")

    for step in range(STEPS):
        # In a real sim, we would map agents to a grid here to handle collisions
        
        # Update every agent
        for agent in agents:
            # SENSE -> THINK
            actions = agent.think()
            
            # ACT
            agent.act(actions)

        # Visualization (Text based)
        if step % 10 == 0:
            print(f"Step {step}: Agent {agents[0].id} is at ({agents[0].x}, {agents[0].y}) Actions: [X:{actions[0]:.2f}, Y:{actions[1]:.2f}]")

if __name__ == "__main__":
    run_simulation()
