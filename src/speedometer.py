import machine
import uasyncio as asyncio
import time

REED_PIN = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP)
RADIUS = 100.0

DISTANCE_PER_ROTATION = 2 * 3.14159 * RADIUS
DELAY = 10.0
HOUR_FRACTION = 3600.0 / DELAY

class SwitchCounter(object):
    def __init__(self, pin, trigger=machine.Pin.IRQ_FALLING, min_ago=300):
        self._counter = 0
        pin.irq(trigger=trigger, handler=self.handle_interrupt)

        # debounce
        self._min_ago = min_ago
        self._next_call = time.ticks_ms() + self._min_ago
    
    def pop_counter(self):
        counter = self._counter
        self._counter = 0
        return counter
    
    def handle_interrupt(self, pin):
        if time.ticks_ms() > self._next_call:
            print("SPEEDOMETER: beep")
            self._next_call = time.ticks_ms() + self._min_ago
            self._counter += 1

async def task():
    counter = SwitchCounter(REED_PIN)

    total_distance = 0.0
    top_speed = 0.0

    while True:
        counter_value = counter.pop_counter()
        distance = counter_value * DISTANCE_PER_ROTATION # in mm
        speed = HOUR_FRACTION * distance                 # in mm/h

        total_distance += distance
        top_speed = max(top_speed, speed)

        print("SPEEDOMETER Counter: {} Distance: {}m Speed: {}km/h Total Distance: {}m Top Speed: {}".format(counter_value, 
                                                                                                             distance / 1000.0, 
                                                                                                             speed / 1000000.0,
                                                                                                             total_distance / 1000.0,
                                                                                                             top_speed / 1000000.0))
        await asyncio.sleep(DELAY)