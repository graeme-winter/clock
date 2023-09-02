@micropython.asm_thumb
def gpio_xor(r0):
    push({r7})
    align(4)
    mov(r7, pc)
    b(xor)
    align(4)
    data(4, 0xD000001C)
    align(2)
    label(xor)
    ldr(r1, [r7, 0])
    str(r0, [r1, 0])
    pop({r7})


@micropython.asm_thumb
def write_spi(r0):
    push({r4, r5, r6, r7})
    align(4)
    mov(r7, pc)
    b(write)
    align(4)
    data(4, 0x40040000)
    align(2)
    label(write)
    mov(r3, 0x8)
    mov(r4, 0xFF)
    ldr(r1, [r7, 0])

    mov(r6, 4)
    label(out)
    strb(r0, [r1, 0x8])

    mov(r5, 0xFF)
    label(tick0)
    sub(r5, 1)
    cmp(r5, 0)
    bne(tick0)

    lsr(r0, r3)
    sub(r6, 1)
    cmp(r6, 0)
    bne(out)

    pop({r4, r5, r6, r7})
