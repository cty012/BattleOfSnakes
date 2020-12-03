import back.sprites.modules.map as m
import back.sprites.modules.player as p
import utils.stopwatch as sw


class Game:
    def __init__(self, args, id, threshold=1):
        self.args = args
        self.id = id
        self.threshold = threshold
        self.map = m.Map(self.args, self.args.get_pos(1, 1), align=(1, 1))
        self.players = [p.Player(self.args, self.id, (255, 0, 0))]
        self.map.generate_apples(self.players)
        self.map.focus_board(self.players[self.id].head())
        self.status = {'running': True}

        # timer
        self.timer = sw.Stopwatch()
        self.timer.start()

    def process_events(self, events):
        self.map.process_events(events)

        # check if game has already ended
        if not self.status['running']:
            return [None]

        if self.timer.get_time() > 0.25:
            # reset timer
            self.timer.clear()
            self.timer.start()

            # check if game ends
            self.check_alive()
            if len(self.survivors()) <= self.threshold:
                print('Game ends')
                self.status['running'] = False
                return ['end']

            # move surviving players and eat apples
            for player in self.survivors():
                player.move()
                remove_list = []
                for apple in self.map.apples:
                    if apple.grid in player.grids:
                        player.energy += 1
                        remove_list.append(apple)
                for apple in remove_list:
                    self.map.apples.remove(apple)

            # refill apples
            self.map.generate_apples(self.survivors())

        # control the player
        if self.players[self.id].alive:
            self.players[self.id].process_events(events)
        return [None]

    def survivors(self):
        return [player for player in self.players if player.alive]

    def is_valid_grid(self, grid):
        if not self.map.in_range_grid(grid):
            return False
        for player in self.survivors():
            if grid in player.grids[1:]:
                return False
        return True

    def check_alive(self):
        new_heads, losers = {}, []
        for player in self.survivors():
            target = player.get_target()
            if not self.is_valid_grid(target):
                losers.append(player)
                continue
            if target in new_heads:
                losers.append(player)
                if new_heads[target] not in losers:
                    losers.append(new_heads[target])
                continue
            new_heads[target] = player
        for loser in losers:
            loser.alive = False

    def show(self, ui):
        self.map.show(ui)
        for player in self.survivors():
            self.map.show_player(ui, player)
