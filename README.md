# c3scooter

A ridiculously over the top "pimp-my-ride" for my 36c3 scooter.

## Contents

  * `src` - MicroPython firmware, flash with `ampy` (`pip install adafruit-ampy` & `ampy -p <port> put main.py`)
  * `stls` - printables

## Hardware

  * [WeSkate Scooter](https://www.amazon.de/gp/product/B07SS7GXDT/)
  * [Lolin D32](https://wiki.wemos.cc/products:d32:d32) (but any ESP32 or MicroPython based board should work just fine)
    * Note: The Lolin board appears to have a circuit design flaw causing in issues to enter the bootloader. It ships with MicroPython, flashing a new version is a major PITA however. Thankfully the python files can be deployed without needing that thanks to something like `ampy`.
