import sys
import random
import pygame
import os
import numpy as np
import math

from biosim.core.constants import *
from biosim.core.grid import Grid, is_safe
from biosim.core.agent import Agent
import biosim.core.genome as gen
from biosim.core.persistence import save_simulation, load_simulation
from biosim.core.analytics import Analytics
from biosim.core.genomics import cluster_population
from biosim.ui.widgets import Button, Slider
from biosim.ui.rendering import draw_brain

# Config
PANEL_WIDTH = 300
SIM_WIDTH = 900
SIM_HEIGHT = 850
WINDOW_WIDTH = PANEL_WIDTH + SIM_WIDTH
WINDOW_HEIGHT = SIM_HEIGHT

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
        pygame.display.set_caption("BioSim-Py")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 14)
        self.small_font = pygame.font.SysFont("monospace", 10)
        
        self.sim_state = "EDIT"
        self.input_mode = None 
        self.input_text = ""
        self.tool_mode = 0
        self.paused = False
        self.hide_dead_nodes = False
        self.spawn_away = False
        
        # Params
        self.mutation_rate = 0.01
        self.insertion_rate = 0.01
        self.deletion_rate = 0.01
        self.unequal_rate = 0.0 
        self.brush_size = 1
        self.pop_size = 1000
        self.genome_len = 12
        self.steps_per_gen = 300
        
        self.enabled_traits = {"Vision": True, "Smell": True, "Osc": True, "Mem": True, "Emit": True, "Kill": False}
        self.sync_genetic_config()
        
        self.grid = Grid(GRID_SIZE)
        self.agents = []
        self.selected_agent = None
        self.generation = 1
        self.step = 0
        self.species_count = 0
        
        self.analytics = Analytics()
        self.current_gen_kills = 0
        
        self.init_ui()

    def sync_genetic_config(self):
        sensors = [S_LOC_X, S_LOC_Y, S_RANDOM]
        if self.enabled_traits["Vision"]: sensors += SENSOR_GROUPS["Vision"]
        if self.enabled_traits["Smell"]: sensors += SENSOR_GROUPS["Smell"]
        if self.enabled_traits["Osc"]: sensors += SENSOR_GROUPS["Osc"]
        if self.enabled_traits["Mem"]: sensors += SENSOR_GROUPS["Mem"]
        if self.enabled_traits["Kill"]: sensors += SENSOR_GROUPS["Danger"]
        gen.ENABLED_SENSORS = sorted(list(set(sensors)))
        actions = [A_MOVE_X, A_MOVE_Y, A_MOVE_FWD]
        if self.enabled_traits["Emit"]: actions += ACTION_GROUPS["Emit"]
        if self.enabled_traits["Kill"]: actions += ACTION_GROUPS["Kill"]
        gen.ENABLED_ACTIONS = sorted(list(set(actions)))

    def init_ui(self):
        self.btn_start = Button(20, 20, 90, 30, "Start", self.toggle_run)
        self.btn_pause = Button(120, 20, 60, 30, "Pause", self.toggle_pause)
        self.btn_clear = Button(190, 20, 60, 30, "Clear", self.clear_grid)
        self.btn_save = Button(20, 60, 125, 30, "Save", self.prompt_save)
        self.btn_load = Button(155, 60, 125, 30, "Load", self.prompt_load)
        y_tool = 100
        self.btn_tool_sel = Button(20, y_tool, 60, 30, "Sel", lambda: self.set_tool(0))
        self.btn_tool_bar = Button(90, y_tool, 60, 30, "Wall", lambda: self.set_tool(1))
        self.btn_tool_saf = Button(160, y_tool, 60, 30, "Zone", lambda: self.set_tool(2))
        self.btn_tool_era = Button(230, y_tool, 60, 30, "Erase", lambda: self.set_tool(3))
        y_toggle = 140
        t_w = 42
        self.btn_tog_vis = Button(20, y_toggle, t_w, 20, "Vis", lambda: self.toggle_trait("Vision"))
        self.btn_tog_sml = Button(20+t_w+5, y_toggle, t_w, 20, "Sml", lambda: self.toggle_trait("Smell"))
        self.btn_tog_osc = Button(20+(t_w+5)*2, y_toggle, t_w, 20, "Osc", lambda: self.toggle_trait("Osc"))
        self.btn_tog_mem = Button(20+(t_w+5)*3, y_toggle, t_w, 20, "Mem", lambda: self.toggle_trait("Mem"))
        self.btn_tog_emt = Button(20+(t_w+5)*4, y_toggle, t_w, 20, "Emt", lambda: self.toggle_trait("Emit"))
        self.btn_tog_kil = Button(20+(t_w+5)*5, y_toggle, t_w, 20, "Kil", lambda: self.toggle_trait("Kill"))
        y_slide = 175
        gap = 33
        self.sliders = [
            Slider(20, y_slide, 210, 12, 0.0, 0.1, self.mutation_rate, "Mut Rate", self.set_mut_rate),
            Slider(20, y_slide+gap, 210, 12, 0.0, 0.1, self.insertion_rate, "Ins Rate", self.set_ins_rate),
            Slider(20, y_slide+gap*2, 210, 12, 0.0, 0.1, self.deletion_rate, "Del Rate", self.set_del_rate),
            Slider(20, y_slide+gap*3, 210, 12, 0.0, 1.0, self.unequal_rate, "Unequal %", self.set_unequal_rate),
            Slider(20, y_slide+gap*4, 210, 12, 1, 5, self.brush_size, "Brush Size", self.set_brush_size, int_mode=True),
            Slider(20, y_slide+gap*5, 210, 12, 100, 5000, self.pop_size, "Pop Size", self.set_pop_size, int_mode=True),
            Slider(20, y_slide+gap*6, 210, 12, 4, 32, self.genome_len, "Genome Len", self.set_genome_len, int_mode=True),
            Slider(20, y_slide+gap*7, 210, 12, 100, 2000, self.steps_per_gen, "Steps/Gen", self.set_steps, int_mode=True)
        ]
        self.btn_stats = Button(20, 445, 100, 25, "Live Stats", lambda: self.analytics.open_window())
        self.btn_prune = Button(130, WINDOW_HEIGHT - 330, 150, 25, "Hide Dead Nodes", self.toggle_prune)
        self.btn_spawn_away = Button(20, WINDOW_HEIGHT - 330, 100, 25, "Spawn Away", self.toggle_spawn_away)
        self.buttons = [self.btn_start, self.btn_pause, self.btn_clear, self.btn_save, self.btn_load,
                        self.btn_tool_sel, self.btn_tool_bar, self.btn_tool_saf, self.btn_tool_era,
                        self.btn_tog_vis, self.btn_tog_sml, self.btn_tog_osc, self.btn_tog_mem, self.btn_tog_emt, self.btn_tog_kil,
                        self.btn_stats, self.btn_prune, self.btn_spawn_away]

    def toggle_trait(self, trait): self.enabled_traits[trait] = not self.enabled_traits[trait]; self.sync_genetic_config()
    def toggle_prune(self): self.hide_dead_nodes = not self.hide_dead_nodes
    def toggle_spawn_away(self): self.spawn_away = not self.spawn_away
    def prompt_save(self): self.input_mode, self.input_text = "SAVE", "level.json"
    def prompt_load(self): self.input_mode, self.input_text = "LOAD", "level.json"

    def perform_save(self):
        params = {"gen": self.generation, "step": self.step, "mut": self.mutation_rate, "ins": self.insertion_rate,
                  "del": self.deletion_rate, "uneq": self.unequal_rate, "pop": self.pop_size, "glen": self.genome_len,
                  "steps": self.steps_per_gen, "traits": self.enabled_traits, "spawn_away": self.spawn_away}
        save_simulation(self.input_text, self.grid, self.agents, params); self.input_mode = None

    def perform_load(self):
        res = load_simulation(self.input_text)
        if res:
            self.grid, self.agents, params = res
            self.generation, self.step = params.get("gen", 1), params.get("step", 0)
            self.mutation_rate, self.insertion_rate = params.get("mut", 0.01), params.get("ins", 0.01)
            self.deletion_rate, self.unequal_rate = params.get("del", 0.01), params.get("uneq", 0.0)
            self.pop_size, self.genome_len, self.steps_per_gen = params.get("pop", 1000), params.get("glen", 12), params.get("steps", 300)
            self.spawn_away = params.get("spawn_away", False)
            self.enabled_traits = params.get("traits", self.enabled_traits); self.sync_genetic_config()
            for i, p in enumerate([self.mutation_rate, self.insertion_rate, self.deletion_rate, self.unequal_rate]): self.sliders[i].value = p
            self.sliders[5].value, self.sliders[6].value, self.sliders[7].value = self.pop_size, self.genome_len, self.steps_per_gen
            self.sim_state, self.paused, self.selected_agent = "RUN", True, None
        self.input_mode = None

    def toggle_run(self):
        if self.sim_state == "EDIT": 
            self.sim_state, self.generation, self.step = "RUN", 1, 0; self.populate_world()
            self.analytics.history = {"generation": [], "survivors": [], "kills": [], "avg_len": []}
        else: self.sim_state, self.agents = "EDIT", []
    def toggle_pause(self): self.paused = not self.paused
    def clear_grid(self): self.grid, self.agents, self.selected_agent = Grid(GRID_SIZE), [], None
    def set_tool(self, mode): self.tool_mode = mode
    def set_mut_rate(self, val): self.mutation_rate = val
    def set_ins_rate(self, val): self.insertion_rate = val
    def set_del_rate(self, val): self.deletion_rate = val
    def set_unequal_rate(self, val): self.unequal_rate = val
    def set_brush_size(self, val): self.brush_size = int(val)
    def set_pop_size(self, val): self.pop_size = int(val)
    def set_genome_len(self, val): self.genome_len = int(val)
    def set_steps(self, val): self.steps_per_gen = int(val)

    def populate_world(self):
        self.agents = []
        self.current_gen_kills = 0
        self.grid.pheromones.fill(0)
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if not self.grid.is_barrier(x, y): self.grid.set(x, y, 0)
        for i in range(self.pop_size):
            loc = self.grid.find_empty_location(avoid_safe=self.spawn_away, margin=5)
            if loc: x, y = loc; self.agents.append(Agent(x, y, genome_length=self.genome_len, agent_id=i+1)); self.grid.set(x, y, i+1)

    def spawn_next_generation(self):
        survivors = [a for a in self.agents if a.alive and is_safe(a, self.grid)]
        num_survivors = len(survivors)
        alive_now = [a for a in self.agents if a.alive]
        avg_len = sum(len(a.genome) for a in alive_now) / max(1, len(alive_now))
        self.analytics.add_data(self.generation, num_survivors, self.current_gen_kills, avg_len)
        self.current_gen_kills = 0
        
        # Clustering Logic (Biologist view)
        if len(survivors) > 1:
            clusters = cluster_population(survivors)
            self.species_count = len(set(clusters))
        
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if not self.grid.is_barrier(x, y): self.grid.set(x, y, 0)
        new_agents = []
        if num_survivors == 0:
            for i in range(self.pop_size):
                loc = self.grid.find_empty_location(avoid_safe=self.spawn_away, margin=5)
                if loc: x, y = loc; new_agents.append(Agent(x, y, genome_length=self.genome_len, agent_id=i+1)); self.grid.set(x, y, i+1)
        else:
            for i in range(self.pop_size):
                p1, p2 = random.choice(survivors), random.choice(survivors)
                child_genome = gen.crossover_genomes(p1.genome, p2.genome, unequal_rate=self.unequal_rate)
                gen.mutate_genome(child_genome, mutation_rate=self.mutation_rate, insertion_rate=self.insertion_rate, deletion_rate=self.deletion_rate)
                loc = self.grid.find_empty_location(avoid_safe=self.spawn_away, margin=5)
                if loc: x, y = loc; new_agents.append(Agent(x, y, genome=child_genome, agent_id=i+1)); self.grid.set(x, y, i+1)
        self.agents, self.selected_agent = new_agents, None

    def run(self):
        running, mouse_down = True, False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if self.input_mode:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN: self.perform_save() if self.input_mode == "SAVE" else self.perform_load()
                        elif event.key == pygame.K_BACKSPACE: self.input_text = self.input_text[:-1]
                        elif event.key == pygame.K_ESCAPE: self.input_mode = None
                        else: self.input_text += event.unicode
                    continue
                self.btn_start.text = "Stop" if self.sim_state == "RUN" else "Start"; self.btn_pause.toggled = self.paused
                self.btn_tool_sel.toggled = (self.tool_mode == 0); self.btn_tool_bar.toggled = (self.tool_mode == 1)
                self.btn_tool_saf.toggled = (self.tool_mode == 2); self.btn_tool_era.toggled = (self.tool_mode == 3)
                self.btn_tog_vis.toggled, self.btn_tog_sml.toggled = self.enabled_traits["Vision"], self.enabled_traits["Smell"]
                self.btn_tog_osc.toggled, self.btn_tog_mem.toggled, self.btn_tog_emt.toggled, self.btn_tog_kil.toggled = self.enabled_traits["Osc"], self.enabled_traits["Mem"], self.enabled_traits["Emit"], self.enabled_traits["Kill"]
                self.btn_prune.toggled, self.btn_spawn_away.toggled = self.hide_dead_nodes, self.spawn_away
                self.btn_stats.toggled = self.analytics.is_open
                for btn in self.buttons: btn.handle_event(event)
                for sld in self.sliders: sld.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: mouse_down = True
                elif event.type == pygame.MOUSEBUTTONUP: mouse_down = False

            mx, my = pygame.mouse.get_pos()
            gx, gy = (mx - SIM_OFFSET_X) // CELL_SIZE if mx > PANEL_WIDTH and my < SIM_HEIGHT else -1, (my - SIM_OFFSET_Y) // CELL_SIZE if mx > PANEL_WIDTH and my < SIM_HEIGHT else -1
            if not self.input_mode:
                if mouse_down and gx != -1:
                    if self.sim_state == "EDIT" and self.tool_mode != 0:
                        r = self.brush_size - 1
                        for bx in range(gx - r, gx + r + 1):
                            for by in range(gy - r, gy + r + 1):
                                if 0 <= bx < GRID_SIZE and 0 <= by < GRID_SIZE:
                                    if self.tool_mode == 1: self.grid.set(bx, by, BARRIER)
                                    elif self.tool_mode == 2: self.grid.set_safe(bx, by, True)
                                    elif self.tool_mode == 3: self.grid.set(bx, by, 0); self.grid.set_safe(bx, by, False)
                    if self.tool_mode == 0 and 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
                        agent_id = self.grid.data[gx][gy]
                        if agent_id > 0:
                            for a in self.agents:
                                if a.id == agent_id: self.selected_agent = a; break
                        else: self.selected_agent = None
                if self.sim_state == "RUN" and not self.paused:
                    self.grid.update_pheromones(); random.shuffle(self.agents)
                    for agent in self.agents:
                        if not agent.alive: continue
                        dx, dy, action_levels = agent.think(self.grid, self.step)
                        if self.enabled_traits["Kill"]:
                            kill_val = math.tanh(action_levels[A_KILL])
                            if kill_val > 0.5:
                                fdx, fdy = agent.last_move
                                if fdx == 0 and fdy == 0: fdx = 1
                                tx, ty = agent.x + fdx, agent.y + fdy
                                if 0 <= tx < GRID_SIZE and 0 <= ty < GRID_SIZE:
                                    target_id = self.grid.data[tx][ty]
                                    if target_id > 0:
                                        for victim in self.agents:
                                            if victim.id == target_id: victim.alive, self.current_gen_kills = False, self.current_gen_kills + 1; self.grid.clear(tx, ty); break
                        if dx != 0 or dy != 0:
                            nx, ny = agent.x + dx, agent.y + dy
                            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and self.grid.is_empty(nx, ny):
                                self.grid.clear(agent.x, agent.y); agent.x, agent.y = nx, ny; self.grid.set(nx, ny, agent.id); agent.last_move = (dx, dy)
                    self.step += 1
                    if self.step >= self.steps_per_gen: self.spawn_next_generation(); self.step, self.generation, self.selected_agent = 0, self.generation + 1, None

            self.screen.fill(COLOR_BG); pygame.draw.rect(self.screen, COLOR_PANEL, (0, 0, PANEL_WIDTH, SIM_HEIGHT)); pygame.draw.line(self.screen, (100, 100, 100), (PANEL_WIDTH, 0), (PANEL_WIDTH, WINDOW_HEIGHT))
            for btn in self.buttons: btn.draw(self.screen, self.font)
            for sld in self.sliders: sld.draw(self.screen, self.font)
            stats_y = 480
            for i, line in enumerate([f"Gen: {self.generation}  Step: {self.step}", f"Pop: {len([a for a in self.agents if a.alive])}  FPS: {self.clock.get_fps():.1f}", f"Species: {self.species_count}"]):
                self.screen.blit(self.font.render(line, True, COLOR_TEXT), (20, stats_y + i*20))
            draw_brain(self.screen, self.selected_agent, pygame.Rect(10, SIM_HEIGHT - 300, PANEL_WIDTH - 20, 290), self.small_font, pygame.mouse.get_pos(), hide_dead=self.hide_dead_nodes)
            if self.selected_agent: 
                self.screen.blit(self.font.render(f"ID: {self.selected_agent.id} {'(DEAD)' if not self.selected_agent.alive else ''}", True, COLOR_HIGHLIGHT), (20, SIM_HEIGHT - 320))

            sim_rect = pygame.Rect(SIM_OFFSET_X, SIM_OFFSET_Y, GRID_SIZE*CELL_SIZE, GRID_SIZE*CELL_SIZE); pygame.draw.rect(self.screen, (0, 0, 0), sim_rect)
            ph_view = (self.grid.pheromones * 255).astype(np.uint8)
            for x in range(GRID_SIZE):
                for y in range(GRID_SIZE):
                    val = ph_view[x, y]
                    if val > 10: pygame.draw.rect(self.screen, (0, 0, val), (SIM_OFFSET_X + x * CELL_SIZE, SIM_OFFSET_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                    if self.grid.is_safe_tile(x, y): pygame.draw.rect(self.screen, COLOR_SAFE_ZONE, (SIM_OFFSET_X + x * CELL_SIZE, SIM_OFFSET_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                    if self.grid.is_barrier(x, y): pygame.draw.rect(self.screen, COLOR_BARRIER, (SIM_OFFSET_X + x * CELL_SIZE, SIM_OFFSET_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            for agent in self.agents:
                if not agent.alive: continue
                rect = (SIM_OFFSET_X + agent.x * CELL_SIZE, SIM_OFFSET_Y + agent.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                color = list(agent.color)
                if agent.kill_intent > 0.5: color = (255, 0, 0)
                pygame.draw.rect(self.screen, color, rect)
                if agent == self.selected_agent: pygame.draw.rect(self.screen, COLOR_HIGHLIGHT, rect, 2)
            pygame.draw.rect(self.screen, (100, 100, 100), sim_rect, 1)
            if not self.input_mode and self.sim_state == "EDIT" and self.tool_mode != 0 and gx != -1:
                r, sz = self.brush_size - 1, (2*(self.brush_size-1)+1)*CELL_SIZE; self.screen.blit(pygame.Surface((sz, sz), pygame.SRCALPHA), (SIM_OFFSET_X + (gx - r) * CELL_SIZE, SIM_OFFSET_Y + (gy - r) * CELL_SIZE)) # Simplified
            if self.input_mode:
                dr = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 - 50, 300, 100); pygame.draw.rect(self.screen, (50, 50, 60), dr); pygame.draw.rect(self.screen, (200, 200, 200), dr, 2)
                self.screen.blit(self.font.render("Save File:" if self.input_mode == "SAVE" else "Load File:", True, (255, 255, 255)), (dr.x + 10, dr.y + 10)); self.screen.blit(self.font.render(self.input_text + "|", True, (100, 255, 100)), (dr.x + 10, dr.y + 50))
            pygame.display.flip(); self.clock.tick(60)
        pygame.quit()