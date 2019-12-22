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
    def __init__(self):
        self._dirty = dict(speed=False,
                           distance=False,
                           top_speed=False)
        self._speed = 0.0
        self._distance = 0.0
        self._top_speed = 0.0

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = value
        self._dirty["speed"] = True

    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, value):
        self._distance = value
        self._dirty["distance"] = True

    @property
    def top_speed(self):
        return self._top_speed

    @top_speed.setter
    def top_speed(self, value):
        self._top_speed = value
        self._dirty["top_speed"] = True

    def update(self, screen, needs_full_redraw=False):
        from ssd1351 import color565

        if needs_full_redraw:
            screen.draw_text(0, 0, "Speed", display.FONT_FIXED, color565(255,255,255))
            screen.draw_text(0, 35, "Distance", display.FONT_FIXED, color565(255, 255, 255))
            screen.draw_text(0, 70, "Top Speed", display.FONT_FIXED, color565(255, 255, 255))

        if self._dirty["speed"] or needs_full_redraw:
            self._dirty["speed"] = False
            screen.fill_rectangle(0, 9, 127, 24, color565(0, 0, 0))
            screen.draw_text(0, 9, "{:.2f} km/h".format(self._speed), display.FONT_UNISPACE, color565(0, 255, 0))

        if self._dirty["distance"] or needs_full_redraw:
            self._dirty["distance"] = False
            screen.fill_rectangle(0, 44, 127, 24, color565(0, 0, 0))
            screen.draw_text(0, 44, "{:.2f} m".format(self._distance), display.FONT_UNISPACE, color565(0, 255, 0))

        if self._dirty["top_speed"] or needs_full_redraw:
            self._dirty["top_speed"] = False
            screen.fill_rectangle(0, 79, 127, 24, color565(0, 0, 0))
            screen.draw_text(0, 79, "{:.2f} km/h".format(self._top_speed), display.FONT_UNISPACE, color565(0, 255, 0))

class LightShowScreen(display.DisplayScreen):
    def __init__(self, light_show):
        self.light_show = light_show
        self._effect_order = ["larson", "red_fire", "green_fire", "blue_fire", "red_breathing", "blue_breathing", "green_breathing", "off"]
        self._dirty = False

    def update(self, screen, needs_full_redraw=False):
        from ssd1351 import color565

        if needs_full_redraw:
            screen.draw_text(0, 0, "Light Effect", display.FONT_FIXED, color565(255, 255, 255))

        if self._dirty or needs_full_redraw:
            self._dirty = False
            screen.fill_rectangle(0, 9, 127, 24, color565(0, 0, 0))
            screen.draw_text(0, 9, self.light_show.effect, display.FONT_UNISPACE, color565(0, 255, 0))


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
    speedometer_screen = SpeedometerScreen()

    def update_speedometer_screen(speed, distance, top_speed):
        speedometer_screen.speed = speed / 1000000.0
        speedometer_screen.distance = distance / 1000.0
        speedometer_screen.top_speed = top_speed / 1000000.0

    sm = speedometer.Speedometer(callback=update_speedometer_screen)

    # display unit
    display_unit = display.ScooterDisplay([speedometer_screen, light_show_screen])

    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Interrupted")

if __name__ == "__main__":
    main()
