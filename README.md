# c3scooter

A ridiculously over the top "pimp-my-ride" for my 36c3 scooter.

## Contents

  * `src` - MicroPython firmware, flash with `ampy` (`pip install adafruit-ampy` & `ampy -p <port> put main.py`)
  * `stls` - printables

## Hardware

  * [WeSkate Scooter](https://www.amazon.de/gp/product/B07SS7GXDT/) ([Affiliate Link](https://amzn.to/2PQr7il))
  * ["Wemos" Mini D1 ESP32](https://www.aliexpress.com/item/32834982479.html) (but any ESP32 or MicroPython based board should work just fine)
  * WS2812 LED strip, 5V, 60 Leds/m, optionally black PCB & IP67
  * [Waveshare 1.5" 128x128px RGB OLED module](https://www.aliexpress.com/item/32878557203.html)
  * [KY-040 rotary encoder module](https://www.amazon.de/gp/product/B07CMSHWV6/) ([Affiliate Link](https://amzn.to/2ScIAmC))
  * [Reedswitch, plastic housing](https://www.amazon.de/gp/product/B07SZDGXLC/) ([Affiliate Link](https://amzn.to/35ZC6eE))
  * Neodymium disc magnet, e.g. 8x3
  * [RAVPower 5000mAh power bank](https://www.amazon.de/gp/product/B07KSWHV45/) ([Affiliate Link](https://amzn.to/34LeKbp))
  * velcro, cable ties, duct tape and similar...

## Firmware

  * Copy files over using `mpfshell`. Precompile everything but `main.py` to ` .mpf`.

## Dev Environment

```
python3 -m virtualenv -p python3.6 venv
source venv/bin/activate
pip install -r requirements.txt
ln -s venv/lib/python3.6/site-packages/mpy_cross/mpy-cross venv/bin/mpy-cross
```
