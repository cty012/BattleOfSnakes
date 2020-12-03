import os
import pygame


class Image:
    def __init__(self, args, imgs=()):
        self.args = args
        self.root = os.path.join(self.args.path, 'resources', 'imgs')
        self.imgs = {name: self.load(name) for name in imgs}

    def load(self, path):
        return pygame.image.load(os.path.join(self.root, path))

    def add(self, img):
        self.imgs[img] = self.load(img)

    def get(self, img):
        ans = self.imgs.get(img)
        if ans is None:
            self.add(img)
            ans = self.imgs.get(img)
        return ans
