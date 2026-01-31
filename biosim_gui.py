import random
import math
import sys
import pygame

import biosim_lib as bs

# --- Configuration ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
GRID_SIZE = 128
CELL_SIZE = WINDOW_WIDTH // GRID_SIZE

POPULATION_SIZE = 1000  # Increased population to see collision effects
STEPS_PER_GEN = 300

COLOR_BG = (10, 10, 10)
COLOR_TEXT = (200, 200, 200)
COLOR_SAFE_ZONE = (0, 40, 0)

CHALLENGE_TYPE = 0 

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
    
    # Clear grid for new generation
    grid.data = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    new_agents = []
    
    if num_survivors == 0:
        print("EXTINCTION! Respawning random population.")
        for i in range(POPULATION_SIZE):
            loc = grid.find_empty_location()
            if loc:
                x, y = loc
                new_agents.append(bs.Agent(x, y, agent_id=i+1))
                grid.set(x, y, i+1)
    else:
        print(f"Survivors: {num_survivors}/{len(agents)}. Reproducing...")
        for i in range(POPULATION_SIZE):
            p1 = random.choice(survivors)
            p2 = random.choice(survivors)
            child_genome = bs.crossover_genomes(p1.genome, p2.genome)
            bs.mutate_genome(child_genome)
            
            loc = grid.find_empty_location()
            if loc:
                x, y = loc
                new_agents.append(bs.Agent(x, y, genome=child_genome, agent_id=i+1))
                grid.set(x, y, i+1)
            
    return new_agents

def main():
    global CHALLENGE_TYPE
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("BioSim Python: Collision & Physics")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 16)

    # Initialize Grid and Population
    grid = bs.Grid(GRID_SIZE)
    agents = []
    for i in range(POPULATION_SIZE):
        loc = grid.find_empty_location()
        if loc:
            x, y = loc
            agents.append(bs.Agent(x, y, agent_id=i+1))
            grid.set(x, y, i+1)

    generation = 1
    step = 0
    running = True
    paused = False

    while running:
        global CHALLENGE_TYPE
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: paused = not paused
                elif event.key == pygame.K_c: CHALLENGE_TYPE = (CHALLENGE_TYPE + 1) % 2

        if not paused:
            # Randomize update order to prevent movement bias (important for collisions!)
            random.shuffle(agents)
            
            for agent in agents:
                # 1. THINK
                dx, dy, action_levels = agent.think(GRID_SIZE, step)
                
                # 2. RESOLVE MOVEMENT (Collision Detection)
                if dx != 0 or dy != 0:
                    new_x = agent.x + dx
                    new_y = agent.y + dy
                    
                    # Boundary Check (No Wrapping)
                    if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
                        # Occupancy Check
                        if grid.is_empty(new_x, new_y):
                            # Move successful
                            grid.clear(agent.x, agent.y)
                            agent.x, agent.y = new_x, new_y
                            grid.set(agent.x, agent.y, agent.id)
                            agent.last_move = (dx, dy)
                        else:
                            # Collision! Stay put.
                            agent.last_move = (0, 0)
                    else:
                        # Border hit! Stay put.
                        agent.last_move = (0, 0)

            step += 1
            if step >= STEPS_PER_GEN:
                agents = spawn_next_generation(agents, grid)
                step = 0
                generation += 1

        # Render
        screen.fill(COLOR_BG)
        
        # Draw Safe Zone
        if CHALLENGE_TYPE == 0:
            pygame.draw.rect(screen, COLOR_SAFE_ZONE, (WINDOW_WIDTH // 2, 0, WINDOW_WIDTH // 2, WINDOW_HEIGHT))
        else:
            pygame.draw.circle(screen, COLOR_SAFE_ZONE, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), (GRID_SIZE // 4) * CELL_SIZE)

        # Draw Agents
        for agent in agents:
            rect = (agent.x * CELL_SIZE, agent.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, agent.color, rect)

        # UI
        overlay = [
            f"Gen: {generation}",
            f"Step: {step}/{STEPS_PER_GEN}",
            f"Pop: {len(agents)}",
            f"FPS: {clock.get_fps():.1f}",
            "Mode: No-Wrap / Collision On"
        ]
        for i, line in enumerate(overlay):
            screen.blit(font.render(line, True, COLOR_TEXT), (10, 10 + i * 20))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
