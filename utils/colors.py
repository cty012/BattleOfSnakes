import utils.functions as utils


def rgb(r, g, b):
    return r, g, b


white = rgb(255, 255, 255)

p_red = rgb(255, 0, 0)
p_blue = rgb(0, 0, 255)
p_green = rgb(0, 128, 0)
p_yellow = rgb(200, 150, 0)
p_cyan = rgb(0, 160, 160)
p_magenta = rgb(180, 35, 255)
p_brown = rgb(128, 80, 0)
p_lavender = rgb(190, 160, 220)


def get_player_colors():
    return [p_red, p_blue, p_green, p_yellow]


def add(color, num):
    return rgb(*[utils.min_max(c + num, 0, 255) for c in color])


def multiply(color, num):
    return rgb(*[utils.min_max(c * num, 0, 255) for c in color])
