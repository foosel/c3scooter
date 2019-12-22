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

        self._speedometer.callback = self.speedometer_update
        self._speedometer.push_to_callback()

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        self._dirty["speed"] = self._speed != value
        self._speed = value

    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, value):
        self._dirty["distance"] = self._distance != value
        self._distance = value

    @property
    def top_speed(self):
        return self._top_speed

    @top_speed.setter
    def top_speed(self, value):
        self._dirty["top_speed"] = self._top_speed != value
        self._top_speed = value

    @property
    def trip(self):
        return self._trip

    @trip.setter
    def trip(self, value):
        self._dirty["trip"] = self._trip != value
        self._trip = value

    def speedometer_update(self, speed, distance, top_speed, trip):
        self.speed = speed / 1000000.0
        self.distance = distance / 1000000.0
        self.top_speed = top_speed / 1000000.0
        self.trip = trip / 1000000.0

    def update(self, screen, needs_full_redraw=False):
        from ssd1351 import color565

        if needs_full_redraw:
            screen.draw_text(0, 0, "Speed (km/h)", display.FONT_FIXED, color565(255,255,255))
            screen.draw_text(0, 45, "Top Speed (km/h)", display.FONT_FIXED, color565(255, 255, 255))
            screen.draw_text(0, 63, "Distance (km)", display.FONT_FIXED, color565(255, 255, 255))
            screen.draw_text(0, 91, "Total Distance (km)", display.FONT_FIXED, color565(255, 255, 255))

        if self._dirty["speed"] or needs_full_redraw:
            self._dirty["speed"] = False
            screen.fill_rectangle(0, 9, 127, 24, color565(0, 0, 0))
            screen.draw_text(0, 9, "{:.2f}".format(self._speed), display.FONT_UNISPACE, color565(0, 255, 0))

        if self._dirty["top_speed"] or needs_full_redraw:
            self._dirty["top_speed"] = False
            screen.fill_rectangle(0, 54, 127, 8, color565(0, 0, 0))
            screen.draw_text(0, 54, "{:.2f}".format(self._top_speed), display.FONT_FIXED, color565(0, 255, 0))

        if self._dirty["trip"] or needs_full_redraw:
            self._dirty["trip"] = False
            screen.fill_rectangle(0, 72, 127, 8, color565(0, 0, 0))
            screen.draw_text(0, 72, "{:.2f}".format(self._trip), display.FONT_FIXED, color565(0, 255, 0))

        if self._dirty["distance"] or needs_full_redraw:
            self._dirty["distance"] = False
            screen.fill_rectangle(0, 100, 127, 8, color565(0, 0, 0))
            screen.draw_text(0, 100, "{:.2f}".format(self._distance), display.FONT_FIXED, color565(0, 255, 0))

    def encoder_longpress(self):
        self._speedometer.reset_trip()

    def encoder_dblclick(self):
        self._speedometer.save()

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
