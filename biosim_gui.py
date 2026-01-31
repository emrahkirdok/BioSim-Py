import random
import math
import sys
import pygame

import biosim_lib as bs

# --- Configuration ---
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Layout
PANEL_WIDTH = 300  # 25% of 1200 is 300
SIM_WIDTH = WINDOW_WIDTH - PANEL_WIDTH
SIM_HEIGHT = WINDOW_HEIGHT

# Simulation View
GRID_SIZE = 128
# Calculate cell size to fit in the sim area (with some padding)
CELL_SIZE = min((SIM_WIDTH - 20) // GRID_SIZE, (SIM_HEIGHT - 20) // GRID_SIZE)
SIM_OFFSET_X = PANEL_WIDTH + (SIM_WIDTH - (GRID_SIZE * CELL_SIZE)) // 2
SIM_OFFSET_Y = (SIM_HEIGHT - (GRID_SIZE * CELL_SIZE)) // 2

POPULATION_SIZE = 1000
STEPS_PER_GEN = 300

# Colors
COLOR_BG = (20, 20, 20)
COLOR_PANEL = (40, 40, 50)
COLOR_TEXT = (220, 220, 220)
COLOR_SAFE_ZONE = (0, 40, 0)
COLOR_HIGHLIGHT = (255, 255, 0) # Selected agent border
COLOR_UI_BG = (60, 60, 70)
COLOR_UI_ACTIVE = (100, 100, 150)

# Global State
CHALLENGE_TYPE = 0 
MUTATION_RATE = 0.01
PAUSED = False
SELECTED_AGENT = None
AGENTS = []
GRID = None
GENERATION = 1
STEP = 0

# --- Helper Logic ---
def is_safe(agent):
    if CHALLENGE_TYPE == 0:
        return agent.x > GRID_SIZE // 2
    elif CHALLENGE_TYPE == 1:
        cx, cy = GRID_SIZE // 2, GRID_SIZE // 2
        radius = GRID_SIZE // 4
        dist = math.sqrt((agent.x - cx)**2 + (agent.y - cy)**2)
        return dist < radius
    return False

def spawn_next_generation(agents, grid):
    survivors = [a for a in agents if is_safe(a)]
    num_survivors = len(survivors)
    
    grid.data = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    new_agents = []
    
    if num_survivors == 0:
        # Extinction
        for i in range(POPULATION_SIZE):
            loc = grid.find_empty_location()
            if loc:
                x, y = loc
                new_agents.append(bs.Agent(x, y, agent_id=i+1))
                grid.set(x, y, i+1)
    else:
        # Reproduction
        for i in range(POPULATION_SIZE):
            p1 = random.choice(survivors)
            p2 = random.choice(survivors)
            child_genome = bs.crossover_genomes(p1.genome, p2.genome)
            bs.mutate_genome(child_genome, mutation_rate=MUTATION_RATE)
            
            loc = grid.find_empty_location()
            if loc:
                x, y = loc
                new_agents.append(bs.Agent(x, y, genome=child_genome, agent_id=i+1))
                grid.set(x, y, i+1)
            
    return new_agents

# --- UI Components ---
class Button:
    def __init__(self, x, y, w, h, text, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.hovered = False

    def draw(self, screen, font):
        color = COLOR_UI_ACTIVE if self.hovered else COLOR_UI_BG
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 1) # Border
        
        text_surf = font.render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and event.button == 1:
                self.callback()

class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial
        self.label = label
        self.dragging = False

    def draw(self, screen, font):
        # Draw Label
        val_str = f"{self.label}: {self.value:.3f}"
        text_surf = font.render(val_str, True, COLOR_TEXT)
        screen.blit(text_surf, (self.rect.x, self.rect.y - 20))
        
        # Draw Track
        pygame.draw.rect(screen, (100, 100, 100), self.rect)
        
        # Draw Knob
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        knob_x = self.rect.x + (ratio * self.rect.width)
        knob_rect = pygame.Rect(knob_x - 5, self.rect.y - 5, 10, self.rect.height + 10)
        pygame.draw.rect(screen, COLOR_UI_ACTIVE, knob_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.update_value(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.update_value(event.pos[0])

    def update_value(self, mouse_x):
        rel_x = mouse_x - self.rect.x
        ratio = max(0.0, min(1.0, rel_x / self.rect.width))
        self.value = self.min_val + (ratio * (self.max_val - self.min_val))
        
        # Specific global update based on label (Hack for demo)
        if "Mutation" in self.label:
            global MUTATION_RATE
            MUTATION_RATE = self.value

# --- Visualization ---

def draw_brain(screen, agent, rect, font):
    pygame.draw.rect(screen, (30, 30, 40), rect)
    pygame.draw.rect(screen, (100, 100, 100), rect, 1)
    
    if agent is None:
        text = font.render("Select an Agent", True, (100, 100, 100))
        screen.blit(text, text.get_rect(center=rect.center))
        return

    # Layout Nodes
    # Inputs (Left), Hidden (Center), Outputs (Right)
    # Using fixed positions for Inputs/Outputs to make it readable
    
    node_radius = 5
    input_x = rect.left + 30
    output_x = rect.right - 30
    hidden_x = rect.centerx
    
    y_spacing = rect.height / (max(bs.NUM_SENSORS, bs.NUM_ACTIONS) + 1)
    
    # Store node positions: (type, index) -> (x, y)
    node_positions = {}
    
    # Draw Inputs
    for i in range(bs.NUM_SENSORS):
        y = rect.top + (i + 1) * y_spacing
        node_positions[(1, i)] = (input_x, y)
        pygame.draw.circle(screen, (0, 200, 0), (input_x, y), node_radius)
        # Label
        lbl = font.render(str(i), True, (150, 255, 150))
        screen.blit(lbl, (input_x - 15, y - 5))

    # Draw Outputs
    for i in range(bs.NUM_ACTIONS):
        y = rect.top + (i + 1) * y_spacing
        node_positions[(1, i)] = (output_x, y) # Reusing type 1 (Sensor) logic for dict key? No, need distinguish.
        # Actually standard Gene uses: src_type (0=N, 1=S), sink_type (0=N, 1=A)
        # So: Sensor=(1, id), Action=(1, id) [Wait, this overlaps]
        # Let's map: Sensor=('S', id), Action=('A', id), Neuron=('N', id)
        node_positions[('A', i)] = (output_x, y)
        
        val = math.tanh(0) # We don't have easy access to latest action values here without re-simulating or storing them
        color = (200, 0, 0) # Red
        pygame.draw.circle(screen, color, (output_x, y), node_radius)
        lbl = font.render(str(i), True, (255, 150, 150))
        screen.blit(lbl, (output_x + 8, y - 5))

    # Draw Hidden Neurons (Random layout or circle)
    # We place them in a circle in the middle
    center_y = rect.centery
    radius = min(rect.width, rect.height) / 4
    for i in range(bs.MAX_NEURONS):
        angle = (2 * math.pi * i) / bs.MAX_NEURONS
        nx = hidden_x + math.cos(angle) * radius
        ny = center_y + math.sin(angle) * radius
        node_positions[('N', i)] = (nx, ny)
        
        # Color based on activation
        act = agent.neurons[i]
        c_val = int((act + 1) * 127) # -1..1 -> 0..255
        color = (c_val, c_val, c_val)
        pygame.draw.circle(screen, color, (nx, ny), node_radius)
        pygame.draw.circle(screen, (100, 100, 100), (nx, ny), node_radius, 1)

    # Draw Connections
    for g in agent.genome:
        # Determine start/end pos
        start_key = ('S' if g.source_type == 1 else 'N', g.source_num % (bs.NUM_SENSORS if g.source_type==1 else bs.MAX_NEURONS))
        end_key = ('A' if g.sink_type == 1 else 'N', g.sink_num % (bs.NUM_ACTIONS if g.sink_type==1 else bs.MAX_NEURONS))
        
        if start_key in node_positions and end_key in node_positions:
            start_pos = node_positions[start_key]
            end_pos = node_positions[end_key]
            
            # Color: Blue=Positive, Red=Negative
            color = (0, 100, 255) if g.weight > 0 else (255, 50, 50)
            width = max(1, int(abs(g.weight)))
            
            pygame.draw.line(screen, color, start_pos, end_pos, width)


def main():
    global PAUSED, CHALLENGE_TYPE, SELECTED_AGENT, GENERATION, STEP, AGENTS, GRID

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("BioSim Python Port")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 14)
    small_font = pygame.font.SysFont("monospace", 10)

    # Setup UI
    def toggle_pause():
        global PAUSED
        PAUSED = not PAUSED
    
    def reset_sim():
        global GENERATION, STEP, AGENTS, GRID, SELECTED_AGENT
        GRID = bs.Grid(GRID_SIZE)
        AGENTS = []
        for i in range(POPULATION_SIZE):
            loc = GRID.find_empty_location()
            if loc:
                x, y = loc
                AGENTS.append(bs.Agent(x, y, agent_id=i+1))
                GRID.set(x, y, i+1)
        GENERATION = 1
        STEP = 0
        SELECTED_AGENT = None

    def toggle_mode():
        global CHALLENGE_TYPE
        CHALLENGE_TYPE = (CHALLENGE_TYPE + 1) % 2

    btn_pause = Button(20, 20, 100, 30, "Pause/Run", toggle_pause)
    btn_reset = Button(130, 20, 100, 30, "Reset", reset_sim)
    btn_mode = Button(20, 60, 210, 30, "Switch Challenge", toggle_mode)
    
    slider_mut = Slider(20, 130, 210, 20, 0.0, 0.1, MUTATION_RATE, "Mutation Rate")
    
    ui_elements = [btn_pause, btn_reset, btn_mode, slider_mut]

    # Initial Sim Setup
    reset_sim()

    running = True
    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # UI Events
            for el in ui_elements:
                el.handle_event(event)
            
            # Selecting Agent
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # Check if click is in Sim Area
                if mx > PANEL_WIDTH:
                    # Convert screen to grid coords
                    gx = (mx - SIM_OFFSET_X) // CELL_SIZE
                    gy = (my - SIM_OFFSET_Y) // CELL_SIZE
                    
                    if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
                        # Find agent at this loc
                        # Grid lookup is fast
                        agent_id = GRID.data[gx][gy]
                        if agent_id != 0:
                            # Linear search to find object (could optimize with dict)
                            for a in AGENTS:
                                if a.id == agent_id:
                                    SELECTED_AGENT = a
                                    break
                        else:
                            SELECTED_AGENT = None

        # Update
        if not PAUSED:
            random.shuffle(AGENTS)
            for agent in AGENTS:
                dx, dy, _ = agent.think(GRID_SIZE, STEP)
                if dx != 0 or dy != 0:
                    nx, ny = agent.x + dx, agent.y + dy
                    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                        if GRID.is_empty(nx, ny):
                            GRID.clear(agent.x, agent.y)
                            agent.x, agent.y = nx, ny
                            GRID.set(nx, ny, agent.id)
                            agent.last_move = (dx, dy)
            
            STEP += 1
            if STEP >= STEPS_PER_GEN:
                AGENTS = spawn_next_generation(AGENTS, GRID)
                STEP = 0
                GENERATION += 1
                SELECTED_AGENT = None # Deselect on new gen (agent might die)

        # Render
        screen.fill(COLOR_BG)
        
        # --- Draw Panel (Left) ---
        pygame.draw.rect(screen, COLOR_PANEL, (0, 0, PANEL_WIDTH, WINDOW_HEIGHT))
        pygame.draw.line(screen, (100, 100, 100), (PANEL_WIDTH, 0), (PANEL_WIDTH, WINDOW_HEIGHT))
        
        # Draw UI Elements
        for el in ui_elements:
            el.draw(screen, font)
        
        # Stats
        stats = [
            f"Gen: {GENERATION}",
            f"Step: {STEP}/{STEPS_PER_GEN}",
            f"Pop: {len(AGENTS)}",
            f"FPS: {clock.get_fps():.1f}",
            f"Mode: {'Right' if CHALLENGE_TYPE==0 else 'Circle'}"
        ]
        for i, line in enumerate(stats):
            screen.blit(font.render(line, True, COLOR_TEXT), (20, 180 + i*20))

        # Brain Viz
        brain_rect = pygame.Rect(10, WINDOW_HEIGHT - 290, PANEL_WIDTH - 20, 280)
        draw_brain(screen, SELECTED_AGENT, brain_rect, small_font)
        if SELECTED_AGENT:
            id_txt = font.render(f"Agent ID: {SELECTED_AGENT.id}", True, COLOR_HIGHLIGHT)
            screen.blit(id_txt, (20, WINDOW_HEIGHT - 310))

        # --- Draw Sim (Right) ---
        sim_rect = pygame.Rect(SIM_OFFSET_X, SIM_OFFSET_Y, GRID_SIZE*CELL_SIZE, GRID_SIZE*CELL_SIZE)
        pygame.draw.rect(screen, (0, 0, 0), sim_rect) # Black background for world
        
        # Safe Zone
        if CHALLENGE_TYPE == 0:
            safe_rect = pygame.Rect(SIM_OFFSET_X + (GRID_SIZE//2)*CELL_SIZE, SIM_OFFSET_Y, (GRID_SIZE//2)*CELL_SIZE, GRID_SIZE*CELL_SIZE)
            pygame.draw.rect(screen, COLOR_SAFE_ZONE, safe_rect)
        else:
             center = (SIM_OFFSET_X + (GRID_SIZE//2)*CELL_SIZE, SIM_OFFSET_Y + (GRID_SIZE//2)*CELL_SIZE)
             radius = (GRID_SIZE//4)*CELL_SIZE
             pygame.draw.circle(screen, COLOR_SAFE_ZONE, center, radius)

        # Agents
        for agent in AGENTS:
            rect = (SIM_OFFSET_X + agent.x * CELL_SIZE, SIM_OFFSET_Y + agent.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, agent.color, rect)
            
            # Highlight selected
            if agent == SELECTED_AGENT:
                pygame.draw.rect(screen, COLOR_HIGHLIGHT, rect, 2)

        # Border around Sim
        pygame.draw.rect(screen, (100, 100, 100), sim_rect, 1)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()