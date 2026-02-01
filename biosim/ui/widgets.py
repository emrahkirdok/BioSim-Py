import pygame

# Colors (Duplicated here or imported? Let's assume standard colors)
COLOR_TEXT = (220, 220, 220)
COLOR_UI_BG = (60, 60, 70)
COLOR_UI_ACTIVE = (100, 100, 150)
COLOR_UI_SELECTED = (100, 200, 100)

class Button:
    def __init__(self, x, y, w, h, text, callback, toggled=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.hovered = False
        self.toggled = toggled

    def draw(self, screen, font):
        color = COLOR_UI_SELECTED if self.toggled else (COLOR_UI_ACTIVE if self.hovered else COLOR_UI_BG)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 1)
        
        text_surf = font.render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and event.button == 1:
                self.callback()

class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial, label, callback, int_mode=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial
        self.label = label
        self.callback = callback # Function to call on update
        self.int_mode = int_mode
        self.dragging = False

    def draw(self, screen, font):
        val_str = f"{self.label}: {int(self.value) if self.int_mode else f'{self.value:.3f}'}"
        text_surf = font.render(val_str, True, COLOR_TEXT)
        screen.blit(text_surf, (self.rect.x, self.rect.y - 18))
        
        pygame.draw.rect(screen, (100, 100, 100), self.rect)
        
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        knob_x = self.rect.x + (ratio * self.rect.width)
        knob_rect = pygame.Rect(knob_x - 5, self.rect.y - 5, 10, self.rect.height + 10)
        pygame.draw.rect(screen, COLOR_UI_ACTIVE, knob_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.update_value(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.update_value(event.pos[0])

    def update_value(self, mouse_x):
        rel_x = mouse_x - self.rect.x
        ratio = max(0.0, min(1.0, rel_x / self.rect.width))
        val = self.min_val + (ratio * (self.max_val - self.min_val))
        if self.int_mode: val = int(round(val))
        self.value = val
        if self.callback:
            self.callback(self.value)
