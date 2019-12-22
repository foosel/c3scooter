import machine
import uasyncio as asyncio
import time

REED_PIN = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP)
RADIUS = 100.0

DISTANCE_PER_ROTATION = 2 * 3.14159 * RADIUS
DELAY = 1.0
HOUR_FRACTION = 3600.0 / DELAY

class SwitchCounter(object):
    def __init__(self, pin, trigger=machine.Pin.IRQ_FALLING, debounce=300):
        self._counter = 0
        pin.irq(trigger=trigger, handler=self.handle_interrupt)

        # debounce
        self._debounce = debounce
        self._debounced_until = time.ticks_ms() + self._debounce
    
    def pop_counter(self):
        counter = self._counter
        self._counter = 0
        return counter
    
    def handle_interrupt(self, pin):
        if time.ticks_ms() > self._debounced_until:
            print("SPEEDOMETER: beep")
            self._debounced_until = time.ticks_ms() + self._debounce
            self._counter += 1

class Speedometer(object):
    def __init__(self, callback=None):
        self.counter = SwitchCounter(REED_PIN, debounce=50)
        self.callback = callback

        self.speed = 0.0
        self.distance = 0.0
        self.top_speed = 0.0

        loop = asyncio.get_event_loop()
        loop.create_task(self.update())
    
    async def update(self):
        while(True):
            counter_value = self.counter.pop_counter()
            distance = counter_value * DISTANCE_PER_ROTATION # in mm
            speed = HOUR_FRACTION * distance                 # in mm/h

            dirty = False
            if speed != self.speed or distance > 0 or speed > self.top_speed:
                dirty = True

            self.speed = speed
            self.distance += distance
            self.top_speed = max(self.top_speed, self.speed)

            if dirty and self.callback:
                self.callback(self.speed, self.distance, self.top_speed)

            print("SPEEDOMETER: Counter: {} Distance: {}m Speed: {}km/h Total Distance: {}m Top Speed: {}".format(counter_value, 
                                                                                                                distance / 1000.0, 
                                                                                                                self.speed / 1000000.0,
                                                                                                                self.distance / 1000.0,
                                                                                                                self.top_speed / 1000000.0))
            await asyncio.sleep(DELAY)        
