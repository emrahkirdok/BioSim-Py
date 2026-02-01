# Evolution Sandbox TODO

This file tracks advanced biological and algorithmic features for future investigation and implementation.

## 🧬 Biological Enhancements

### 1. Gene Duplication (Paralogy)
*   **Concept:** Instead of inserting a random gene, duplicate an existing one.
*   **Code Snippet:**
    ```python
    if random.random() < 0.8: # High chance of duplication
        gene_to_copy = random.choice(genome)
        genome.append(gene_to_copy.copy())
    else:
        genome.append(make_random_gene()) # Low chance of de novo creation
    ```
*   **Why:** Allows traits to be preserved in one copy while the other mutates freely.

### 2. Mutation Types Separation
*   **Concept:** Split mutation into "Weight Drift" and "Topology Shift".
*   **Goal:** Make weight changes frequent (0.1) and structural changes rare (0.001).
*   **Why:** Increases stability of evolved behaviors.

### 3. Diploidy (Two Sets of Genes)
*   **Concept:** Each agent has two versions of each gene (Dominant/Recessive).
*   **Why:** Protects against lethal mutations and increases genetic diversity.

---

## ⚙️ Engine & Simulation

### 1. Pheromones (Scent Trails)
*   **Implementation:** Add a "Scent" layer to the `Grid`.
*   **Actions:** `EmitScent`.
*   **Sensors:** `SmellScentForward`, `SmellScentLeft`, `SmellScentRight`.
*   **Physics:** Diffusion and Evaporation logic.

### 2. NumPy Vectorization
*   **Implementation:** Refactor `Grid` and `NeuralNet` math to use NumPy.
*   **Goal:** Support 10,000+ agents and larger grids (256x256).

### 3. Save/Load Level System
*   **Implementation:** Export/Import `GRID.barriers` and `GRID.safe_zones` as JSON or Binary.

---

## 📊 Analysis & visualization

### 1. Population Graphs
*   **Features:** Real-time plot of Survivor count vs Generation.
*   **Tool:** Integrate `matplotlib` or a custom lightweight grapher.

### 2. Lineage Tracking
*   **Concept:** Track the "Family Tree" of the most successful agent.
