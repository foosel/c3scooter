import machine
import neopixel

import random
import time

import uasyncio as asyncio

import micropython
micropython.alloc_emergency_exception_buf(100)

import lights
import speedometer
import display

class SpeedometerScreen(display.DisplayScreen):
    def __init__(self, speedometer):
        self._speedometer = speedometer

        self._dirty = dict(speed=False,
                           distance=False,
                           top_speed=False,
                           trip=False)

        self._speed = 0.0
        self._distance = 0.0
        self._top_speed = 0.0
        self._trip = 0.0

    def update(self, screen, needs_full_redraw=False):
        from ssd1351 import color565

        if needs_full_redraw:
            screen.draw_text(0, 0, "Speed (km/h)", display.FONT_FIXED, color565(255,255,255))
            screen.draw_text(0, 45, "Top Speed (km/h)", display.FONT_FIXED, color565(255, 255, 255))
            screen.draw_text(0, 63, "Distance (km)", display.FONT_FIXED, color565(255, 255, 255))
            screen.draw_text(0, 91, "Total Distance (km)", display.FONT_FIXED, color565(255, 255, 255))

        if self._speed != self._speedometer.speed or needs_full_redraw:
            self._speed = self._speedometer.speed
            screen.fill_rectangle(0, 9, 127, 24, color565(0, 0, 0))
            screen.draw_text(0, 9, "{:.2f}".format(self._speed), display.FONT_UNISPACE, color565(0, 255, 0))

        if self._top_speed != self._speedometer.top_speed or needs_full_redraw:
            self._top_speed = self._speedometer.top_speed
            screen.fill_rectangle(0, 54, 127, 8, color565(0, 0, 0))
            screen.draw_text(0, 54, "{:.2f}".format(self._top_speed), display.FONT_FIXED, color565(0, 255, 0))

        if self._trip != self._speedometer.trip or needs_full_redraw:
            self._trip = self._speedometer.trip
            screen.fill_rectangle(0, 72, 127, 8, color565(0, 0, 0))
            screen.draw_text(0, 72, "{:.2f}".format(self._trip / 1000.0), display.FONT_FIXED, color565(0, 255, 0))

        if self._distance != self._speedometer.distance or needs_full_redraw:
            self._distance = self._speedometer.distance
            screen.fill_rectangle(0, 100, 127, 8, color565(0, 0, 0))
            screen.draw_text(0, 100, "{:.2f}".format(self._distance / 1000.0), display.FONT_FIXED, color565(0, 255, 0))

    def encoder_longpress(self):
        self._speedometer.reset_trip()
        self._speedometer.save()

    def encoder_dblclick(self):
        self._speedometer.save()

class LightShowScreen(display.DisplayScreen):
    def __init__(self, light_show):
        self.light_show = light_show
        self._effect_order = ["larson", "rainbow",
                              "red_fire", "green_fire", "blue_fire",
                              "red_breathing", "green_breathing", "blue_breathing",
                              "off"]
        self._dirty = False

    def update(self, screen, needs_full_redraw=False):
        from ssd1351 import color565

        if needs_full_redraw:
            screen.draw_text(0, 0, "Light Effect", display.FONT_FIXED, color565(255, 255, 255))

        if self._dirty or needs_full_redraw:
            self._dirty = False
            screen.fill_rectangle(0, 9, 127, 8, color565(0, 0, 0))
            screen.draw_text(0, 9, self.light_show.effect, display.FONT_FIXED, color565(0, 255, 0))

    def encoder_click(self):
        index = self._effect_order.index(self.light_show.effect)
        index += 1
        if index > len(self._effect_order) - 1:
            index = 0
        self.light_show.effect = self._effect_order[index]
        self._dirty = True


def main():
    # light show
    light_show = lights.LightShow()
    light_show_screen = LightShowScreen(light_show)

    # speedometer
    sm = speedometer.Speedometer()
    speedometer_screen = SpeedometerScreen(sm)

    # display unit
    display_unit = display.ScooterDisplay([speedometer_screen,
                                           light_show_screen])

    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Interrupted")

if __name__ == "__main__":
    main()
