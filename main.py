from machine import Pin, SPI
import ili9341
import time

print("Zagon ESP32-S3")

spi = SPI(
    1,
    baudrate=10000000,
    polarity=0,
    phase=0,
    sck=Pin(12),
    mosi=Pin(11),
    miso=Pin(13)
)

print("SPI OK")

display = ili9341.Display(
    spi,
    cs = Pin(10, Pin.OUT),
    dc = Pin(9, Pin.OUT),
    rst = Pin(8, Pin.OUT),
    width=320,
    height=240,
    rotation=90
)

print("ILI9341 OK")

display.fill(0xF800)
display.show()

print("Rdeča barva poslana")

time.sleep(1)

display.fill(0x07E0)
display.show()

print("Zelena barva poslana")

time.sleep(1)

display.fill(0x001F)
display.show()

print("Modra barva poslana")

while True:
    time.sleep(1)
