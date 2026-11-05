# `daylight-clock`

[<img alt="Static Badge" src="https://img.shields.io/badge/%F0%9F%AA%B4%20Houseplant%20-x?style=flat&amp;label=Project%20type&amp;color=1E1E1D">](https://www.hannahilea.com/blog/houseplant-programming)

Project write-up here: [Here comes the sun[light]: An ambient Daylight Clock with time and space controls](https://hannahilea.com/blog/daylight-clock)

Inspired by CCEckman's [aclock](https://cceckman.com/writing/aclock/); the daylight calculations were ported from cceckman's [Rust implementation](https://github.com/cceckman/aclock/blob/5547d8490151eafa77f33dc697cbb58ea0035c70/server/src/riseset.rs#L60) of the [NOAA](https://gml.noaa.gov/grad/solcalc/calcdetails.html) equations.

Code for controlling a strand of neopixels in a circle, that correspond to a 24-hour clock. Based on an input latitude and longitude, calculates the span of LEDs to between sunrise and sunset for the given day.


## Software set-up (sparse!)

1. On an [Adafruit Feather RP2040](https://www.adafruit.com/product/4884), follow [set-up instructions](https://learn.adafruit.com/adafruit-feather-rp2040-pico) to install CircuitPython
    - When connecting the hardware components, the board's [pinout](https://learn.adafruit.com/adafruit-feather-rp2040-pico/pinouts) is useful
2. Downloaded the necessary [CircuitPython libraries](https://circuitpython.org/libraries) and add them to your board:
    - For lights: 
        - `neopixel.mpy`
    - For RTC (clock):
        - `adafruit_bus_device` folder
        - `adafruit_register` folder
        - `adafruit_pcf8523` folder
        - `adafruit_datetime.mpy`
    - For asyncio support:
        - `asyncio` folder 
        - `adafruit_ticks.mpy`

3. Copy the [`code.py`](./code.py) and [`sunrise-sunset-python.py`](./sunrise-sunset-python.py) files to the top-level directory on the Feather

4. Update the `LATITUDE`, `LONGITUDE`, and `TIME_ZONE` values in [`sunrise-sunset-python.py`](./sunrise-sunset-python.py) for your clock's home locale. (Default is set for Boston).

...that should be it!
