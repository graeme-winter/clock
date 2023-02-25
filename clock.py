import network
import socket
import time
import struct
import json
import urequests
import machine


def update_time():
    connect()
    offset = time_zone()
    set_time(offset)


def time_zone():
    response = urequests.get("http://worldtimeapi.org/api/timezone/Europe/London")
    offset = response.json()["utc_offset"]
    response.close()
    if offset == "+00:00":
        return 0
    # apply 3600s offset
    return 3600


def set_time(offset=0):
    NTP_DELTA = 2208988800
    host = "pool.ntp.org"
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()
    val = struct.unpack("!I", msg[40:44])[0]
    t = val - NTP_DELTA
    tm = time.gmtime(t + offset)
    machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6], tm[3], tm[4], tm[5], 0))


def connect(max_wait=10):
    from wifi import ssid, password

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        time.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError("network connection failed")

    return wlan.ifconfig()


