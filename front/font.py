import os
import pygame


class Font:
    def __init__(self, args):
        self.args = args
        self.root = os.path.join(self.args.path, 'resources', 'fonts')
        self.text_imgs = {}

    def render_font(self, font):
        if font[0] == 'ttf':
            return pygame.font.Font(font[1], font[2])
        elif font[0] == 'src':
            return pygame.font.Font(self.get(font[1]), font[2])
        elif font[0] == 'sys':
            return pygame.font.SysFont(font[1], font[2])

    def get(self, file):
        return os.path.join(self.root, file)

    def load(self, save, msg):
        if save in self.text_imgs.keys() and msg in self.text_imgs[save].keys():
            return self.text_imgs[save][msg]
        return None

    def save(self, save, msg, img):
        if save not in self.text_imgs.keys():
            self.text_imgs[save] = {}
        self.text_imgs[save][msg] = img
