import json

import back.sprites.component as c
from network.discovery import DiscoveryBeacon
import utils.fonts as f
import utils.functions as utils
import utils.stopwatch as sw


class Scene:
    def __init__(self, args):
        self.args = args
        self.background = c.Component(lambda ui: ui.show_div((0, 0), self.args.size, color=(60, 179, 113)))
        self.btn_slots = [
            (self.args.size[0] // 2, 150),
            (self.args.size[0] // 2, 270),
            (self.args.size[0] // 2, 390),
            (self.args.size[0] // 2, 510)
        ]
        self.beacon = DiscoveryBeacon('224.0.3.101', list(range(5000, 5100)), b'battleofsnakes')
        self.beacon.start()
        self.rooms = []
        self.buttons = {
            'back': c.Button(
                (self.args.size[0] // 2, 650), (400, 60), 'Back', font=f.tnr(25),
                save='tnr-25', align=(1, 1), background=(210, 210, 210)),
        }
        self.refresh()
        self.timer = sw.Stopwatch()
        self.timer.start()

    def process_events(self, events):
        if self.timer.get_time() > 0.1:
            self.timer.clear()
            self.timer.start()
            self.refresh()
        if events['mouse-left'] == 'down':
            for name in self.buttons:
                if self.buttons[name].in_range(events['mouse-pos']):
                    return self.execute([name])
            for room in self.rooms:
                if room.in_range(events['mouse-pos']):
                    return self.execute(room.process_events(events))
        return [None]

    def execute(self, command):
        if command[0] == 'join':
            self.beacon.stop(cb=lambda a, b: print(f'BEACON ENDS: scene=join'))
            return ['room', command[1].name, (command[1].ip, command[1].port), None]
        elif command[0] == 'back':
            self.beacon.stop(cb=lambda a, b: print(f'BEACON ENDS: scene=join'))
            return ['menu']
        return [None]

    def refresh(self):
        self.rooms = []
        for i, ((ip, _), info_b) in enumerate(self.beacon.responses.items()):
            pos = self.btn_slots[i % len(self.btn_slots)]
            info = json.loads(info_b.decode('utf-8'))
            self.rooms.append(Room(self.args, pos, (ip, info['port']), info['name'], align=(1, 1)))
        self.beacon.ping(True)

    def show(self, ui):
        self.background.show(ui)
        for room in self.rooms:
            room.show(ui)
        for name in self.buttons:
            self.buttons[name].show(ui)


class Room:
    def __init__(self, args, pos, address, name, *, align=(0, 0)):
        self.args = args
        self.size = [600, 100]
        self.pos = utils.top_left(pos, self.size, align=align)
        self.ip = address[0]
        self.port = address[1]
        self.name = name
        self.join_btn = c.Button(utils.add(self.pos, (550, 50)), (80, 60), 'Join', font=f.tnr(20), border=1, align=(1, 1))

    def process_events(self, events):
        if events['mouse-left'] == 'down':
            if self.join_btn.in_range(events['mouse-pos']):
                return ['join', self]
        return [None]

    def in_range(self, pos, *, pan=(0, 0)):
        return self.pos[0] + pan[0] < pos[0] < self.pos[0] + self.size[0] + pan[0] and \
               self.pos[1] + pan[1] < pos[1] < self.pos[1] + self.size[1] + pan[1]

    def show(self, ui, *, pan=(0, 0)):
        # show background
        ui.show_div(self.pos, self.size, color=(210, 210, 210), pan=pan)
        ui.show_div(self.pos, self.size, border=1, pan=pan)

        # show text
        ui.show_text(utils.add(self.pos, (50, 30)), self.name, f.cambria(25), pan=pan, align=(0, 1))
        ui.show_text(utils.add(self.pos, (50, 80)), self.ip, f.cambria(15), pan=pan, align=(0, 1))
        ui.show_text(utils.add(self.pos, (150, 80)), str(self.port), f.cambria(15), pan=pan, align=(0, 1))

        # show button
        self.join_btn.show(ui, pan=pan)
