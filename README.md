# BioSim-Py

## Overview
**BioSim-Py** is a high-performance, feature-rich port of the **biosim4** biological simulation engine to Python. It combines a real-time GUI, an integrated Level Editor, and a sophisticated neural network visualization system to create a powerful laboratory for exploring artificial life and neuroevolution.

The simulation models a population of agents that evolve over time to survive in user-defined environments. Agents possess genomes that encode sparse-graph neural network brains, allowing them to sense their surroundings and make emergent behavioral decisions.

## 🧬 Biological Mechanisms

### 1. The Genome (Hex DNA)
Each organism's blueprint is stored as a list of **Genes**, which can be serialized into a compact **Hexadecimal String** (DNA). Each gene describes a single connection in the agent's brain:
*   **Source:** Signal origin (Sensor or Internal Neuron).
*   **Sink:** Signal destination (Action or Internal Neuron).
*   **Weight:** Connection strength (Excitatory or Inhibitory).

### 2. Mutation Types
*   **Point Mutation:** Randomly modifies a single property of a gene (Rate: 0% - 10%).
*   **Insertions & Deletions (Indels):** Dynamically changes genome length, adding or removing connections (Rate: 0% - 10%).
*   **Gene Duplication:** Through **Unequal Recombination**, segments of the genome can be duplicated, providing "spare copies" for future evolution.

### 3. Homologous Recombination (Crossover)
BioSim-Py uses an advanced **String-Based Recombination** method that mimics biological chiasmata:
*   **Equal Crossover:** Parent DNA strings are spliced at a common point.
*   **Unequal Crossover:** Misalignment during splicing creates duplications and deletions.
*   **Hybrid Genes:** Cuts occurring *inside* a gene's 32-bit code can fuse the input of one parent with the output of another, creating de novo functional connections.

---

## 🚀 Key Features

### 1. Interactive Level Editor
*   **Live Painting:** Use tools to draw **Barriers** (Grey) and **Safe Zones** (Green) directly on the 128x128 grid.
*   **Brush Preview:** A semi-transparent cursor helper that adapts to your brush size for precise design.
*   **Physics Engine:** Collision detection prevents agents from overlapping or passing through walls.

### 2. Swarm Intelligence & Pheromones
*   **Vectorized Diffusion:** Chemical trails "bleed" and spread across the grid using high-performance **NumPy** matrix math.
*   **Gradient Sensing:** New sensors (`SmlFwd`, `SmlLR`) allow agents to detect scent intensity and compare left/right gradients, enabling the evolution of trail-following and swarming.

### 3. Inspection & Analytics
*   **Real-time Brain Viz:** Select any agent to watch its neurons fire. 
    *   **Interactive Highlight:** Hover over any node to light up all its incoming and outgoing connections.
    *   **Hide Dead Nodes:** A toggle to filter out unconnected/vestigial neurons for a clearer view.
*   **Genome Inspector:** A dedicated bar at the bottom displays the full raw DNA hex string of the selected organism.

## 🎮 User Manual

### Controls (Left Panel)
*   **Start/Stop:** Switch between "Edit Mode" (Level Design) and "Run Mode" (Evolution).
*   **Pause:** Freeze the simulation to inspect agents without resetting.
*   **Clear:** Wipe all level geometry.
*   **Save/Load:** Export and Import levels and populations as JSON files via interactive dialogs.

### Parameters
*   **Genetic Sliders:** Control Mut/Ins/Del/Unequal rates in real-time.
*   **Environment:** Adjust Population Size, Genome Complexity, and Generation Duration.
*   **Trait Toggles:** Enable or disable entire sensory systems (Vision, Smell, Memory, etc.) on demand.

## 🛠 Installation & Usage

### Prerequisites
*   Python 3.8+
*   Pygame
*   NumPy

```bash
pip install pygame numpy
```

### Running the Application
```bash
cd biosim4_py
python3 main.py
```

## 🏗 Architecture
The project is built as a modular Python package:
*   **`biosim/core/`**: Simulation logic (Physics, Biology, Grid).
*   **`biosim/ui/`**: Presentation layer (App loop, Widgets, Rendering).
*   **`main.py`**: Lightweight entry point.
