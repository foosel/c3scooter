from aswitch import Pushbutton
from rotary_irq_esp import RotaryIRQ

from machine import Pin, SPI
from ssd1351 import Display, color565
from xglcd_font import XglcdFont

import uasyncio as asyncio

import time

PIN_DISPLAY_MOSI = 27
PIN_DISPLAY_CLK = 25
PIN_DISPLAY_CS = 32
PIN_DISPLAY_RST = 21
PIN_DISPLAY_DC = 17

PIN_KNOB_CLK = 18
PIN_KNOB_DT = 23
PIN_KNOB_SWITCH = 19

FONT_UNISPACE = XglcdFont("fonts/Unispace12x24.c", 12, 24)
FONT_FIXED = XglcdFont("fonts/FixedFont5x8.c", 5, 7)

class RotaryEncoder(object):
    def __init__(self, pin_clk, pin_dt, delay=100, cw=None, ccw=None):
        self._rotary = RotaryIRQ(pin_clk, pin_dt)
        self._delay = delay

        self._cb_cw = cw
        self._cb_ccw = ccw

        loop = asyncio.get_event_loop()
        loop.create_task(self.check())

    async def check(self):
        old_value = 0

        while True:
            new_value = self._rotary.value()
            difference = abs(new_value - old_value)

            if new_value > old_value and callable(self._cb_ccw):
                self._cb_ccw(difference)
            elif old_value > new_value and callable(self._cb_cw):
                self._cb_cw(difference)

            old_value = new_value

            await asyncio.sleep_ms(self._delay)

class SafeDisplay(Display):
    def draw_text(self, x, y, text, font, color,  background=0,
                  landscape=False, spacing=1):
        max_length = (self.width - x + spacing) // (font.width + spacing)
        text = text[0:min(max_length, len(text))]
        Display.draw_text(self, x, y, text, font, color, background=background,
                          landscape=landscape, spacing=spacing)


class DisplayScreen(object):
    PIXEL_SHIFT_INTERVAL = 60 * 1000 # 1 min

    def __init__(self):
        self._x0 = 0
        self._y0 = 0
        self._last_shift = time.ticks_ms()
        self._shift_offsets = [(0, 1), (1, 1), (1, 0), (0, 0)]

    def update(self, display, needs_full_redraw=False):
        pass

    def encoder_cw(self, steps):
        pass

    def encoder_ccw(self, steps):
        pass

    def encoder_click(self):
        pass

    def encoder_dblclick(self):
        pass

    def encoder_longpress(self):
        pass

    def needs_pixel_shift(self):
        return self._last_shift + self.PIXEL_SHIFT_INTERVAL < time.ticks_ms()

    def pixel_shift(self):
        self._x0, self._y0 = self._shift_offsets.pop(0)
        self._shift_offsets.append((self._x0, self._y0))
        self._last_shift = time.ticks_ms()
        print("DISPLAYSCREEN: Pixel shift to avoid burn-in, x0={}, y0={}".format(self._x0, self._y0))

class DemoScreen(DisplayScreen):
    def __init__(self):
        self.y = 0

    def update(self, display, needs_full_redraw=False):
        display.draw_text(0, self.y, "Unispace", FONT_UNISPACE, color565(255,128,0))
        self.y += 24
        if self.y > 100:
            self.y = 0

class ScooterDisplay(object):
    def __init__(self, screens):
        self.screens = screens
        if not self.screens:
            self.screens = [DemoScreen()]
        self._screen = 0

        # OLED
        spi = SPI(2, baudrate=14500000, sck=Pin(PIN_DISPLAY_CLK), mosi=Pin(PIN_DISPLAY_MOSI))
        self.display = SafeDisplay(spi, dc=Pin(PIN_DISPLAY_DC), cs=Pin(PIN_DISPLAY_CS), rst=Pin(PIN_DISPLAY_RST))

        loop = asyncio.get_event_loop()
        loop.create_task(self.update_display())

        # Encoder rotation
        self.encoder = RotaryEncoder(PIN_KNOB_CLK, PIN_KNOB_DT, cw=self.encoder_cw, ccw=self.encoder_ccw)

        # Encoder button
        self.button = Pushbutton(Pin(PIN_KNOB_SWITCH, Pin.IN))
        self.button.release_func(self.encoder_push)
        self.button.double_func(self.encoder_dblpush)
        self.button.long_func(self.encoder_longpush)

    def encoder_cw(self, steps):
        print("DISPLAY: Encoder CW, {} steps".format(steps))
        self._screen += 1
        if self._screen > len(self.screens) - 1:
            self._screen = 0

    def encoder_ccw(self, steps):
        print("DISPLAY: Encoder CCW, {} steps".format(steps))
        self._screen -= 1
        if self._screen < 0:
            self._screen = len(self.screens) - 1

    def encoder_push(self):
        print("DISPLAY: Encoder PUSH")
        self.screens[self._screen].encoder_click()

    def encoder_dblpush(self):
        print("DISPLAY: Encoder DBLPUSH")
        self.screens[self._screen].encoder_dblclick()

    def encoder_longpush(self):
        print("DISPLAY: Encoder LONGPUSH")
        self.screens[self._screen].encoder_longpress()

    async def update_display(self):
        current_screen = self._screen
        screen_changed = True
        needs_pixel_shift = False

        while True:
            if screen_changed or needs_pixel_shift:
                self.display.clear()
            if needs_pixel_shift:
                self.screens[self._screen].pixel_shift()

            self.screens[self._screen].update(self.display, needs_full_redraw=screen_changed or needs_pixel_shift)
            current_screen = self._screen
            await asyncio.sleep_ms(1000)

            screen_changed = current_screen != self._screen
            needs_pixel_shift = self.screens[self._screen].needs_pixel_shift()
