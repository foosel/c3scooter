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
        self.trip = 0.0

        self.load()

        loop = asyncio.get_event_loop()
        loop.create_task(self.update())
        loop.create_task(self.persist())

    def reset_trip(self):
        self.trip = 0.0
        self.top_speed = 0.0
        self.push_to_callback()

    def push_to_callback(self):
        if self.callback:
            self.callback(self.speed, self.distance, self.top_speed, self.trip)

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
            self.trip += distance
            self.top_speed = max(self.top_speed, self.speed)

            if dirty:
                self.push_to_callback()

            await asyncio.sleep(DELAY)

    def load(self):
        try:
            with open("/data/total.txt", "rb") as f:
                self.distance = float(f.readline())
            print("SPEEDOMETER: Total data loaded, {:2f} total".format(self.distance))
        except:
            print("SPEEDOMETER: ERROR - could not read distance from /data/total.txt, does it exist?")

        try:
            with open("/data/trip.txt", "rb") as f:
                self.trip = float(f.readline())
                self.top_speed = float(f.readline())
            print("SPEEDOMETER: Trip data loaded, {:.2f} trip, {:.2f} top speed".format(self.trip, self.top_speed))
        except:
            print("SPEEDOMETER: ERROR - could not read trip and speed from /data/trip.txt, does it exist?")

        self.push_to_callback()

    def save(self, trip=True, total=True):
        if total:
            try:
                with open("/data/total.txt", "wb") as f:
                    f.write("{}\n".format(self.distance))
                print("SPEEDOMETER: Persisted total to /data/total.txt")
            except:
                print("SPEEDOMETER: ERROR - could not save total to /data/total.txt")

        if trip:
            try:
                with open("/data/trip.txt", "wb") as f:
                    f.write("{}\n".format(self.trip))
                    f.write("{}\n".format(self.top_speed))
                print("SPEEDOMETER: Persisted trip data to /data/trip.txt")
            except:
                print("SPEEDOMETER: ERROR - could not save trip to /data/trip.txt")

    async def persist(self):
        distance = self.distance
        trip = self.trip
        top_speed = self.top_speed

        while True:
            self.save(trip=self.trip != trip or self.top_speed != top_speed,
                      total=self.distance != distance)

            distance = self.distance
            trip = self.trip
            top_speed = self.top_speed

            await asyncio.sleep(60)

