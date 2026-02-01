import json
import os
from biosim.core.grid import Grid
from biosim.core.agent import Agent
from biosim.core.genome import genome_to_hex, genome_from_hex
from biosim.core.constants import BARRIER

def save_simulation(filename, grid, agents, params):
    """
    Saves the entire simulation state to a JSON file.
    """
    data = {
        "params": params,
        "grid": {
            "size": grid.size,
            "barriers": [],
            "safe_zones": []
        },
        "agents": []
    }

    # Serialize Grid
    for x in range(grid.size):
        for y in range(grid.size):
            if grid.is_barrier(x, y):
                data["grid"]["barriers"].append((x, y))
            if grid.is_safe_tile(x, y):
                data["grid"]["safe_zones"].append((x, y))

    # Serialize Agents
    for agent in agents:
        agent_data = {
            "id": agent.id,
            "x": agent.x,
            "y": agent.y,
            "genome": genome_to_hex(agent.genome)
        }
        data["agents"].append(agent_data)

    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Simulation saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False

def load_simulation(filename):
    """
    Loads simulation state from a JSON file.
    Returns: (grid, agents, params)
    """
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return None

    try:
        with open(filename, 'r') as f:
            data = json.load(f)

        # 1. Restore Params
        params = data.get("params", {})

        # 2. Restore Grid
        grid_data = data["grid"]
        size = grid_data["size"]
        grid = Grid(size)
        
        for x, y in grid_data["barriers"]:
            grid.set(x, y, BARRIER)
            
        for x, y in grid_data["safe_zones"]:
            grid.set_safe(x, y, True)

        # 3. Restore Agents
        agents = []
        for a_data in data["agents"]:
            # Reconstruct Brain
            genome = genome_from_hex(a_data["genome"])
            agent = Agent(a_data["x"], a_data["y"], genome=genome, agent_id=a_data["id"])
            agents.append(agent)
            
            # Place in grid if space available (avoids corruption if file bad)
            if not grid.is_barrier(agent.x, agent.y):
                grid.set(agent.x, agent.y, agent.id)

        print(f"Simulation loaded from {filename}")
        return grid, agents, params

    except Exception as e:
        print(f"Error loading file: {e}")
        return None
