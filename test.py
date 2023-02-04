from machine import Pin, SPI, mem32
import time
from uctypes import addressof
import array
import _thread

# set the time
from ntp import set_time

set_time()


@micropython.viper
def byteswap(a: uint) -> uint:
    return (
        ((uint(0xFF000000) & a) >> 24)
        | ((uint(0x00FF0000) & a) >> 8)
        | ((uint(0x0000FF00) & a) << 8)
        | ((uint(0x000000FF) & a) << 24)
    )


# 8 rows of 4 bytes
pixels = array.array("I", [0, 0, 0, 0, 0, 0, 0, 0])
addr = addressof(pixels)


def display(pixels):
    """Display pixel on screen"""

    # this seems to need to be set _low_ to enable or high to disable
    oe = Pin(13, Pin.OUT)
    oe.off()

    # columns controlled over SPI
    spi = SPI(1, 2_000_000, sck=Pin(10), mosi=Pin(11))

    # row control pins
    rows = [Pin(j, Pin.OUT) for j in (16, 18, 22)]

    # write from shift register to output - pulse to high
    en = Pin(12, Pin.OUT)

    while True:
        for j in range(8):
            for k in range(3):
                rows[k].value(j & (1 << k))
            oe.on()
            spi.write(pixels[j : j + 1])

            en.on()
            en.off()
            oe.off()
            time.sleep(0.002)


_thread.start_new_thread(display, (pixels,))


font = {
    0: (14, 17, 19, 21, 25, 17, 14),
    1: (4, 12, 4, 4, 4, 4, 14),
    2: (14, 17, 1, 2, 4, 8, 31),
    3: (31, 2, 4, 2, 1, 17, 14),
    4: (2, 6, 10, 18, 31, 2, 2),
    5: (31, 16, 30, 1, 1, 17, 14),
    6: (6, 8, 16, 30, 17, 17, 14),
    7: (31, 1, 2, 4, 8, 8, 8),
    8: (14, 17, 17, 14, 17, 17, 14),
    9: (14, 17, 17, 15, 1, 2, 12),
}


def render(number, s):
    digits = list(map(int, reversed(str(number))))

    if s % 2 == 0:
        bip = 1 << 11
    else:
        bip = 0

    for r in range(7):
        row = 0
        for j, d in enumerate(digits):
            row = row | (font[d][r] << (6 * j))
        if r in (3, 5):
            row |= bip
        pixels[r + 1] = byteswap(row << 8)


while True:
    t = time.localtime()
    now = 100 * t[3] + t[4]
    if now >= 1300:
        now -= 1200
    render(now, t[6])
    time.sleep(0.1)
