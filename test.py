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

            # pulse to lock
            en.on()
            en.off()

            # dim
            time.sleep_ms(1)

            # lights on
            oe.off()
            time.sleep_ms(1)


_thread.start_new_thread(display, (pixels,))


font = {
    0: 0x69BD996,
    1: 0x2622222,
    2: 0x691248F,
    3: 0x6912196,
    4: 0x359F111,
    5: 0xF886196,
    6: 0x698E996,
    7: 0xF112222,
    8: 0x6996996,
    9: 0x6997196,
}


def render(number):
    digits = list(map(int, reversed(str(number))))

    for r in range(7):
        row = 0
        for j, d in enumerate(digits):
            o = (0, 5, 12, 17)[j]
            row = row | ((font[d] >> (4 * (6 - r))) & 0xF) << o
        if r in (2, 4):
            row |= 1 << 10
        pixels[r + 1] = byteswap(row << 8)


while True:
    t = time.localtime()
    now = 100 * t[3] + t[4]
    render(now)
    time.sleep(0.1)
