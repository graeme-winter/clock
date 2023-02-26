from machine import Pin, SPI, mem32
import _thread
import array
import time

# 8 rows of 4 bytes + 2 x on / off time
pixels = array.array("I", [0, 0, 0, 0, 0, 0, 0, 0, 1000, 1000])


# set the time
from update_time import update_time

do_update_time = False


def button_middle(args):
    global do_update_time
    do_update_time = True


def button_top(args):
    global pixels
    if pixels[9] <= 100:
        return
    pixels[8] += 100
    pixels[9] -= 100


def button_bottom(args):
    global pixels
    if pixels[8] <= 100:
        return
    pixels[8] -= 100
    pixels[9] += 100


top = Pin(15, Pin.IN, Pin.PULL_UP)
top.irq(button_top, Pin.IRQ_RISING)

middle = Pin(17, Pin.IN, Pin.PULL_UP)
middle.irq(button_middle, Pin.IRQ_RISING)

bottom = Pin(2, Pin.IN, Pin.PULL_UP)
bottom.irq(button_bottom, Pin.IRQ_RISING)


def prepare_display():
    """Set up the display"""

    # this seems to need to be set _low_ to enable or high to disable
    oe = Pin(13, Pin.OUT)
    oe.off()

    # columns controlled over SPI
    spi = SPI(1, 2_000_000, sck=Pin(10), mosi=Pin(11))

    # row control pins
    rows = [Pin(j, Pin.OUT) for j in (16, 18, 22)]

    # write from shift register to output - pulse to high
    en = Pin(12, Pin.OUT)
    en.off()

    # on entry all row pins are 0 -> set to 1 so that the loops work correctly
    for r in rows:
        r.on()


def display(pixels):
    """Display pixel on screen"""

    from asm_helpers import gpio_xor, write_spi

    a = 1 << 16
    b = 1 << 18
    c = 1 << 22
    steps = array.array("I", [a | b | c, a, a | b, a, a | b | c, a, a | b, a])

    EN = 1 << 12
    OE = 1 << 13

    while True:
        for j in range(8):
            gpio_xor(OE)
            gpio_xor(steps[j])
            write_spi(pixels[j])
            gpio_xor(EN)
            gpio_xor(EN)

            # dim
            time.sleep_us(pixels[8])

            # lights on
            gpio_xor(OE)
            time.sleep_us(pixels[9])


prepare_display()
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


def byteswap(a):
    return (
        ((0xFF000000 & a) >> 24)
        | ((0x00FF0000 & a) >> 8)
        | ((0x0000FF00 & a) << 8)
        | ((0x000000FF & a) << 24)
    )


def render(number):
    digits = list(map(int, reversed(f"{number:04d}")))

    for r in range(7):
        row = 0
        for j, d in enumerate(digits):
            o = (0, 5, 12, 17)[j]
            row = row | ((font[d] >> (4 * (6 - r))) & 0xF) << o
        if r in (2, 4):
            row |= 1 << 10
        pixels[r + 1] = byteswap(row << 8)


while True:

    if do_update_time:
        update_time()
        do_update_time = False

    t = time.localtime()
    now = 100 * t[3] + t[4]
    render(now)
    time.sleep(0.1)
