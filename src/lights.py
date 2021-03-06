import machine
import neopixel
import random

import uasyncio as asyncio


PIXEL_PIN = machine.Pin(4)
PIXEL_COUNT = 29


class ScooterLight(object):
    def __init__(self, pin, count):
        self._pin = pin
        self._count = count
        self._np = neopixel.NeoPixel(pin, count * 2)

    @property
    def count(self):
        return self._count

    def set_all(self, color):
        for i in range(self._count):
            self.set_pixel(i, color)

    def set_pixel(self, pixel, color):
        self._np[pixel] = self._np[self._count * 2 - pixel - 1] = color

    def clear(self):
        self.set_all((0, 0, 0))

    def apply(self):
        self._np.write()

class Effect(object):
    async def run(self, lights):
        pass

class NoEffect(Effect):
    async def run(self, lights):
        await asyncio.sleep_ms(500)

class LarsonScannerEffect(Effect):
    EYE = (4, 32, 256, 32, 4)

    def __init__(self, color, speed):
        self._color = color
        self._speed = speed

        self._colors = [(self._color[0] * x // 256, self._color[1] * x // 256, self._color[2] * x // 256) for x in self.EYE]

    async def run(self, lights):
        colors = [(self._color[0] * x // 256, self._color[1] * x // 256, self._color[2] * x // 256) for x in self.EYE]
        pixels = lights.count

        async def move(dir):
            r = range(len(self.EYE) - 1, pixels)
            if dir:
                r = reversed(r)

            for i in r:
                lights.clear()

                for j in range(len(colors)):
                    p = i - len(colors) + j + 1
                    if p < 0 or p > pixels - 1:
                        continue
                    lights.set_pixel(p, colors[j])
                lights.apply()

                await asyncio.sleep_ms(self._speed)

        await move(False)
        await move(True)

class RunningLightEffect(Effect):
    LIGHT = (256, 32, 32, 4, 4)

    def __init__(self, color, speed):
        self._color = color
        self._speed = speed
        self._colors = [(self._color[0] * x // 256, self._color[1] * x // 256, self._color[2] * x // 256) for x in self.LIGHT]

    async def run(self, lights):
        colors = [(self._color[0] * x // 256, self._color[1] * x // 256, self._color[2] * x // 256) for x in self.LIGHT]
        pixels = lights.count

        r = range(len(self.LIGHT) - 1, pixels)

        for i in r:
            lights.clear()

            for j in range(len(colors)):
                p = i - len(colors) + j + 1
                if p < 0 or p > pixels - 1:
                    continue
                lights.set_pixel(p, colors[j])
            lights.apply()

            await asyncio.sleep_ms(self._speed)

class BreathingEffect(Effect):
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    def __init__(self, color, steps):
        self._color = color
        self._steps = steps

    async def run(self, lights):
        pixels = lights.count
        step_size = 256 // self._steps

        async def inexhale(ex):
            rng = range(0, 256, step_size)
            if ex:
                rng = reversed(rng)

            for i in rng:
                r, g, b = self._color
                r = int((i / 256) * r)
                g = int((i / 256) * g)
                b = int((i / 256) * b)
                lights.set_all((r, g, b))
                lights.apply()
                await asyncio.sleep_ms(1)

        await inexhale(False)
        await inexhale(True)


class SimpleDot(Effect):
    def __init__(self, color):
        self._color = color

    async def run(self, lights):
        for i in range(lights.count):
            lights.clear()
            lights.set_pixel(i, self._color)
            lights.apply()
            await asyncio.sleep_ms(25)


class RainbowEffect(Effect):
    def __init__(self, delay):
        self._delay = delay
        self._i = 0

    async def run(self, lights):
        for j in range(lights.count):
            pos = int((self._i * 256 / lights.count) + j) % 255
            lights.set_pixel(j, self.color_on_wheel(pos))
        lights.apply()

        self._i += 1
        if self._i > 255:
            self._i = 0

        await asyncio.sleep_ms(self._delay)

    def color_on_wheel(self, pos):
        if pos < 85:
            r = pos * 3
            g = 255 - pos * 3
            b = 0
        elif pos < 170:
            pos -= 85
            r = 255 - pos * 3
            g = 0
            b = pos * 3
        else:
            pos -= 170
            r = 0
            g = pos * 3
            b = 255 - pos * 3

        return (r, g, b)


class FireEffect(Effect):
    # hot, mid, cold
    RED = (lambda x: (255, 255, x), lambda x: (255, x, 0), lambda x: (x, 0, 0))
    BLUE = (lambda x: (x, 255, 255), lambda x: (0, x, 255), lambda x: (0, 0, x))
    GREEN = (lambda x: (x, 255, x), lambda x: (x, 255, 0), lambda x: (0, x, 0))

    def __init__(self, cooling, sparking, delay, color=RED):
        self._cooling = cooling
        self._sparking = sparking
        self._delay = delay
        self._color = color

        self._heat = None

    async def run(self, lights):
        if self._heat is None:
            self._heat = [0] * lights.count
        heat = self._heat

        def burn():
            # cool down every cell a little
            for i in range(lights.count):
                cooldown = random.randint(0, (((self._cooling * 10) // lights.count) + 1))
                if cooldown > heat[i]:
                    heat[i] = 0
                else:
                    heat[i] = heat[i] - cooldown

            # heat from each cell drifts up and diffuses a little
            for i in range(lights.count - 1, 1, -1):
                heat[i] = (heat[i - 1] + heat[i - 2] + heat[i - 2]) // 3

            # randomly ignite new sparks near the bottom
            if random.randint(0, 255) < self._sparking:
                spark = random.randint(0, 7)
                heat[spark] = heat[spark] + random.randint(160, 255)

            # convert to led colors
            for i in range(lights.count):
                self.set_pixel_heat_color(lights, i, heat[i])

        burn()
        lights.apply()
        await asyncio.sleep_ms(self._delay)

    def set_pixel_heat_color(self, lights, pixel, temperature):
        t192 = round((temperature / 255) * 191)

        heatramp = t192 % 64
        heatramp *= 4

        if t192 > 128: # hottest
            lights.set_pixel(pixel, self._color[0](heatramp))
        elif t192 > 64: # middle
            lights.set_pixel(pixel, self._color[1](heatramp))
        else: # coolest
            lights.set_pixel(pixel, self._color[2](heatramp))


class LightShow(object):
    def __init__(self):
        self._lights = ScooterLight(PIXEL_PIN, PIXEL_COUNT)

        self._effects = dict(larson=LarsonScannerEffect((255, 0, 0), 30),
                             red_running=RunningLightEffect((255, 0, 0), 30),
                             green_running=RunningLightEffect((0, 255, 0), 30),
                             blue_running=RunningLightEffect((0, 0, 255), 30),
                             rainbow=RainbowEffect(70),
                             red_fire=FireEffect(100, 60, 15, FireEffect.RED),
                             green_fire=FireEffect(100, 60, 15, FireEffect.GREEN),
                             blue_fire=FireEffect(100, 60, 15, FireEffect.BLUE),
                             red_breathing=BreathingEffect(BreathingEffect.RED, 70),
                             blue_breathing=BreathingEffect(BreathingEffect.BLUE, 70),
                             green_breathing=BreathingEffect(BreathingEffect.GREEN, 70),
                             off=NoEffect())

        self._effect = "larson"
        self.load()

        loop = asyncio.get_event_loop()
        loop.create_task(self.update())

    @property
    def effect(self):
        return self._effect

    @effect.setter
    def effect(self, value):
        if not value in self._effects:
            raise ValueError()
        self._effect = value
        self.save()
        print("LIGHTSHOW: New effect = {}".format(self._effect))

    async def update(self):
        effect = self._effect
        while(True):
            if effect != self._effect:
                self._lights.clear()
                self._lights.apply()
            effect = self._effect
            await self._effects[self._effect].run(self._lights)

    def load(self):
        try:
            with open("/data/effect.txt", "r") as f:
                effect = f.readline().strip()
            print("LIGHTSHOW: Loaded effect {} from /data/effect.txt".format(effect))
            if effect in self._effects:
                self._effect = effect
        except:
            print("LIGHTSHOW: ERROR - Could not load effect from /data/effect.txt")

    def save(self):
        try:
            with open("/data/effect.txt", "w") as f:
                f.write(self._effect)
                f.write("\n")
        except:
            print("LIGHTSHOW: ERROR - Could not write effect to /data/effect.txt")
