# Minimal ILI9341 driver for MicroPython + Wokwi
# Uses a 320x240 RGB565 framebuffer.

from machine import Pin
import framebuf
import time

class Display:
    def __init__(self, spi, cs, dc, rst, width=320, height=240, rotation=90):
        self.spi = spi
        self.cs = cs if isinstance(cs, Pin) else Pin(cs, Pin.OUT)
        self.dc = dc if isinstance(dc, Pin) else Pin(dc, Pin.OUT)
        self.rst = rst if isinstance(rst, Pin) else Pin(rst, Pin.OUT)
        self.width = width
        self.height = height

        self.cs.value(1)
        self.dc.value(1)
        self.rst.value(1)
        self.rst.value(0)
        time.sleep_ms(50)
        self.rst.value(1)
        time.sleep_ms(120)

        self._init_display(rotation)

        # Framebuffer is little-endian in MicroPython; bytes are swapped in show().
        self.buffer = bytearray(self.width * self.height * 2)
        self.fb = framebuf.FrameBuffer(
            self.buffer, self.width, self.height, framebuf.RGB565
        )
        self.fb.fill(0x0000)
        self.show()

    def _cmd(self, command, data=None):
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytes([command]))
        if data is not None:
            self.dc.value(1)
            self.spi.write(data)
        self.cs.value(1)

    def _init_display(self, rotation):
        self._cmd(0x01)  # Software reset
        time.sleep_ms(150)
        self._cmd(0x28)  # Display off
        self._cmd(0xCF, bytes([0x00, 0x83, 0x30]))
        self._cmd(0xED, bytes([0x64, 0x03, 0x12, 0x81]))
        self._cmd(0xE8, bytes([0x85, 0x01, 0x79]))
        self._cmd(0xCB, bytes([0x39, 0x2C, 0x00, 0x34, 0x02]))
        self._cmd(0xF7, bytes([0x20]))
        self._cmd(0xEA, bytes([0x00, 0x00]))
        self._cmd(0xC0, bytes([0x26]))
        self._cmd(0xC1, bytes([0x11]))
        self._cmd(0xC5, bytes([0x35, 0x3E]))
        self._cmd(0xC7, bytes([0xBE]))
        self._cmd(0x36, bytes([0x28 if rotation == 90 else 0x48]))
        self._cmd(0x3A, bytes([0x55]))  # 16-bit RGB565
        self._cmd(0xB1, bytes([0x00, 0x1B]))
        self._cmd(0xB6, bytes([0x08, 0x82, 0x27]))
        self._cmd(0xF2, bytes([0x00]))
        self._cmd(0x26, bytes([0x01]))
        self._cmd(0xE0, bytes([
            0x0F, 0x31, 0x2B, 0x0C, 0x0E, 0x08, 0x4E, 0xF1,
            0x37, 0x07, 0x10, 0x03, 0x0E, 0x09, 0x00
        ]))
        self._cmd(0xE1, bytes([
            0x00, 0x0E, 0x14, 0x03, 0x11, 0x07, 0x31, 0xC1,
            0x48, 0x08, 0x0F, 0x0C, 0x31, 0x36, 0x0F
        ]))
        self._cmd(0x11)  # Sleep out
        time.sleep_ms(120)
        self._cmd(0x29)  # Display on
        time.sleep_ms(20)

    def _set_window(self, x0, y0, x1, y1):
        self._cmd(0x2A, bytes([
            (x0 >> 8) & 0xFF, x0 & 0xFF,
            (x1 >> 8) & 0xFF, x1 & 0xFF
        ]))
        self._cmd(0x2B, bytes([
            (y0 >> 8) & 0xFF, y0 & 0xFF,
            (y1 >> 8) & 0xFF, y1 & 0xFF
        ]))
        self._cmd(0x2C)

    def show(self):
        self._set_window(0, 0, self.width - 1, self.height - 1)

        out = bytearray(len(self.buffer))

        for i in range(0, len(self.buffer), 2):
            out[i] = self.buffer[i + 1]
            out[i + 1] = self.buffer[i]

        self.cs.value(0)
        self.dc.value(1)
        self.spi.write(out)
        self.cs.value(1)

    def fill(self, color):
        self.fb.fill(color)

    def pixel(self, x, y, color):
        self.fb.pixel(x, y, color)

    def text(self, string, x, y, color=0xFFFF):
        self.fb.text(string, x, y, color)

    def rect(self, x, y, w, h, color):
        self.fb.rect(x, y, w, h, color)

    def fill_rect(self, x, y, w, h, color):
        self.fb.fill_rect(x, y, w, h, color)

    def line(self, x1, y1, x2, y2, color):
        self.fb.line(x1, y1, x2, y2, color)
