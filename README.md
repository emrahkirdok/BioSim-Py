# Biosim4 Python Port

## Overview
This document tracks the effort to port the C++ **biosim4** biological simulation engine to Python. The goal is to create a more accessible, hackable, and cross-platform version of the simulation while maintaining the core biological algorithms.

## Current Status
We have successfully implemented three key prototypes demonstrating the core logic and visualization.

### 1. Genome & Wiring Logic (`python_genome_logic.py`)
*   **Purpose:** Replicates the C++ `Indiv::createWiringFromGenome` logic.
*   **Functionality:** 
    *   Generates random genomes (lists of genes).
    *   Maps large gene IDs to specific sensor/neuron/action ranges using modulo arithmetic.
    *   **Culling Algorithm:** Iteratively removes "useless" neurons (dead ends or self-loops) to optimize the neural net.
    *   **Renumbering:** Remaps surviving neurons to a clean sequential index.

### 2. CLI Proof of Concept (`biosim_python_poc.py`)
*   **Purpose:** A text-based simulation loop to verify the agent lifecycle.
*   **Functionality:**
    *   Implements the `Agent` class with a functional neural brain.
    *   **Feed-Forward Network:** Propagates signals from Sensors -> Neurons -> Actions.
    *   **Sensors:** Location (X, Y), Last Move Direction, Random input.
    *   **Actions:** Move X, Move Y.
    *   Runs a deterministic simulation loop and prints agent states to the console.

### 3. GUI Visualization (`biosim_gui.py`)
*   **Purpose:** A real-time visual representation of the simulation.
*   **Tech Stack:** `pygame`.
*   **Features:**
    *   **Grid World:** 128x128 grid rendered in an 800x800 window.
    *   **Visuals:** Agents are colored based on a hash of their genome (indicating "species") and dynamic internal state.
    *   **Interactive Controls:** Spacebar to pause, 'R' to reset.
    *   **Performance:** Capable of running ~500 agents at 60 FPS in pure Python.

## Technical Architecture

### The Genome
A genome is a list of **Genes**. Each gene represents a single connection in the brain.
*   **Source:** Sensor ID or Neuron ID.
*   **Sink:** Action ID or Neuron ID.
*   **Weight:** Float value (strength of connection).

### The Brain (Neural Net)
Unlike standard deep learning models (fixed layers), this brain is a **sparse, arbitrary graph**.
1.  **Sensing:** The agent reads its environment (Coordinates, Pheromones, Oscillator).
2.  **Thinking:** Inputs are multiplied by weights and summed at the target nodes. Activation function is `tanh`.
3.  **Acting:** Output nodes determine movement probability and other traits (color, responsiveness).

### Hardcoded Mappings
Just like the C++ version, specific IDs map to specific functions:
*   **Sensors:** 0=`LOC_X`, 1=`LOC_Y`, 2=`RANDOM`, etc.
*   **Actions:** 0=`MOVE_X`, 1=`MOVE_Y`, etc.

## Usage Instructions

### Prerequisites
*   Python 3.8+
*   Pygame

```bash
pip install pygame
```

### Running the Simulation
To run the interactive GUI:
```bash
python3 biosim_gui.py
```

To run the logic verification script:
```bash
python3 python_genome_logic.py
```

## Development Roadmap

### Phase 1: Optimization (The "Big Scale" Update)
*   **Current Limit:** ~500-1000 agents.
*   **Goal:** 5000+ agents.
*   **Strategy:** 
    *   Migrate data structures to **NumPy** arrays (Structure of Arrays pattern).
    *   Use **Numba** to JIT compile the hot paths (collision detection, neural feed-forward).

### Phase 2: Evolution
*   Implement `Survival Criteria` (who lives, who dies).
*   Implement `Reproduction`:
    *   **Sexual:** Crossover of two parent genomes.
    *   **Asexual:** Cloning with mutations (bit flips, insertions, deletions).
*   Add `Epoch` management to the main loop.

### Phase 3: Advanced Environment
*   Add **Pheromones** (Grid-based chemical trails).
*   Add **Barriers** (Walls).
*   Add **Killing** (Agents attacking each other).
