import utils.fonts as f
import utils.functions as utils


# COMPONENT
class Component:
    def __init__(self, func):
        self.show = func


# BUTTON
class Button:
    def __init__(self, pos, size, text, *, font=f.tnr(25),
                 border=2, color=((0, 0, 0), (0, 0, 0)), save=None, align=(0, 0), background=None):
        self.pos = utils.top_left(pos, size, align=align)
        self.size = size
        self.text = text
        self.font = font
        self.border = border
        self.color = color
        self.save = save
        self.align = align
        self.background = background

    def in_range(self, pos):
        return self.pos[0] < pos[0] < self.pos[0] + self.size[0] and self.pos[1] < pos[1] < self.pos[1] + self.size[1]

    def show(self, ui, *, pan=(0, 0)):
        if self.background is not None:
            ui.show_div(self.pos, self.size, border=0, color=self.background, pan=pan)
        ui.show_div(self.pos, self.size, border=self.border, color=self.color[0], pan=pan)
        center = self.pos[0] + self.size[0] // 2, self.pos[1] + self.size[1] // 2
        if self.text != '':
            ui.show_text(center, self.text, self.font, color=self.color[1], save=self.save, align=(1, 1), pan=pan)
