import random
import copy
from biosim.core.constants import *

# Global Config
ENABLED_SENSORS = list(range(NUM_SENSORS))
ENABLED_ACTIONS = list(range(NUM_ACTIONS))

class Gene:
    __slots__ = ('source_type', 'source_num', 'sink_type', 'sink_num', 'weight')
    def __init__(self):
        self.source_type = 0 
        self.source_num = 0
        self.sink_type = 0   
        self.sink_num = 0
        self.weight = 0.0
    
    def copy(self):
        g = Gene(); g.source_type, g.source_num = self.source_type, self.source_num
        g.sink_type, g.sink_num, g.weight = self.sink_type, self.sink_num, self.weight
        return g

    def to_32bit_int(self):
        """Packs gene into a 32-bit integer."""
        src_id = self.source_num & 0x7F
        snk_id = self.sink_num & 0x7F
        w_int = int(self.weight * 8192.0)
        w_int = max(-32768, min(32767, w_int)) & 0xFFFF 
        return (self.source_type << 31) | (src_id << 24) | (self.sink_type << 23) | (snk_id << 16) | w_int

    def to_hex(self):
        return f"{self.to_32bit_int():08X}"

    def to_binary(self):
        """Returns 32-character binary string."""
        return f"{self.to_32bit_int():032b}"

    @staticmethod
    def from_32bit_int(val):
        g = Gene()
        g.source_type = (val >> 31) & 1
        g.source_num = (val >> 24) & 0x7F
        g.sink_type = (val >> 23) & 1
        g.sink_num = (val >> 16) & 0x7F
        w_int = val & 0xFFFF
        if w_int >= 0x8000: w_int -= 0x10000
        g.weight = w_int / 8192.0
        return g

    @staticmethod
    def from_hex(hex_str):
        return Gene.from_32bit_int(int(hex_str, 16))

    @staticmethod
    def from_binary(bin_str):
        return Gene.from_32bit_int(int(bin_str, 2))

def genome_to_hex(genome): return "".join([g.to_hex() for g in genome])
def genome_from_hex(hex_str):
    return [Gene.from_hex(hex_str[i:i+8]) for i in range(0, len(hex_str), 8) if len(hex_str[i:i+8]) == 8]

def genome_to_binary(genome): return "".join([g.to_binary() for g in genome])
def genome_from_binary(bin_str):
    return [Gene.from_binary(bin_str[i:i+32]) for i in range(0, len(bin_str), 32) if len(bin_str[i:i+32]) == 32]

def make_random_gene():
    g = Gene(); g.source_type = random.choice([0, 1])
    g.source_num = random.choice(ENABLED_SENSORS) if g.source_type == 1 else random.randint(0, MAX_NEURONS - 1)
    g.sink_type = random.choice([0, 1])
    g.sink_num = random.choice(ENABLED_ACTIONS) if g.sink_type == 1 else random.randint(0, MAX_NEURONS - 1)
    g.weight = (random.random() * 8.0) - 4.0
    return g

def mutate_genome(genome, mutation_rate=0.01, insertion_rate=0.05, deletion_rate=0.05):
    for gene in genome:
        if random.random() < mutation_rate:
            trait = random.randint(0, 4)
            if trait == 0: gene.source_type ^= 1
            elif trait == 1: 
                if gene.source_type == 1: gene.source_num = random.choice(ENABLED_SENSORS)
                else: gene.source_num = random.randint(0, MAX_NEURONS - 1)
            elif trait == 2: gene.sink_type ^= 1
            elif trait == 3:
                if gene.sink_type == 1: gene.sink_num = random.choice(ENABLED_ACTIONS)
                else: gene.sink_num = random.randint(0, MAX_NEURONS - 1)
            elif trait == 4: gene.weight += (random.random() - 0.5) * 2.0
    if random.random() < deletion_rate and len(genome) > 1: del genome[random.randint(0, len(genome)-1)]
    if random.random() < insertion_rate: genome.append(make_random_gene())

def recombine_dna(dna1, dna2):
    limit = min(len(dna1), len(dna2))
    if limit < 2: return dna1
    pivot = random.randint(1, limit - 1)
    return dna1[:pivot] + dna2[pivot:]

def recombine_dna_unequal(dna1, dna2):
    len1, len2 = len(dna1), len(dna2)
    pivot1 = random.randint(0, len1)
    jitter = random.randint(-16, 16)
    pivot2 = max(0, min(len2, pivot1 + jitter))
    return dna1[:pivot1] + dna2[pivot2:]

def crossover_genomes(g1, g2, unequal_rate=0.0):
    dna1, dna2 = genome_to_hex(g1), genome_to_hex(g2)
    child_dna = recombine_dna_unequal(dna1, dna2) if random.random() < unequal_rate else recombine_dna(dna1, dna2)
    return genome_from_hex(child_dna)
