import array

# 8 rows of 4 bytes
pixels = array.array("I", [0, 0, 0, 0, 0, 0, 0, 0])


def display(pixels):
    for j in range(8):
        print(("{0:032b}".format(pixels[j])).replace("0", " ").replace("1", "■"))


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
        pixels[r + 1] = row
    display(pixels)


for now in 1234, 2356, 908:
    render(now)
