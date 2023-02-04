from machine import Pin, SPI, mem32
import time
from uctypes import addressof
import array
import _thread


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
    spi = SPI(1, 10_000_000, sck=Pin(10), mosi=Pin(11))

    # row control pins
    rows = [Pin(j, Pin.OUT) for j in (16, 18, 22)]

    # write from shift register to output - pulse to high
    en = Pin(12, Pin.OUT)

    while True:
        for j in range(8):
            for k in range(3):
                rows[k].value(j & (1 << k))
            spi.write(pixels[j : j + 1])

            en.on()
            en.off()
            oe.on()
            time.sleep(0.001)
            oe.off()
            time.sleep(0.001)


_thread.start_new_thread(display, (pixels,))


def write_cols(j, x):
    """Write bits from x to cols"""
    pixels[j] = byteswap(x)


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


def render(number):
    digits = list(map(int, reversed(str(number))))
    for r in range(7):
        row = 0
        for j, d in enumerate(digits):
            row = row | (font[d][r] << (6 * j))
        write_cols(r + 1, row << 8)


for value in range(1999):
    render(value)
    time.sleep(1)
