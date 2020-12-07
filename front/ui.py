import pygame

import front.font as f
import front.image as i
import utils.functions as utils


class StupidStub:
    def get_size(self, *a, **kw):
        pass  # Does nothing

    def blit(self, *a, **kw):
        pass  # Does nothing


stupid_stub = StupidStub()


class UI:
    def __init__(self, args, window, screen):
        self.args = args
        self.window = window
        self.screen = screen
        self.size = self.screen.get_size()
        self.font = f.Font(self.args)
        self.image = i.Image(self.args)

    @classmethod
    def new(cls, args, size):
        surface = pygame.Surface(size)
        return cls(args, stupid_stub, surface)

    def clear(self):
        self.screen.fill((255, 255, 255))

    def toggle_fullscreen(self):
        pygame.display.toggle_fullscreen()

    def update(self):
        frame = pygame.transform.scale(self.screen, self.window.get_size())
        self.window.blit(frame, frame.get_rect())
        pygame.display.update()

    def show_line(self, start, end, *, width=1, color=(0, 0, 0), pan=(0, 0)):
        start = utils.add(start, pan)
        end = utils.add(end, pan)
        pygame.draw.line(self.screen, color, start, end, width)

    def show_triangle(self, pos, radius, direction, *, border=0, color=(0, 0, 0), pan=(0, 0)):
        pos = utils.add(pos, pan)
        if direction == 'left':
            points = ((pos[0] - radius, pos[1]), (pos[0] + radius, pos[1] - 2 * radius), (pos[0] + radius, pos[1] + 2 * radius))
        else:
            points = ((pos[0] + radius, pos[1]), (pos[0] - radius, pos[1] - 2 * radius), (pos[0] - radius, pos[1] + 2 * radius))
        pygame.draw.polygon(self.screen, color, points, border)

    def show_div(self, pos, size, *, border=0, color=(0, 0, 0), align=(0, 0), pan=(0, 0)):
        # align: 0 left/top, 1 center, 2 right/bottom
        pos = utils.add(pos, pan)
        rect = [utils.top_left(pos, size, align=align), size]
        pygame.draw.rect(self.screen, color, rect, border)

    def show_circle(self, pos, radius, *, border=0, color=(0, 0, 0), align=(1, 1), pan=(0, 0)):
        pos = utils.add(utils.top_left(pos, (radius * 2, radius * 2), align=align), (radius, radius), pan)
        pygame.draw.circle(self.screen, color, pos, radius, border)

    def show_text(self, pos, text, font, *, color=(0, 0, 0), background=None, save=None, align=(0, 0), pan=(0, 0)):
        if text == '':
            return

        if save is None:
            pos = utils.add(pos, pan)
            text_img = self.font.render_font(font).render(text, True, color, background)
            size = text_img.get_size()
            self.screen.blit(text_img, utils.top_left(pos, size, align=align))
            return

        text_imgs = []
        for char in text:
            char_img = self.font.load(save, char)
            if char_img is None:
                char_img = self.font.render_font(font).render(char, True, color, background)
                self.font.save(save, char, char_img)
            text_imgs.append(char_img)
        total_size = sum([text_img.get_size()[0] for text_img in text_imgs]), \
               max([text_img.get_size()[1] for text_img in text_imgs])
        pos = utils.top_left(pos, total_size, align=align)
        x, y = pos[0], pos[1] + total_size[1] // 2
        for text_img in text_imgs:
            self.show_img((x, y), text_img, align=(0, 1), pan=pan)
            x += text_img.get_size()[0]

    def show_texts(self, pos, texts, font, *, align=(0, 0), pan=(0, 0)):
        pos = utils.add(pos, pan)
        text_font = self.font.render_font(font)
        # evaluate total size
        total_size = (0, 0)
        for text in texts:
            size = text_font.size(text[0])
            total_size = (total_size[0] + size[0], size[1])
        # draw text
        pos, x = utils.top_left(pos, total_size, align=align), 0
        for text in texts:
            text_img = text_font.render(text[0], True, text[1])
            self.screen.blit(text_img, (pos[0] + x, pos[1]))
            x += text_img.get_size()[0]

    def show_img(self, pos, img, *, align=(0, 0), pan=(0, 0)):
        pos = utils.add(pos, pan)
        size = img.get_size()
        self.screen.blit(img, utils.top_left(pos, size, align=align))

    def show_img_by_path(self, pos, path, *, align=(0, 0), pan=(0, 0)):
        img = self.image.get(path)
        self.show_img(pos, img, align=align, pan=pan)

    def show_ui(self, pos, ui, *, pan=(0, 0), align=(0, 0)):
        pos = utils.top_left(utils.add(pos, pan), ui.size, align=align)
        self.screen.blit(ui.screen, pos)
