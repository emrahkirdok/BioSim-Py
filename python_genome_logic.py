import random
import copy

# --- Configuration Constants (mimicking biosim4.ini) ---
MAX_NEURONS = 10    # p.maxNumberNeurons
NUM_SENSORS = 4     # Sensor::NUM_SENSES
NUM_ACTIONS = 4     # Action::NUM_ACTIONS

# Enum-like constants
NEURON = 0
SENSOR = 1
ACTION = 1  # In C++ source sinkType=1 is ACTION

class Gene:
    """
    Represents one connection (edge) in the graph.
    """
    def __init__(self):
        self.source_type = 0  # 0: NEURON, 1: SENSOR
        self.source_num = 0   # ID
        self.sink_type = 0    # 0: NEURON, 1: ACTION
        self.sink_num = 0     # ID
        self.weight = 0.0

    def __repr__(self):
        src_label = f"Sens({self.source_num})" if self.source_type == SENSOR else f"Neur({self.source_num})"
        sink_label = f"Act({self.sink_num})" if self.sink_type == ACTION else f"Neur({self.sink_num})"
        return f"[{src_label} -> {sink_label} w={self.weight:.2f}]"

    @staticmethod
    def make_random():
        g = Gene()
        g.source_type = random.choice([NEURON, SENSOR])
        g.source_num = random.randint(0, 127) # 7-bit simulation
        g.sink_type = random.choice([NEURON, ACTION])
        g.sink_num = random.randint(0, 127)   # 7-bit simulation
        # Weight: random float between -4.0 and 4.0 (approx C++ logic)
        g.weight = (random.random() * 8.0) - 4.0
        return g

class NeuronNode:
    """Helper struct for the culling process."""
    def __init__(self):
        self.num_outputs = 0
        self.num_self_inputs = 0
        self.remapped_number = -1

def create_wiring_from_genome(genome):
    """
    The core logic ported from Indiv::createWiringFromGenome
    """
    
    # 1. Make Renumbered Connection List
    # Map the raw random IDs to the valid ranges (modulo operator)
    connection_list = copy.deepcopy(genome)
    for conn in connection_list:
        if conn.source_type == NEURON:
            conn.source_num %= MAX_NEURONS
        else:
            conn.source_num %= NUM_SENSORS
            
        if conn.sink_type == NEURON:
            conn.sink_num %= MAX_NEURONS
        else:
            conn.sink_num %= NUM_ACTIONS

    # 2. Make Node List (Build the Graph)
    # Track inputs/outputs to identify useless neurons
    node_map = {} # Key: neuron_id, Value: NeuronNode

    for conn in connection_list:
        # If sink is a neuron, ensure it exists in map and count inputs
        if conn.sink_type == NEURON:
            if conn.sink_num not in node_map:
                node_map[conn.sink_num] = NeuronNode()
            
            node = node_map[conn.sink_num]
            if conn.source_type == NEURON and conn.source_num == conn.sink_num:
                node.num_self_inputs += 1
            # Note: We don't track other inputs specifically for culling, 
            # only need output counts to detect dead ends.

        # If source is a neuron, ensure it exists and count outputs
        if conn.source_type == NEURON:
            if conn.source_num not in node_map:
                node_map[conn.source_num] = NeuronNode()
            node_map[conn.source_num].num_outputs += 1

    # 3. Cull Useless Neurons
    # Remove neurons that have no outputs, or only output to themselves.
    # Repeat until no more changes occur.
    all_done = False
    while not all_done:
        all_done = True
        # Create a list of keys to remove to avoid modifying dict while iterating
        neurons_to_remove = []

        for neuron_id, node in node_map.items():
            # Criterion: Dead end or pure self-loop
            if node.num_outputs == node.num_self_inputs:
                all_done = False
                neurons_to_remove.append(neuron_id)

        # Remove the marked neurons and their connections
        for dead_neuron_id in neurons_to_remove:
            # Remove from map
            del node_map[dead_neuron_id]

            # Remove connections pointing TO this neuron
            # (And decrement the output count of the source neuron!)
            new_connection_list = []
            for conn in connection_list:
                if conn.sink_type == NEURON and conn.sink_num == dead_neuron_id:
                    # This connection feeds the dead neuron.
                    # If the source was a neuron, its output count decreases.
                    if conn.source_type == NEURON and conn.source_num in node_map:
                        node_map[conn.source_num].num_outputs -= 1
                    # Do not add to new list (effectively erasing it)
                else:
                    new_connection_list.append(conn)
            connection_list = new_connection_list

    # 4. Renumbering
    # Assign new sequential IDs (0, 1, 2...) to the surviving neurons
    new_number = 0
    # Sorting keys ensures deterministic remapping (C++ map is ordered)
    for neuron_id in sorted(node_map.keys()):
        node_map[neuron_id].remapped_number = new_number
        new_number += 1

    print(f"DEBUG: {len(node_map)} neurons survived culling out of {MAX_NEURONS} max.")

    # 5. Final Wiring
    # Apply the new IDs to the connections
    final_net = []
    
    # Pass 1: Neuron -> Neuron connections
    for conn in connection_list:
        if conn.sink_type == NEURON:
            # Update sink
            conn.sink_num = node_map[conn.sink_num].remapped_number
            # Update source if it's a neuron
            if conn.source_type == NEURON:
                conn.source_num = node_map[conn.source_num].remapped_number
            final_net.append(conn)

    # Pass 2: Neuron -> Action connections
    for conn in connection_list:
        if conn.sink_type == ACTION:
            # Update source if it's a neuron
            if conn.source_type == NEURON:
                conn.source_num = node_map[conn.source_num].remapped_number
            final_net.append(conn)

    return final_net, len(node_map)

# --- Main Test ---
if __name__ == "__main__":
    print(f"Generating random genome (Simulating C++ logic)...")
    print(f"Max Neurons Allowed: {MAX_NEURONS}")
    
    # Create a random genome
    genome = [Gene.make_random() for _ in range(15)]
    
    print("\n--- Raw Genome (Genes) ---")
    for i, g in enumerate(genome):
        print(f"{i}: {g}")

    # Compile it
    print("\n--- Compiling to Neural Net ---")
    net, active_neurons = create_wiring_from_genome(genome)

    print(f"\n--- Final Neural Net ({active_neurons} active neurons) ---")
    for g in net:
        print(g)
