import sys
import random
import pygame

from biosim.core.constants import *
from biosim.core.grid import Grid, is_safe
from biosim.core.agent import Agent
from biosim.core.genome import crossover_genomes, mutate_genome
from biosim.ui.widgets import Button, Slider
from biosim.ui.rendering import draw_brain

# Config
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
PANEL_WIDTH = 300
SIM_WIDTH = WINDOW_WIDTH - PANEL_WIDTH
SIM_HEIGHT = WINDOW_HEIGHT
GRID_SIZE = 128
CELL_SIZE = min((SIM_WIDTH - 20) // GRID_SIZE, (SIM_HEIGHT - 20) // GRID_SIZE)
SIM_OFFSET_X = PANEL_WIDTH + (SIM_WIDTH - (GRID_SIZE * CELL_SIZE)) // 2
SIM_OFFSET_Y = (SIM_HEIGHT - (GRID_SIZE * CELL_SIZE)) // 2

# Colors
COLOR_BG = (20, 20, 20)
COLOR_PANEL = (40, 40, 50)
COLOR_TEXT = (220, 220, 220)
COLOR_SAFE_ZONE = (0, 60, 0)
COLOR_BARRIER = (100, 100, 100)
COLOR_HIGHLIGHT = (255, 255, 0)

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("BioSim Python Port")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 14)
        self.small_font = pygame.font.SysFont("monospace", 10)
        
        self.sim_state = "EDIT"
        self.tool_mode = 0
        self.paused = False
        
        # Params
        self.mutation_rate = 0.01
        self.brush_size = 1
        self.pop_size = 1000
        self.genome_len = 12
        self.steps_per_gen = 300
        
        self.grid = Grid(GRID_SIZE)
        self.agents = []
        self.selected_agent = None
        self.generation = 1
        self.step = 0
        
        self.init_ui()

    def init_ui(self):
        self.btn_start = Button(20, 20, 90, 30, "Start", self.toggle_run)
        self.btn_pause = Button(120, 20, 60, 30, "Pause", self.toggle_pause)
        self.btn_clear = Button(190, 20, 60, 30, "Clear", self.clear_grid)
        
        self.btn_tool_sel = Button(20, 70, 60, 30, "Sel", lambda: self.set_tool(0))
        self.btn_tool_bar = Button(90, 70, 60, 30, "Wall", lambda: self.set_tool(1))
        self.btn_tool_saf = Button(160, 70, 60, 30, "Zone", lambda: self.set_tool(2))
        self.btn_tool_era = Button(230, 70, 60, 30, "Erase", lambda: self.set_tool(3))
        
        self.sliders = [
            Slider(20, 130, 210, 12, 0.0, 0.1, self.mutation_rate, "Mutation Rate", self.set_mut_rate),
            Slider(20, 170, 210, 12, 1, 5, self.brush_size, "Brush Size", self.set_brush_size, int_mode=True),
            Slider(20, 210, 210, 12, 100, 5000, self.pop_size, "Pop Size", self.set_pop_size, int_mode=True),
            Slider(20, 250, 210, 12, 4, 32, self.genome_len, "Genome Len", self.set_genome_len, int_mode=True),
            Slider(20, 290, 210, 12, 100, 2000, self.steps_per_gen, "Steps/Gen", self.set_steps, int_mode=True)
        ]
        
        self.buttons = [self.btn_start, self.btn_pause, self.btn_clear, 
                        self.btn_tool_sel, self.btn_tool_bar, self.btn_tool_saf, self.btn_tool_era]

    # --- Callbacks ---
    def toggle_run(self):
        if self.sim_state == "EDIT":
            self.sim_state = "RUN"
            self.populate_world()
            self.generation = 1
            self.step = 0
        else:
            self.sim_state = "EDIT"
            self.agents = []
            
    def toggle_pause(self): self.paused = not self.paused
    def clear_grid(self): 
        self.grid = Grid(GRID_SIZE)
        self.agents = []
        
    def set_tool(self, mode): self.tool_mode = mode
    def set_mut_rate(self, val): self.mutation_rate = val
    def set_brush_size(self, val): self.brush_size = int(val)
    def set_pop_size(self, val): self.pop_size = int(val)
    def set_genome_len(self, val): self.genome_len = int(val)
    def set_steps(self, val): self.steps_per_gen = int(val)

    # --- Logic ---
    def populate_world(self):
        self.agents = []
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if not self.grid.is_barrier(x, y):
                    self.grid.set(x, y, 0)
        for i in range(self.pop_size):
            loc = self.grid.find_empty_location()
            if loc:
                x, y = loc
                self.agents.append(Agent(x, y, genome_length=self.genome_len, agent_id=i+1))
                self.grid.set(x, y, i+1)

    def spawn_next_generation(self):
        survivors = [a for a in self.agents if is_safe(a, self.grid)]
        num_survivors = len(survivors)
        
        # Clear agents from grid
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if not self.grid.is_barrier(x, y):
                    self.grid.set(x, y, 0)
        
        new_agents = []
        if num_survivors == 0:
            for i in range(self.pop_size):
                loc = self.grid.find_empty_location()
                if loc:
                    x, y = loc
                    new_agents.append(Agent(x, y, genome_length=self.genome_len, agent_id=i+1))
                    self.grid.set(x, y, i+1)
        else:
            for i in range(self.pop_size):
                p1 = random.choice(survivors)
                p2 = random.choice(survivors)
                child_genome = crossover_genomes(p1.genome, p2.genome)
                mutate_genome(child_genome, mutation_rate=self.mutation_rate)
                
                loc = self.grid.find_empty_location()
                if loc:
                    x, y = loc
                    new_agents.append(Agent(x, y, genome=child_genome, agent_id=i+1))
                    self.grid.set(x, y, i+1)
        self.agents = new_agents

    def run(self):
        running = True
        mouse_down = False
        
        while running:
            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                
                self.btn_start.text = "Stop" if self.sim_state == "RUN" else "Start"
                self.btn_pause.toggled = self.paused
                self.btn_tool_sel.toggled = (self.tool_mode == 0)
                self.btn_tool_bar.toggled = (self.tool_mode == 1)
                self.btn_tool_saf.toggled = (self.tool_mode == 2)
                self.btn_tool_era.toggled = (self.tool_mode == 3)
                
                for btn in self.buttons: btn.handle_event(event)
                for sld in self.sliders: slider = sld.handle_event(event)
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: mouse_down = True
                elif event.type == pygame.MOUSEBUTTONUP: mouse_down = False

            # Interaction
            if mouse_down:
                mx, my = pygame.mouse.get_pos()
                if mx > PANEL_WIDTH:
                    gx = (mx - SIM_OFFSET_X) // CELL_SIZE
                    gy = (my - SIM_OFFSET_Y) // CELL_SIZE
                    
                    # Brush Logic
                    if self.sim_state == "EDIT" and self.tool_mode != 0:
                        r = self.brush_size - 1
                        for bx in range(gx - r, gx + r + 1):
                            for by in range(gy - r, gy + r + 1):
                                if 0 <= bx < GRID_SIZE and 0 <= by < GRID_SIZE:
                                    if self.tool_mode == 1: self.grid.set(bx, by, BARRIER)
                                    elif self.tool_mode == 2: self.grid.set_safe(bx, by, True)
                                    elif self.tool_mode == 3: 
                                        self.grid.set(bx, by, 0)
                                        self.grid.set_safe(bx, by, False)
                    
                    if self.tool_mode == 0 and 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
                        agent_id = self.grid.data[gx][gy]
                        if agent_id > 0:
                            for a in self.agents:
                                if a.id == agent_id:
                                    self.selected_agent = a
                                    break
                        else:
                            self.selected_agent = None

            # Simulation
            if self.sim_state == "RUN" and not self.paused:
                random.shuffle(self.agents)
                for agent in self.agents:
                    dx, dy, _ = agent.think(self.grid, self.step)
                    if dx != 0 or dy != 0:
                        nx, ny = agent.x + dx, agent.y + dy
                        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                            if self.grid.is_empty(nx, ny):
                                self.grid.clear(agent.x, agent.y)
                                agent.x, agent.y = nx, ny
                                self.grid.set(nx, ny, agent.id)
                                agent.last_move = (dx, dy)
                self.step += 1
                if self.step >= self.steps_per_gen:
                    self.spawn_next_generation()
                    self.step = 0
                    self.generation += 1
                    self.selected_agent = None

            # Render
            self.screen.fill(COLOR_BG)
            
            # Panel
            pygame.draw.rect(self.screen, COLOR_PANEL, (0, 0, PANEL_WIDTH, WINDOW_HEIGHT))
            pygame.draw.line(self.screen, (100, 100, 100), (PANEL_WIDTH, 0), (PANEL_WIDTH, WINDOW_HEIGHT))
            
            for btn in self.buttons: btn.draw(self.screen, self.font)
            for sld in self.sliders: sld.draw(self.screen, self.font)
            
            stats = [
                f"State: {self.sim_state} {'(PAUSED)' if self.paused else ''}",
                f"Gen: {self.generation}",
                f"Step: {self.step}/{self.steps_per_gen}",
                f"Pop: {len(self.agents)}",
                f"FPS: {self.clock.get_fps():.1f}",
                "L-Click to Draw/Sel"
            ]
            for i, line in enumerate(stats):
                self.screen.blit(self.font.render(line, True, COLOR_TEXT), (20, 330 + i*20))

            # Brain Viz
            brain_rect = pygame.Rect(10, WINDOW_HEIGHT - 290, PANEL_WIDTH - 20, 280)
            draw_brain(self.screen, self.selected_agent, brain_rect, self.small_font, pygame.mouse.get_pos())
            if self.selected_agent:
                id_txt = self.font.render(f"Agent ID: {self.selected_agent.id}", True, COLOR_HIGHLIGHT)
                self.screen.blit(id_txt, (20, WINDOW_HEIGHT - 310))

            # Sim View
            sim_rect = pygame.Rect(SIM_OFFSET_X, SIM_OFFSET_Y, GRID_SIZE*CELL_SIZE, GRID_SIZE*CELL_SIZE)
            pygame.draw.rect(self.screen, (0, 0, 0), sim_rect)
            
            for x in range(GRID_SIZE):
                for y in range(GRID_SIZE):
                    if self.grid.is_safe_tile(x, y):
                        rect = (SIM_OFFSET_X + x * CELL_SIZE, SIM_OFFSET_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        pygame.draw.rect(self.screen, COLOR_SAFE_ZONE, rect)
                    if self.grid.is_barrier(x, y):
                        rect = (SIM_OFFSET_X + x * CELL_SIZE, SIM_OFFSET_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        pygame.draw.rect(self.screen, COLOR_BARRIER, rect)

            for agent in self.agents:
                rect = (SIM_OFFSET_X + agent.x * CELL_SIZE, SIM_OFFSET_Y + agent.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, agent.color, rect)
                if agent == self.selected_agent:
                    pygame.draw.rect(self.screen, COLOR_HIGHLIGHT, rect, 2)

            pygame.draw.rect(self.screen, (100, 100, 100), sim_rect, 1)
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
