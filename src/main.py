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
        from xglcd_font import XglcdFont
        self.fixed = XglcdFont("fonts/FixedFont5x8.c", 5, 7)
        self.unispace = XglcdFont("fonts/Unispace12x24.c", 12, 24)

        self._dirty = False
        self._speed = 0.0
        self._distance = 0.0
        self._top_speed = 0.0
    
    @property
    def speed(self):
        return self._speed
    
    @speed.setter
    def speed(self, value):
        self._speed = value
        self._dirty = True
    
    @property
    def distance(self):
        return self._distance
    
    @distance.setter
    def distance(self, value):
        self._distance = value
        self._dirty = True
    
    @property
    def top_speed(self):
        return self._top_speed
    
    @top_speed.setter
    def top_speed(self, value):
        self._top_speed = value
        self._dirty = True

    def update(self, display, needs_full_redraw=False):
        from ssd1351 import color565

        if needs_full_redraw:
            display.draw_text(0, 0, "Speed", self.fixed, color565(255,255,255))
            display.draw_text(0, 35, "Distance", self.fixed, color565(255, 255, 255))
            display.draw_text(0, 70, "Top Speed", self.fixed, color565(255, 255, 255))

        if self._dirty or needs_full_redraw:
            self._dirty = False
            display.fill_rectangle(0, 9, 127, 24, color565(0, 0, 0))
            display.draw_text(0, 9, "{:.2f} km/h".format(self._speed), self.unispace, color565(0, 255, 0))

            display.fill_rectangle(0, 44, 127, 24, color565(0, 0, 0))
            display.draw_text(0, 44, "{:.2f} m".format(self._distance), self.unispace, color565(0, 255, 0))

            display.fill_rectangle(0, 79, 127, 24, color565(0, 0, 0))
            display.draw_text(0, 79, "{:.2f} km/h".format(self._top_speed), self.unispace, color565(0, 255, 0))

def main():
    speedometer_screen = SpeedometerScreen()

    def update_speedometer_screen(speed, distance, top_speed):
        speedometer_screen.speed = speed / 1000000.0
        speedometer_screen.distance = distance / 1000.0
        speedometer_screen.top_speed = top_speed / 1000000.0

    sm = speedometer.Speedometer(callback=update_speedometer_screen)

    display_unit = display.ScooterDisplay([speedometer_screen])

    loop = asyncio.get_event_loop()
    loop.create_task(lights.task())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Interrupted")

if __name__ == "__main__":
    main()
