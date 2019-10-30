import machine
import neopixel

import random
import time

import uasyncio as asyncio

import lights


loop = asyncio.get_event_loop()
loop.create_task(lights.task())
loop.run_forever()

