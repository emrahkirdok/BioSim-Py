# Biosim4 Python Port

## Overview
This is a feature-rich port of the **biosim4** biological simulation engine to Python. It features a real-time GUI, an integrated Level Editor, and a sophisticated neural network visualization system.

The simulation models a population of agents that evolve over time to survive in a user-defined environment. Agents possess genomes that encode neural network brains, allowing them to sense their surroundings and make decisions.

## Key Features

### 1. Interactive Simulation & Level Editor
*   **Split-Screen Interface:** A control panel on the left and the simulation world on the right.
*   **Painting Tools:** Draw Barriers (Walls) and Safe Zones directly onto the grid.
*   **Physics Engine:** Collision detection prevents agents from moving through walls or overlapping with each other.
*   **Boundary Constraints:** Agents are confined to the 128x128 grid (no wrapping).

### 2. Biological Engine (`biosim_lib.py`)
*   **Genetics:** Agents have genomes (lists of genes) that can mutate and crossover (sexual reproduction).
*   **Neural Network:** 
    *   **Sensors:** Vision (Raycasting), Position, Randomness, Oscillator.
    *   **Actions:** Movement (Cardinal directions), Color change.
    *   **Hidden Layer:** Up to 10 internal neurons for complex processing.
*   **Evolution:** Agents that end the generation inside a "Safe Zone" survive and reproduce.

### 3. Inspection Tools
*   **Brain Visualizer:** Click on any agent to inspect its Neural Network in real-time.
    *   **Green Nodes:** Sensors (Inputs).
    *   **Red Nodes:** Actions (Outputs).
    *   **Connections:** Blue lines (Positive weights) and Red lines (Negative weights).
*   **Real-time Stats:** Track Generation, Step, Population Count, and FPS.

## User Manual

### Controls (Left Panel)
*   **Start/Stop:** Toggles between "Edit Mode" (Empty world) and "Run Mode" (Populated world).
*   **Pause:** Freezes the simulation loop without resetting the population.
*   **Clear:** Wipes the grid (removes barriers and zones).
*   **Tools:**
    *   **Sel:** Select an agent to inspect its brain.
    *   **Wall:** Draw grey barriers (agents cannot pass).
    *   **Zone:** Draw green safe zones (agents must be here to survive).
    *   **Erase:** Remove walls or zones.

### Parameters (Sliders)
*   **Mutation Rate:** Probability of gene mutation during reproduction (0.0 - 0.1).
*   **Brush Size:** Radius of the painting tool (1 - 5).
*   **Pop Size:** Target population for the next generation (100 - 5000).
*   **Genome Len:** Complexity of initial brains (4 - 32 genes).
*   **Steps/Gen:** Duration of a generation (100 - 2000 frames).

## Sensors & Actions

### Sensors (Inputs)
*   `LocX`, `LocY`: Normalized X/Y coordinates.
*   `Rnd`: Random noise.
*   `LmvX`, `LmvY`: Direction of last movement.
*   `Osc`: Sinewave oscillator (internal clock).
*   `DstBar`: Distance to nearest barrier forward (Raycast).
*   `DstSafe`: Distance to safe zone forward (Raycast).
*   `DensAg`: Density of agents forward.

### Actions (Outputs)
*   `MvX`, `MvY`: Movement velocity vector.
*   `MvFwd`: Move in previous direction.
*   `ColR`, `ColG`, `ColB`: Change body color.

## Installation & Usage

### Prerequisites
*   Python 3.8+
*   Pygame

```bash
pip install pygame
```

### Running the Application
```bash
cd biosim4_py
python3 biosim_gui.py
```

## Architecture
*   **`biosim_gui.py`**: Handles rendering, input, and the main application loop.
*   **`biosim_lib.py`**: Contains the core simulation logic (`Agent`, `Genome`, `Grid`, `Physics`, `Evolution`).