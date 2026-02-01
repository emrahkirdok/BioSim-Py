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
