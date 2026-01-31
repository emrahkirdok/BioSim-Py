import random
import math
import time
import sys

# Try to import pygame, or exit with a helpful message
try:
    import pygame
except ImportError:
    print("Error: Pygame is not installed.")
    print("Please install it to run the visualization:")
    print("  pip install pygame")
    sys.exit(1)

# --- Configuration ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
GRID_SIZE = 128  # The simulation world dimensions
CELL_SIZE = WINDOW_WIDTH // GRID_SIZE  # Pixels per grid cell

POPULATION_SIZE = 500
STEPS_PER_GEN = 300

# Colors
COLOR_BG = (10, 10, 10)
COLOR_TEXT = (200, 200, 200)

# --- Simulation Constants ---
MAX_NEURONS = 10
S_LOC_X, S_LOC_Y, S_RANDOM, S_LAST_MOVE_X, S_LAST_MOVE_Y, S_OSC = range(6)
NUM_SENSORS = 6
A_MOVE_X, A_MOVE_Y, A_MOVE_FWD, A_COLOR_R, A_COLOR_G, A_COLOR_B = range(6)
NUM_ACTIONS = 6

# --- Logic: Genome & Brain ---

class Gene:
    __slots__ = ('source_type', 'source_num', 'sink_type', 'sink_num', 'weight')
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

class Agent:
    __slots__ = ('x', 'y', 'genome', 'connections', 'neurons', 'last_move', 'color')
    def __init__(self, x, y, genome=None):
        self.x = x
        self.y = y
        self.last_move = (0, 0)
        
        if genome is None:
            self.genome = [make_random_gene() for _ in range(16)]
        else:
            self.genome = genome
            
        self.compile_brain()
        
        # Default color (will be overridden by brain output if wired)
        # Generate a static base color from genome hash
        h = abs(hash(str([(g.source_num, g.sink_num) for g in self.genome])))
        self.color = (h % 255, (h // 255) % 255, (h // 65025) % 255)

    def compile_brain(self):
        """Simplistic compilation: just store active connections."""
        self.connections = []
        self.neurons = [0.0] * MAX_NEURONS
        
        for g in self.genome:
            src_t = g.source_type
            sink_t = g.sink_type
            
            src_id = g.source_num % (MAX_NEURONS if src_t == 0 else NUM_SENSORS)
            sink_id = g.sink_num % (MAX_NEURONS if sink_t == 0 else NUM_ACTIONS)
            
            self.connections.append((src_t, src_id, sink_t, sink_id, g.weight))

    def get_sensor(self, index):
        if index == S_LOC_X: return self.x / GRID_SIZE
        if index == S_LOC_Y: return self.y / GRID_SIZE
        if index == S_RANDOM: return random.random()
        if index == S_LAST_MOVE_X: return (self.last_move[0] + 1) / 2
        if index == S_LAST_MOVE_Y: return (self.last_move[1] + 1) / 2
        if index == S_OSC: return (math.sin(time.time() * 5) + 1) / 2
        return 0.0

    def think_and_act(self):
        # Reset Accumulators
        action_levels = [0.0] * NUM_ACTIONS
        next_neurons = [0.0] * MAX_NEURONS
        
        # Process connections
        for src_t, src_id, sink_t, sink_id, w in self.connections:
            val = 0.0
            if src_t == 1: # Sensor
                val = self.get_sensor(src_id)
            else: # Neuron
                val = self.neurons[src_id]
            
            output = val * w
            
            if sink_t == 1: # Action
                action_levels[sink_id] += output
            else: # Neuron
                next_neurons[sink_id] += output
        
        # Update neurons (tanh activation)
        for i in range(MAX_NEURONS):
            self.neurons[i] = math.tanh(next_neurons[i])
            
        # Execute Actions
        # Movement: Probabilistic
        move_x = math.tanh(action_levels[A_MOVE_X])
        move_y = math.tanh(action_levels[A_MOVE_Y])
        
        dx = 0
        dy = 0
        if random.random() < abs(move_x): dx = 1 if move_x > 0 else -1
        if random.random() < abs(move_y): dy = 1 if move_y > 0 else -1
        
        self.x = (self.x + dx) % GRID_SIZE
        self.y = (self.y + dy) % GRID_SIZE
        self.last_move = (dx, dy)
        
        # Dynamic Color Change (optional fun feature)
        # If the brain outputs to the color channels, mix it with base color
        r_mod = (math.tanh(action_levels[A_COLOR_R]) + 1) * 127
        g_mod = (math.tanh(action_levels[A_COLOR_G]) + 1) * 127
        b_mod = (math.tanh(action_levels[A_COLOR_B]) + 1) * 127
        
        # Simple blending
        self.color = (
            min(255, int((self.color[0] + r_mod)/2)),
            min(255, int((self.color[1] + g_mod)/2)),
            min(255, int((self.color[2] + b_mod)/2))
        )

# --- Main Application ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("BioSim Python Port")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 16)

    # Initialize Population
    agents = [Agent(random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)) 
              for _ in range(POPULATION_SIZE)]

    generation = 0
    step = 0
    running = True
    paused = False

    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    # Reset
                    agents = [Agent(random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)) 
                              for _ in range(POPULATION_SIZE)]
                    generation = 0
                    step = 0

        if not paused:
            # 2. Update Simulation
            # Performance Note: Doing this for 500-1000 agents in pure Python is okay.
            # For 5000+, we would need the NumPy approach.
            for agent in agents:
                agent.think_and_act()
            
            step += 1
            if step >= STEPS_PER_GEN:
                step = 0
                generation += 1
                # (Evolution logic would go here - selection, reproduction)

        # 3. Render
        screen.fill(COLOR_BG)

        # Draw Agents
        # We draw directly to pixels for speed if particles are small
        # But rects are easier to see
        for agent in agents:
            rect = (agent.x * CELL_SIZE, agent.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, agent.color, rect)

        # Draw UI Overlay
        info_text = [
            f"Gen: {generation}",
            f"Step: {step}/{STEPS_PER_GEN}",
            f"Pop: {len(agents)}",
            f"FPS: {clock.get_fps():.1f}",
            "[SPACE] Pause  [R] Reset"
        ]
        
        for i, line in enumerate(info_text):
            text_surf = font.render(line, True, COLOR_TEXT)
            screen.blit(text_surf, (10, 10 + i * 20))

        pygame.display.flip()
        clock.tick(60) # Limit to 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()
