import platform

# https://stackoverflow.com/a/29643643
def hex_to_rgb(h):
    return tuple(int(h[1:][i:i+2], 16) for i in (0, 2, 4))

# https://stackoverflow.com/a/57338561
def interpolate(color_a, color_b, t):
    # 'color_a' and 'color_b' are RGB tuples
    # 't' is a value between 0.0 and 1.0
    # this is a naive interpolation
    list = []
    for a, b in zip(color_a, color_b):
        i = int(a + (b - a) * t)
        if i < 0:
            i = 0
        elif i > 255:
            i = 255
        list.append(i)
    return tuple(list)
    # return tuple( int(a + (b - a) * t) for a, b in zip(color_a, color_b))

# reference: https://docs.python.org/3/library/platform.html#module-platform
def get_os_type():
    os_type = platform.system()
    if os_type == 'Windows':
        return 'windows'
    elif os_type == 'Darwin':
        return 'mac'
    elif os_type == 'Linux':
        return 'linux'
