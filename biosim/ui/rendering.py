import math
import pygame
from biosim.core.constants import *
from biosim.core.genome import genome_to_hex

def draw_brain(screen, agent, rect, font, mouse_pos=None, hide_dead=False):
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
    y_spacing = rect.height / (max(NUM_SENSORS, NUM_ACTIONS) + 1)
    
    node_positions = {}
    hovered_node = None
    
    # 1. Identify Connected Nodes
    connected_neurons = set()
    used_sensors = set()
    used_actions = set()
    
    for g in agent.genome:
        src_id = g.source_num % (NUM_SENSORS if g.source_type==1 else MAX_NEURONS)
        snk_id = g.sink_num % (NUM_ACTIONS if g.sink_type==1 else MAX_NEURONS)
        
        if g.source_type == 1: used_sensors.add(src_id)
        else: connected_neurons.add(src_id)
            
        if g.sink_type == 1: used_actions.add(snk_id)
        else: connected_neurons.add(snk_id)

    # 2. Calculate Positions
    # Sensors
    for i in range(NUM_SENSORS):
        if hide_dead and i not in used_sensors: continue
        y = rect.top + (i + 1) * y_spacing
        pos = (input_x, y)
        node_positions[('S', i)] = pos
        if mouse_pos and math.hypot(mouse_pos[0]-pos[0], mouse_pos[1]-pos[1]) < node_radius + 5:
            hovered_node = ('S', i)

    # Actions
    for i in range(NUM_ACTIONS):
        if hide_dead and i not in used_actions: continue
        y = rect.top + (i + 1) * y_spacing
        pos = (output_x, y)
        node_positions[('A', i)] = pos
        if mouse_pos and math.hypot(mouse_pos[0]-pos[0], mouse_pos[1]-pos[1]) < node_radius + 5:
            hovered_node = ('A', i)

    # Hidden
    center_y = rect.centery
    radius = min(rect.width, rect.height) / 4
    for i in range(MAX_NEURONS):
        if hide_dead and i not in connected_neurons: continue
        angle = (2 * math.pi * i) / MAX_NEURONS
        nx = hidden_x + math.cos(angle) * radius
        ny = center_y + math.sin(angle) * radius
        pos = (nx, ny)
        node_positions[('N', i)] = pos
        if mouse_pos and math.hypot(mouse_pos[0]-pos[0], mouse_pos[1]-pos[1]) < node_radius + 5:
            hovered_node = ('N', i)

    # 3. Draw Connections
    for g in agent.genome:
        start_key = ('S' if g.source_type == 1 else 'N', g.source_num % (NUM_SENSORS if g.source_type==1 else MAX_NEURONS))
        end_key = ('A' if g.sink_type == 1 else 'N', g.sink_num % (NUM_ACTIONS if g.sink_type==1 else MAX_NEURONS))
        
        if start_key in node_positions and end_key in node_positions:
            start_pos = node_positions[start_key]
            end_pos = node_positions[end_key]
            
            is_highlighted = (hovered_node is None) or (hovered_node == start_key) or (hovered_node == end_key)
            
            if is_highlighted:
                width = max(2, int(abs(g.weight)) + (2 if hovered_node else 0))
                color = (50, 200, 255) if g.weight > 0 else (255, 50, 50)
            else:
                width = 1
                color = (40, 40, 60)
            
            pygame.draw.line(screen, color, start_pos, end_pos, width)

    # 4. Draw Nodes
    for key, pos in node_positions.items():
        type, idx = key
        is_hover = hovered_node == key
        
        if type == 'S':
            col = (100, 255, 100) if is_hover else (0, 200, 0)
            pygame.draw.circle(screen, col, pos, node_radius + (2 if is_hover else 0))
            name = SENSOR_NAMES.get(idx, str(idx))
            lbl = font.render(name, True, (150, 255, 150) if (hovered_node is None or is_hover) else (60, 100, 60))
            screen.blit(lbl, lbl.get_rect(midright=(pos[0]-10, pos[1])))
            
        elif type == 'A':
            col = (255, 100, 100) if is_hover else (200, 0, 0)
            pygame.draw.circle(screen, col, pos, node_radius + (2 if is_hover else 0))
            name = ACTION_NAMES.get(idx, str(idx))
            lbl = font.render(name, True, (255, 150, 150) if (hovered_node is None or is_hover) else (100, 60, 60))
            screen.blit(lbl, lbl.get_rect(midleft=(pos[0]+10, pos[1])))
            
        elif type == 'N':
            c_val = int((agent.neurons[idx] + 1) * 127)
            pygame.draw.circle(screen, (c_val, c_val, c_val), pos, node_radius + (2 if is_hover else 0))
            pygame.draw.circle(screen, (255, 255, 255) if is_hover else (100, 100, 100), pos, node_radius + (2 if is_hover else 0), 1)