import machine
import neopixel

import random
import time

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
	def run(self, lights):
		pass

class LarsonScannerEffect(Effect):
	EYE = (4, 32, 256, 32, 4)

	def __init__(self, color, speed):
		self._color = color
		self._speed = speed
	
	def run(self, lights):
		colors = [(self._color[0] * x // 256, self._color[1] * x // 256, self._color[2] * x // 256) for x in self.EYE]
		pixels = lights.count

		def move(dir):
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

				time.sleep_ms(self._speed)

		move(False)
		move(True)

class BreathingEffect(Effect):
	def __init__(self, color, steps):
		self._color = color
		self._steps = steps
	
	def run(self, lights):
		pixels = lights.count
		step_size = 256 // self._steps

		def inexhale(ex):
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
				time.sleep_ms(1)
		
		inexhale(False)
		inexhale(True)

class SimpleDot(Effect):
	def __init__(self, color):
		self._color = color

	def run(self, lights):
		for i in range(lights.count):
			lights.clear()
			lights.set_pixel(i, self._color)
			lights.apply()
			time.sleep_ms(25)

class RainbowEffect(Effect):
	def __init__(self, delay):
		self._delay = delay
	
	def run(self, lights):
		for i in range(256):
			for j in range(lights.count):
				pos = int((i * 256 / lights.count) + j) % 255
				lights.set_pixel(j, self.color_on_wheel(pos))
			lights.apply()
			time.sleep_ms(self._delay)
	
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
	def __init__(self, cooling, sparking, delay):
		self._cooling = cooling
		self._sparking = sparking
		self._delay = delay
		self._heat = None
	
	def run(self, lights):
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
		
		for _ in range(100):
			burn()
			lights.apply()
			time.sleep_ms(self._delay)
	
	def set_pixel_heat_color(self, lights, pixel, temperature):
		t192 = round((temperature / 255) * 191)

		heatramp = t192 % 64
		heatramp *= 4

		if t192 > 128: # hottest
			lights.set_pixel(pixel, (255, 255, heatramp))
		elif t192 > 64: # middle
			lights.set_pixel(pixel, (255, heatramp, 0))
		else: # coolest
			lights.set_pixel(pixel, (heatramp, 0, 0))

lights = ScooterLight(PIXEL_PIN, PIXEL_COUNT)
larson = LarsonScannerEffect((255, 0, 0), 30)
breathing = BreathingEffect((127, 127, 127), 100)
rainbow = RainbowEffect(100)
fire = FireEffect(100, 60, 15)

effects = (rainbow, fire, larson, breathing)
#effect = random.choice(effects)

#while(True):
#	effect.run(lights)
#lights.clear()
#lights.apply()

while(True):
	for effect in effects:
		for _ in range(5):
			effect.run(lights)
		lights.clear()
		lights.apply()
