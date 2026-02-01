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
        """Encodes gene into an 8-character hex string (32-bit packed)."""
        # Pack bits: 
        # [31: SrcT] [30-24: SrcID] [23: SnkT] [22-16: SnkID] [15-0: Weight]
        
        # Clamp IDs to 7 bits (0-127)
        src_id = self.source_num & 0x7F
        snk_id = self.sink_num & 0x7F
        
        # Convert float weight back to 16-bit int (scaled by 8192)
        # Clamp to signed 16-bit range (-32768 to 32767)
        w_int = int(self.weight * 8192.0)
        w_int = max(-32768, min(32767, w_int))
        w_int &= 0xFFFF # Mask to 16 bits
        
        packed = (self.source_type << 31) | (src_id << 24) | \
                 (self.sink_type << 23) | (snk_id << 16) | \
                 w_int
                 
        return f"{packed:08X}"

    @staticmethod
    def from_hex(hex_str):
        """Decodes an 8-character hex string into a Gene."""
        val = int(hex_str, 16)
        g = Gene()
        
        g.source_type = (val >> 31) & 1
        g.source_num = (val >> 24) & 0x7F
        g.sink_type = (val >> 23) & 1
        g.sink_num = (val >> 16) & 0x7F
        
        # Weight is signed 16-bit
        w_int = val & 0xFFFF
        if w_int >= 0x8000:
            w_int -= 0x10000
        g.weight = w_int / 8192.0
        
        return g

def genome_to_hex(genome):
    """Converts a list of Genes to a single hex string."""
    return "".join([g.to_hex() for g in genome])

def genome_from_hex(hex_str):
    """Converts a hex string back to a list of Genes."""
    # Chunk into 8 chars
    genes = []
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

def crossover_genomes(g1, g2):
    if len(g1) == 0: return [g.copy() for g in g2]
    if len(g2) == 0: return [g.copy() for g in g1]
    child_genome = []
    pivot = random.randint(0, min(len(g1), len(g2)))
    for i in range(pivot): child_genome.append(g1[i].copy())
    for i in range(pivot, len(g2)): child_genome.append(g2[i].copy())
    return child_genome