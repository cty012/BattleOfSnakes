import pygame

import front.event as e
import front.ui as u


class FrontEnd:
    def __init__(self, args):
        self.args = args
        self.window = None
        self.screen = None
        self.event = None
        self.ui = None
        self.clock = None

    def prepare(self):
        pygame.init()
        self.window = pygame.display.set_mode(self.args.real_size)
        self.screen = pygame.Surface(self.args.size, flags=pygame.DOUBLEBUF)
        self.screen.set_alpha(None)
        self.event = e.Event(self.args)
        self.ui = u.UI(self.args, self.window, self.screen)
        pygame.display.set_caption(self.args.title)
        try:
            pygame.display.set_icon(self.ui.image.get('icon.png'))
        except:
            print(f'ERROR: cannot load resources\\imgs\\icon.png!')
        self.clock = pygame.time.Clock()

    # Event operation
    def get_events(self):
        return self.event.detect()

    # UI operation
    def render(self, component):
        self.ui.clear()
        component.show(self.ui)
        self.ui.update()

    def quit(self):
        pygame.display.quit()
        pygame.quit()
