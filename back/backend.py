import back.scenes as s


class BackEnd:
    def __init__(self, args):
        self.args = args
        self.scene = None

    def prepare(self):
        self.scene = s.menu.Scene(self.args)

    def process_events(self, events):
        command = self.scene.process_events(events)
        if command[0] == 'menu':
            self.scene = s.menu.Scene(self.args)
        elif command[0] == 'mode':
            self.scene = s.mode.Scene(self.args)
        elif command[0] == 'room_server':
            self.scene = s.room_server.Scene(self.args)
        elif command[0] == 'game':
            self.scene = s.game.Scene(self.args, command[1], command[2], command[3])
        else:
            return command[0]

    def show(self, ui):
        self.scene.show(ui)

    def quit(self):
        self.scene = None
