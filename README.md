# Biosim4 Python Port

## Overview
This is a feature-rich port of the **biosim4** biological simulation engine to Python. It features a real-time GUI, an integrated Level Editor, and a sophisticated neural network visualization system.

The simulation models a population of agents that evolve over time to survive in a user-defined environment. Agents possess genomes that encode neural network brains, allowing them to sense their surroundings and make decisions.

## 🧬 Biological Mechanisms

### 1. The Genome (DNA)
The genome is a list of **Genes**. Each gene describes a single connection in the agent's neural brain:
*   **Source:** Where the signal comes from (Sensor or Neuron).
*   **Sink:** Where the signal goes (Action or Neuron).
*   **Weight:** How strong the connection is (Positive = Excitatory, Negative = Inhibitory).

### 2. Point Mutation
*   **Trigger:** Happens during reproduction.
*   **Rate:** Controlled by the **Mutation Rate** slider (0% - 10% chance per gene).
*   **Effect:** Randomly modifies a single property of a gene:
    *   Switches input from Eye to Ear (Source Type).
    *   Rewires connection to a different muscle (Sink ID).
    *   Strengthens or weakens the synapse (Weight).

### 3. Indels (Insertion & Deletion)
*   **Trigger:** 5% chance per reproduction.
*   **Effect:**
    *   **Deletion:** Removes a random gene, potentially streamlining the brain or removing a useless trait.
    *   **Insertion:** Adds a completely random new gene, potentially creating a new behavior or "junk DNA".

### 4. Homologous Recombination (Crossover)
This simulation uses an advanced **String-Based Recombination** method:
1.  **Transcription:** Parent genomes are converted into Hexadecimal strings (e.g., `85A2...`).
2.  **Alignment:** The two DNA strings are aligned.
3.  **Crossover:** A random cut point is chosen along the string length.
4.  **Splicing:** The Child inherits the left part of Parent A and the right part of Parent B.
*   **Hybrid Genes:** Because the cut can happen *inside* a gene's hex code, this can fuse the Input of one parent's gene with the Output of the other, creating entirely new functional connections.

---

## Key Features

### 1. Interactive Simulation & Level Editor
*   **Split-Screen Interface:** A control panel on the left and the simulation world on the right.
*   **Painting Tools:** Draw Barriers (Walls) and Safe Zones directly onto the grid.
*   **Physics Engine:** Collision detection prevents agents from moving through walls or overlapping with each other.
*   **Boundary Constraints:** Agents are confined to the 128x128 grid (no wrapping).

### 2. Inspection Tools
*   **Brain Visualizer:** Click on any agent to inspect its Neural Network in real-time.
    *   **Interactive Highlight:** Hover over nodes to isolate specific connections.
    *   **Labels:** See exactly which sensor (e.g., `DstBar`) connects to which action (`MvFwd`).
    *   **Genome Inspector:** View the raw Hex DNA string of the selected agent.
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
*   **Mutation Rate:** Probability of gene mutation (0.0 - 0.1).
*   **Brush Size:** Radius of the painting tool (1 - 5).
*   **Pop Size:** Target population for the next generation (100 - 5000).
*   **Genome Len:** Complexity of initial brains (4 - 32 genes).
*   **Steps/Gen:** Duration of a generation (100 - 2000 frames).

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
python3 main.py
```