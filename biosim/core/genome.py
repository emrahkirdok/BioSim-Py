import random
import copy
from biosim.core.constants import *

class Gene:
    __slots__ = ('source_type', 'source_num', 'sink_type', 'sink_num', 'weight')
    def __init__(self):
        self.source_type = 0 
        self.source_num = 0
        self.sink_type = 0   
        self.sink_num = 0
        self.weight = 0.0
    
    def copy(self):
        g = Gene()
        g.source_type = self.source_type
        g.source_num = self.source_num
        g.sink_type = self.sink_type
        g.sink_num = self.sink_num
        g.weight = self.weight
        return g

    def to_hex(self):
        src_id = self.source_num & 0x7F
        snk_id = self.sink_num & 0x7F
        w_int = int(self.weight * 8192.0)
        w_int = max(-32768, min(32767, w_int))
        w_int &= 0xFFFF 
        packed = (self.source_type << 31) | (src_id << 24) | \
                 (self.sink_type << 23) | (snk_id << 16) | \
                 w_int
        return f"{packed:08X}"

    @staticmethod
    def from_hex(hex_str):
        val = int(hex_str, 16)
        g = Gene()
        g.source_type = (val >> 31) & 1
        g.source_num = (val >> 24) & 0x7F
        g.sink_type = (val >> 23) & 1
        g.sink_num = (val >> 16) & 0x7F
        w_int = val & 0xFFFF
        if w_int >= 0x8000: w_int -= 0x10000
        g.weight = w_int / 8192.0
        return g

def genome_to_hex(genome):
    return "".join([g.to_hex() for g in genome])

def genome_from_hex(hex_str):
    genes = []
    # Ensure 8-char alignment for safety, though hybrid genes are allowed
    # If a split happened mid-gene, the new hex string is still valid hex, 
    # just representing a fused gene.
    for i in range(0, len(hex_str), 8):
        chunk = hex_str[i:i+8]
        if len(chunk) == 8:
            genes.append(Gene.from_hex(chunk))
    return genes

def make_random_gene():
    g = Gene()
    g.source_type = random.choice([0, 1])
    g.source_num = random.randint(0, 127)
    g.sink_type = random.choice([0, 1])
    g.sink_num = random.randint(0, 127)
    g.weight = (random.random() * 8.0) - 4.0
    return g

def mutate_genome(genome, mutation_rate=0.01):
    for gene in genome:
        if random.random() < mutation_rate:
            trait = random.randint(0, 4)
            if trait == 0: gene.source_type ^= 1
            elif trait == 1: gene.source_num ^= random.randint(1, 127)
            elif trait == 2: gene.sink_type ^= 1
            elif trait == 3: gene.sink_num ^= random.randint(1, 127)
            elif trait == 4: gene.weight += (random.random() - 0.5) * 2.0
    if random.random() < 0.05:
        if random.random() < 0.5 and len(genome) > 1:
            del genome[random.randint(0, len(genome)-1)]
        else:
            genome.append(make_random_gene())

def recombine_dna(dna1, dna2):
    """
    Homologous Recombination on DNA strings.
    Allows crossover at any character index (4-bit boundary).
    """
    if not dna1: return dna2
    if not dna2: return dna1
    
    limit = min(len(dna1), len(dna2))
    if limit < 2: return dna1
    
    pivot = random.randint(1, limit - 1)
    return dna1[:pivot] + dna2[pivot:]

def crossover_genomes(g1, g2):
    """
    Wrapper that converts to DNA, recombines, and converts back.
    """
    dna1 = genome_to_hex(g1)
    dna2 = genome_to_hex(g2)
    child_dna = recombine_dna(dna1, dna2)
    return genome_from_hex(child_dna)
