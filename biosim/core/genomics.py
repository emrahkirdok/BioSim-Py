import numpy as np
from biosim.core.genome import genome_to_binary

def calculate_hamming_distance(dna1_bin, dna2_bin):
    """Calculates number of bit differences between two binary strings."""
    # Ensure equal length for comparison
    length = min(len(dna1_bin), len(dna2_bin))
    if length == 0: return 1.0
    
    diffs = 0
    for i in range(length):
        if dna1_bin[i] != dna2_bin[i]:
            diffs += 1
            
    # Add length difference penalty
    diffs += abs(len(dna1_bin) - len(dna2_bin))
    return diffs / max(len(dna1_bin), len(dna2_bin))

def cluster_population(agents):
    """
    Groups agents by genetic similarity.
    Returns: List of Cluster IDs for each agent.
    """
    if len(agents) < 2: return [0] * len(agents)
    
    # 1. Convert all to binary
    dnas = [genome_to_binary(a.genome) for a in agents]
    
    # 2. Simplistic clustering (e.g., prefix matching or hash-based)
    # For a real scientific version, we'd use scipy.cluster.hierarchy here.
    # But since we want to avoid extra dependencies for now, let's use 
    # a simple 'Similarity Grouping' algorithm.
    
    clusters = [-1] * len(agents)
    current_cluster = 0
    threshold = 0.2 # 20% bit difference max
    
    for i in range(len(agents)):
        if clusters[i] != -1: continue
        
        clusters[i] = current_cluster
        for j in range(i + 1, len(agents)):
            if clusters[j] == -1:
                dist = calculate_hamming_distance(dnas[i], dnas[j])
                if dist < threshold:
                    clusters[j] = current_cluster
        current_cluster += 1
        
    return clusters
