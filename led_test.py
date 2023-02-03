from machine import Pin, ADC, SPI
import time

sensor = ADC(26)

# row power N.B. does not appear to have the enable line set
# so cannot use nifty PWM type mechanism to control brightness
rows = [Pin(j, Pin.OUT) for j in (16, 18, 22)]

# columns controlled over SPI
spi = SPI(1, 10_000_000, sck=Pin(10), mosi=Pin(11))

# write from shift register to output - pulse to high
en = Pin(12, Pin.OUT)

# this seems to need to be set _low_ to enable or high to disable
oe = Pin(13, Pin.OUT)

cols = bytearray(4)


def write_cols(x):
    """Write bits from x to cols"""
    for j in range(4):
        shift = 8 * (3 - j)
        cols[j] = (x & (0xFF << shift)) >> shift
    spi.write(cols)

    en.on()
    en.off()


oe.off()

while True:
    for j in range(1, 8):
        for k in range(3):
            rows[k].value(j & (1 << k))
        for j in range(22):
            x = 1 << (29 - j)
            write_cols(x)
            time.sleep(0.1)
