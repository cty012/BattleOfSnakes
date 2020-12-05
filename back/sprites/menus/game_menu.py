import back.sprites.component as c
import utils.fonts as f
import utils.functions as utils


class GameMenu:
    def __init__(self, args, pos, size=(300, 240), choices=('continue', 'quit'), *, align=(0, 0)):
        self.args = args
        self.size = size
        self.pos = utils.top_left(pos, self.size, align=align)
        self.buttons = {
            name: c.Button(
                (self.pos[0] + self.size[0] // 2, self.pos[1] + pos), (200, 40), name,
                font=f.tnr(22), border=1, align=(1, 0), background=(230, 230, 230)
                ) for name, pos in zip(choices, range(100, 100 + 60 * len(choices), 60))}
        self.active = False

    def process_events(self, events):
        if not self.active:
            return [None]
        if events['mouse-left'] == 'down':
            for name in self.buttons:
                if self.buttons[name].in_range(events['mouse-pos']):
                    return self.execute(name)
        if 'escape' in events['key-down']:
            return self.execute('continue')
        return [None]

    def execute(self, name):
        if name == 'continue':
            return ['pause']
        elif name == 'quit':
            return ['close']
        return [None]

    def show(self, ui, *, win=None, pan=(0, 0)):
        pos = self.pos[0] + pan[0], self.pos[1] + pan[1]
        # container
        if win is None:
            color, text = (192, 192, 192), 'OPTIONS'
        elif win:
            color, text = (255, 204, 204), 'YOU WIN'
        else:
            color, text = (204, 204, 255), 'YOU LOSE'
        ui.show_div(pos, self.size, color=color)
        ui.show_div(pos, self.size, border=1)
        # msg
        ui.show_text((self.size[0] // 2, 40), text, f.cambria(28), align=(1, 0), pan=pos)
        # buttons
        for name in self.buttons:
            self.buttons[name].show(ui)
