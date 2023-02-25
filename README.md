# Green Clock (Python)

[Waveshare green clock kit](https://www.waveshare.com/pico-clock-green.htm) - need to be able to make use of the real time clock mmodule, display, peripherals. First start with clock.

## Plan 0

Get the clock displaying time, with time taken from NTP with timezone derived from world time zone database:

```bash
curl http://worldtimeapi.org/api/timezone/Europe/London
```

which will return many things including the `utc_offset` - which is needed to map from NTP time that the RTC will be on to local time which is what the display will show (so do, or do not, add 1 hour).

## Hardware for Plan 0

### RTC

[DS3231 RTC module](https://www.waveshare.com/w/upload/9/9b/DS3231.pdf) accessed over i2c.

### LED drivers

Implemented through a couple of chips to control lights + 8 x 24 matrix. Could use µPython framebuffer for that? Would give some stuff free. OK, looks like there are two (three) chips involved in driving the LED matrix: one 3 bit -> 8 demultiplexer on + and 2 x 16-way controlled by SPI on -, where the first does columns 0...15 and the second does the last 8. Brightness therefore will need to be manually controlled etc. -> 🤔 much.

Wiring:

- rows[0] -> GPIO16
- rows[1] -> GPIO18
- rows[2] -> GPIO20

i.e. to get row 5 lit set GPIO16 and 20 to high, I assume.

SPI connections on GPIO10-13 (CLK, TX, RX, enable). Implementation I am looking at here appears to do this by bit bashing? In µPython? Not using hardware SPI. Or is this some plain UART serial? Data sheet time.

## 2023-02-25 System Design

### Display

Two key methods: set up display, main display routine which is writen in Thumb assembly.

Set up:

- configure the GPIO pins which will be used
- configure the SPI to the display controller

Execute:

- main routine taking the pointer to the data area, which will hold the pixel data, which will run on a 200 Hz update cycle

### Update

This will:

- configure the wifi, abort if failed
- fetch the current UTC from NTP server
- fetch the current offset from UTC from t'nternet
- apply this to the current system time

Update will be triggered on (i) boot (ii) trigger from the middle button

### IRQ handlers

Buttons require IRQ handlers:

- button top -> brighter (increment time on, decrement time off)
- button bottom -> dimmer (reverse above)
- middle - trigger update as above

### Main routine

Will sit in a tight loop doing:

- read current time
- render current time to scratch array
- byte swap scratch array
- copy scratch array to main
