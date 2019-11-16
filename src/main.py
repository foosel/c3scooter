import machine
import neopixel

import random
import time

import uasyncio as asyncio

import micropython
micropython.alloc_emergency_exception_buf(100)

import lights
import speedometer

loop = asyncio.get_event_loop()
loop.create_task(lights.task())
loop.create_task(speedometer.task())
loop.run_forever()

