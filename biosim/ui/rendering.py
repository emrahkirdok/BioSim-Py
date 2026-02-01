import math
import pygame
from biosim.core.constants import *
from biosim.core.genome import genome_to_hex

def draw_brain(screen, agent, rect, font, mouse_pos=None):
    pygame.draw.rect(screen, (30, 30, 40), rect)
    pygame.draw.rect(screen, (100, 100, 100), rect, 1)
    
    if agent is None:
        text = font.render("Select an Agent", True, (100, 100, 100))
        screen.blit(text, text.get_rect(center=rect.center))
        return

    node_radius = 6
    input_x = rect.left + 50  
    output_x = rect.right - 50
    hidden_x = rect.centerx
    
    # Reserve space at bottom for Genome Hex
    genome_area_height = 40
    viz_height = rect.height - genome_area_height
    
    y_spacing = viz_height / (max(NUM_SENSORS, NUM_ACTIONS) + 1)
    
    node_positions = {}
    hovered_node = None
    
    # 1. Calculate Positions & Detect Hover
    for i in range(NUM_SENSORS):
        y = rect.top + (i + 1) * y_spacing
        pos = (input_x, y)
        node_positions[('S', i)] = pos
        if mouse_pos and math.hypot(mouse_pos[0]-pos[0], mouse_pos[1]-pos[1]) < node_radius + 5:
            hovered_node = ('S', i)

    for i in range(NUM_ACTIONS):
        y = rect.top + (i + 1) * y_spacing
        pos = (output_x, y)
        node_positions[('A', i)] = pos
        if mouse_pos and math.hypot(mouse_pos[0]-pos[0], mouse_pos[1]-pos[1]) < node_radius + 5:
            hovered_node = ('A', i)

    center_y = rect.top + viz_height / 2
    radius = min(rect.width, viz_height) / 4
    for i in range(MAX_NEURONS):
        angle = (2 * math.pi * i) / MAX_NEURONS
        nx = hidden_x + math.cos(angle) * radius
        ny = center_y + math.sin(angle) * radius
        pos = (nx, ny)
        node_positions[('N', i)] = pos
        if mouse_pos and math.hypot(mouse_pos[0]-pos[0], mouse_pos[1]-pos[1]) < node_radius + 5:
            hovered_node = ('N', i)

    # 2. Draw Connections
    for g in agent.genome:
        start_key = ('S' if g.source_type == 1 else 'N', g.source_num % (NUM_SENSORS if g.source_type==1 else MAX_NEURONS))
        end_key = ('A' if g.sink_type == 1 else 'N', g.sink_num % (NUM_ACTIONS if g.sink_type==1 else MAX_NEURONS))
        
        if start_key in node_positions and end_key in node_positions:
            start_pos = node_positions[start_key]
            end_pos = node_positions[end_key]
            
            is_highlighted = False
            is_dimmed = False
            
            if hovered_node:
                if start_key == hovered_node or end_key == hovered_node:
                    is_highlighted = True
                else:
                    is_dimmed = True
            
            if is_highlighted:
                width = max(2, int(abs(g.weight)) + 2)
                color = (50, 200, 255) if g.weight > 0 else (255, 50, 50)
            elif is_dimmed:
                width = 1
                color = (30, 30, 50) if g.weight > 0 else (50, 30, 30)
            else:
                width = max(1, int(abs(g.weight)))
                color = (0, 100, 200) if g.weight > 0 else (200, 0, 0)
            
            pygame.draw.line(screen, color, start_pos, end_pos, width)

    # 3. Draw Nodes
    for i in range(NUM_SENSORS):
        pos = node_positions[('S', i)]
        is_hover = hovered_node == ('S', i)
        col = (100, 255, 100) if is_hover else (0, 200, 0)
        pygame.draw.circle(screen, col, pos, node_radius + (2 if is_hover else 0))
        
        text_col = (150, 255, 150)
        if hovered_node and not is_hover: text_col = (60, 100, 60)
        
        name = SENSOR_NAMES.get(i, str(i))
        lbl = font.render(name, True, text_col)
        lbl_rect = lbl.get_rect(midright=(pos[0] - 10, pos[1]))
        screen.blit(lbl, lbl_rect)

    for i in range(NUM_ACTIONS):
        pos = node_positions[('A', i)]
        is_hover = hovered_node == ('A', i)
        col = (255, 100, 100) if is_hover else (200, 0, 0)
        pygame.draw.circle(screen, col, pos, node_radius + (2 if is_hover else 0))
        
        text_col = (255, 150, 150)
        if hovered_node and not is_hover: text_col = (100, 60, 60)

        name = ACTION_NAMES.get(i, str(i))
        lbl = font.render(name, True, text_col)
        lbl_rect = lbl.get_rect(midleft=(pos[0] + 10, pos[1]))
        screen.blit(lbl, lbl_rect)

    for i in range(MAX_NEURONS):
        pos = node_positions[('N', i)]
        is_hover = hovered_node == ('N', i)
        c_val = int((agent.neurons[i] + 1) * 127)
        base_col = (c_val, c_val, c_val)
        border_col = (255, 255, 255) if is_hover else (100, 100, 100)
        pygame.draw.circle(screen, base_col, pos, node_radius + (2 if is_hover else 0))
        pygame.draw.circle(screen, border_col, pos, node_radius + (2 if is_hover else 0), 1)

    # 4. Draw Genome String
    dna = genome_to_hex(agent.genome)
    # Truncate if too long to fit
    display_dna = dna[:64] + ("..." if len(dna) > 64 else "")
    
    # Draw label
    lbl_dna = font.render("Genome:", True, (150, 150, 150))
    screen.blit(lbl_dna, (rect.left + 5, rect.bottom - 35))
    
    # Draw Hex code (smaller font?)
    # Using existing font but maybe gray
    txt_dna = font.render(display_dna, True, (100, 200, 255))
    screen.blit(txt_dna, (rect.left + 5, rect.bottom - 20))