import re
import threading


# return the top-left corner of the rectangle
def top_left(pos, size, *, align=(0, 0)):
    return pos[0] - align[0] * (size[0] // 2), pos[1] - align[1] * (size[1] // 2)


def is_rect(rect):
    return rect[0][0] < rect[1][0] and rect[0][1] < rect[1][1]


def add(*rects):
    return tuple([sum([i[0] for i in rects]), sum([i[1] for i in rects])])


def negative(rect):
    return tuple([-i for i in rect])


def min_max(val, min_val, max_val):
    return min(max(val, min_val), max_val)


def is_ip(ip):
    regex = r'(([1-9]?[0-9])|(1[0-9][0-9])|(2[0-4][0-9])|(25[0-5]))'
    return re.match(r'^(' + regex + r'\.){3}' + regex + r'$', ip)


def is_private_ip(ip):
    if not is_ip(ip):
        return False
    return ip.startswith('10.') or ip.startswith('192.168.') or re.match(r'^172\.((1[6-9])|(2[0-9])|(3[0-1]))\.', ip)


def to_str_time(hundredth_secs, *, connect=(':', ':')):
    minutes = hundredth_secs // 6000
    seconds = (hundredth_secs % 6000) // 100
    decimals = hundredth_secs % 100
    return f'{minutes:02}{connect[0]}{seconds:02}{connect[1]}{decimals:02}'


def synchronized(func):
    func.__lock__ = threading.Lock()

    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func


def get_init_grids(map_size):
    return [
        [(1, i) for i in range(1, 4)],
        [(map_size[0] - 2, map_size[1] - i - 1) for i in range(1, 4)],
        [(map_size[0] - i - 1, 1) for i in range(1, 4)],
        [(i, map_size[1] - 2) for i in range(1, 4)]
    ]
