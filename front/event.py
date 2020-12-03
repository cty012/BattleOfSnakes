import pygame
from pygame.locals import *


class Event:
    def __init__(self, args):
        self.args = args
        self.key_list = \
            [k for k in range(K_0, K_9 + 1)] + [k for k in range(K_a, K_z + 1)] + [k for k in range(K_F1, K_F12 + 1)] + \
            [K_SPACE, K_TAB, K_ESCAPE, K_BACKSPACE, K_RETURN, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_PAGEUP, K_PAGEDOWN, K_DELETE] + \
            [K_MINUS, K_EQUALS, K_LEFTBRACKET, K_RIGHTBRACKET, K_BACKSLASH, K_COLON, K_QUOTE, K_COMMA, K_PERIOD, K_BACKSLASH] + \
            [k for k in range(K_KP0, K_KP9 + 1)] + [K_KP_PLUS, K_KP_MINUS]

    def detect(self):
        pos = pygame.mouse.get_pos()
        all_events = {
            'quit': False,
            'mouse-left': 'hover',
            'mouse-middle': 'hover',
            'mouse-right': 'hover',
            'mouse-wheel': 'static',
            'mouse-pos': (pos[0] / self.args.scale, pos[1] / self.args.scale),
            'key-down': [],
            'key-up': [],
            'key-pressed': None,
            'mods': pygame.key.get_mods()
        }
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                all_events['quit'] = True
            elif event.type == pygame.KEYDOWN:
                all_events['key-down'].append(pygame.key.name(event.key))
            elif event.type == pygame.KEYUP:
                all_events['key-up'].append(pygame.key.name(event.key))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    all_events['mouse-left'] = 'down'
                elif event.button == 2:
                    all_events['mouse-middle'] = 'down'
                elif event.button == 3:
                    all_events['mouse-right'] = 'down'
                elif event.button == 4:
                    all_events['mouse-wheel'] = 'up'
                elif event.button == 5:
                    all_events['mouse-wheel'] = 'down'
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    all_events['mouse-left'] = 'up'
        # add pressed keys
        pressed = pygame.key.get_pressed()
        all_events['key-pressed'] = [pygame.key.name(key) for key in self.key_list if pressed[key]]
        return all_events
