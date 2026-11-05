# Daylight-clock

import time
import board
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction, Pull
import neopixel
from adafruit_pcf8523.pcf8523 import PCF8523
import rotaryio
import asyncio
from math import floor

import sunrise_sunset_calculations  # Custom; should exist next to this file

MAX_LAT = 70

#####
# Global state params
#####

DEFAULT_LATITUDE = 42.387959
DEFAULT_LONGITUDE = -71.103088   # boston
TIMEZONE_OFFSET_FOR_DEFAULT_LAT_LONG = -5 # EST

LONGITUDE_WEST = -85.591736   # kalamazoo
LONGITUDE_CENTRAL = -78.345   # halfway between (~Buffalo, or near enough)
LONGITUDE_EAST = DEFAULT_LONGITUDE

i_DATE_INCREMENT = 7  # Every rotary encoder click is 7 days

DEFAULT_I_TZ_PERCENT = 12   # From -12 to 12 off center of timezone;
#  e.g. kazoo -12, boston +12; range -12 to + 12,
# ((num_neopixel/2)/2)

# Global state
latitude_from_slider = DEFAULT_LATITUDE          # updated by sliders
i_day_offset = 0                     # updated by knob
encoder_last_pos = 0                 # updated by knob

print("Hello! :)")

#####
# Set up Lights
#####
NUM_LIGHTS = 48
DEFAULT_NEOPIXEL_BRIGHTNESS = 0.02
neopixel_brightness = DEFAULT_NEOPIXEL_BRIGHTNESS
neopixels = neopixel.NeoPixel(board.A0, NUM_LIGHTS, brightness=neopixel_brightness,
                              auto_write=False)
NIGHT_COLOR = (12, 95, 170)
DAY_COLOR = (250, 227, 160)
OFF = (0, 0, 0)
PIX_HOUR_RESOLUTION_MULTIPLIER = round(NUM_LIGHTS / 24)
BRIGHTNESS_INCREMENT = 0.005


COLOR_TODAY = (120, 120, 120)  # pale magenta?
COLOR_DAY_DYNAMIC = (179, 0, 179)  # MAGENTA

COLOR_VERTICAL = (25, 180, 25)  # pale GREEN?
COLOR_VERTICAL_DYANMIC = (50, 205, 50)  # GREEN

COLOR_HORIZONTAL = (0, 200, 0)  # pale BLUE?
COLOR_HORIZONTAL_DYNAMIC = (0, 205, 0)  # BLUE?

#####
# Set up clock
#####
rtc = PCF8523(board.I2C())

DAYS = ("Mon", "Tues", "Wed", "Thur", "Fri", "Sat", "Sun")
if False:  # change to True to set the time, then turn back to false
    #                     year, mon, date, hour, min, sec, wday, yday, isdst
    t = time.struct_time((2026, 9, 7, 21, 25, 0, 0, -1, -1))
    # you must set year, mon, date, hour, min, sec and weekday
    # yearday is not supported, isdst can be set but we don't do anything
    # with it at this time

    # TODO: set isdst
    # TODO: use isdst in calculations https://www.instructables.com/Adding-Daylight-Savings-Time-to-Your-RTC/
    print("Setting time to:", t)
    rtc.datetime = t
    print("***")
    print(rtc.datetime)


#####
# Set up input slider
#####
slider_in = AnalogIn(board.A1)


def get_slider_value():
    return slider_in.value // 128  # ranges from 0-65535; make 0-512 range


#####
# Set up input toggle
#####
toggle_dynamic_mode = DigitalInOut(board.D6)
toggle_dynamic_mode.direction = Direction.INPUT
toggle_dynamic_mode.pull = Pull.UP


def is_dynamic_mode_enabled():
    return toggle_dynamic_mode.value

#####
# Set up time zone toggle
#####
toggle_tz_west = DigitalInOut(board.D12)
toggle_tz_west.direction = Direction.INPUT
toggle_tz_west.pull = Pull.UP

toggle_tz_east = DigitalInOut(board.D11)
toggle_tz_east.direction = Direction.INPUT
toggle_tz_east.pull = Pull.UP

def get_tz_mode():
    # print(toggle_tz_west.value)
    # print(toggle_tz_east.value)
    if toggle_tz_east.value and toggle_tz_west.value:
        return "CENTER"
    if toggle_tz_east.value:
        return "EAST"
    return "WEST"

#####
# Set up LEDs
#####

led_west = DigitalInOut(board.D10)
led_west.direction = Direction.OUTPUT
led_west.value = False

led_center = DigitalInOut(board.D9)
led_center.direction = Direction.OUTPUT
led_center.value = False

led_east = DigitalInOut(board.D5)
led_east.direction = Direction.OUTPUT
led_east.value = False

#####
# Set up rotary encoder
#####
rotary_encoder_button = DigitalInOut(board.D25)
rotary_encoder_button.direction = Direction.INPUT
rotary_encoder_button.pull = Pull.UP

rotary_encoder = rotaryio.IncrementalEncoder(board.A3, board.A2)

#####
# Helper functions
#####

# https://asd.gsfc.nasa.gov/Craig.Markwardt/doy2026.html
DAYLIGHT_SAVINGS_USA = {
    # 2026	March 8 	November 1
    "2026": (67, 305), 
    # 2027	March 14	November 7
    "2027": (73, 311), 
    # 2028	March 12	November 5
    "2028": (72, 310), 
    # 2029	March 11	November 4
    "2029": (70, 308),
}

def is_daylight_savings_enabled(year, i_day):
   if int(year) > 2026:
       print("WARNING: year not supported, using 2026")
       year = "2026"
   i_dst_start, i_dst_stop = DAYLIGHT_SAVINGS_USA[str(year)]
   if i_day < i_dst_start or i_day >= i_dst_stop:
       return False
   return True

def min_utc_to_i_hour_tz(min_utc, is_dst_enabled):
    tz_offset_hr = TIMEZONE_OFFSET_FOR_DEFAULT_LAT_LONG
    if is_dst_enabled:
        tz_offset_hr += 1
    hr_tz = min_utc / 60 + tz_offset_hr
    return hr_tz


# Return hour of day as float, so will be value 0-24
def get_sunstate_indices_for_date_lat_lon(year, i_day, lat, lon):
    # print("get_sunstate_indices_for_date_lat_lon:", year, i_day, lat, lon)
    rise, _, set = sunrise_sunset_calculations.riseset_in_noaa_min_utc(year,
                                                                       i_day,
                                                                       lat,
                                                                       lon)
    # print("rise, set:", rise, set)
    is_dst_enabled = is_daylight_savings_enabled(year, i_day)
    # print("Daylight savings enabled?", i_day, is_dst_enabled)
    return (min_utc_to_i_hour_tz(rise, is_dst_enabled),
            min_utc_to_i_hour_tz(set, is_dst_enabled))

def day_of_year_index(t):
    days=[0,31,59,90,120,151,181,212,243,273,304,334]    # Number of days at the beginning of the month in a not leap year.
    d = days[(t.tm_mon-1)]+t.tm_mday
    leap_year = t.tm_year % 4 == 0 and t.tm_year % 100 != 0
    if leap_year and t.tm_mon > 2:
        # add a day if it's a leap year and we're after february
        d += 1
    return d


# Relies on a whole host of global variables
def update_neopixels_for_current_state():
    # Update sunrise/sunset values
    t = rtc.datetime
    i_day = day_of_year_index(t)
    if is_dynamic_mode_enabled():
        leap_year = t.tm_year % 4 == 0 and t.tm_year % 100 != 0
        days_in_year = 366 if leap_year else 365
        i_day_adjusted = (i_day + i_day_offset) % days_in_year
        tz_mode = get_tz_mode()
        if tz_mode == "CENTER":
            lon_adjusted = LONGITUDE_CENTRAL
        elif tz_mode == "EAST":
            lon_adjusted = LONGITUDE_EAST
        else:
            lon_adjusted = LONGITUDE_WEST
        i_sunrise, i_sunset = get_sunstate_indices_for_date_lat_lon(t.tm_year,
                                                                    i_day_adjusted, 
                                                                    latitude_from_slider, 
                                                                    lon_adjusted)
        # print("daylight (adjusted by ", i_day_offset, "): ", i_sunrise, i_sunset)
    else:
        i_sunrise, i_sunset = get_sunstate_indices_for_date_lat_lon(t.tm_year, i_day, 
                                                                    DEFAULT_LATITUDE, 
                                                                    DEFAULT_LONGITUDE)
        # print("daylight: ", i_sunrise, i_sunset)
    neopixels.fill(NIGHT_COLOR)

    # print("daylight indices: ", i_sunrise * PIX_HOUR_RESOLUTION_MULTIPLIER, i_sunset * PIX_HOUR_RESOLUTION_MULTIPLIER)
    # print("***")
    for i in range(round(i_sunrise * PIX_HOUR_RESOLUTION_MULTIPLIER),
                   round(i_sunset * PIX_HOUR_RESOLUTION_MULTIPLIER)):
        i = i % NUM_LIGHTS
        neopixels[i] = DAY_COLOR
    neopixels.brightness = neopixel_brightness
    neopixels.show()


async def refresh_neopixels(interval):
    while True:
        print_time()
        update_neopixels_for_current_state()
        await asyncio.sleep(interval)

def map_range(x, in_min, in_max, out_min, out_max):
    return out_min + ((x - in_min) * (out_max - out_min) / (in_max - in_min))


async def watch_slider(interval):
    global latitude_from_slider
    prev_val = 0
    while True:
        val = get_slider_value()
        if abs(val - prev_val) > 2:
            print(f"Slider updated! {val}")
            prev_val = val
            if val < 250:
                new_latitude = map_range(val, 5, 250, MAX_LAT, 0)
                new_latitude = min(new_latitude, MAX_LAT)
            else:
                new_latitude = map_range(val, 250, 495, 0, -MAX_LAT)
                new_latitude = max(new_latitude, -MAX_LAT)

        if latitude_from_slider != new_latitude:
            latitude_from_slider = new_latitude
            print(f"Slider updated! latitude now {latitude_from_slider} degrees ({val})")
        if is_dynamic_mode_enabled():
            update_neopixels_for_current_state()
        await asyncio.sleep(interval)

def update_tz_leds():
    led_west.value = False
    led_center.value = False
    led_east.value = False

    if is_dynamic_mode_enabled():
        tz = get_tz_mode()
        if tz == "WEST":
            led_west.value = True
        elif tz == "EAST":
            led_east.value = True
        else:
            led_center.value = True

async def watch_toggle_dynamic_mode(interval):
    last_value = toggle_dynamic_mode.value
    while True:
        value = toggle_dynamic_mode.value
        if value != last_value:
            last_value = value
            print(f"Toggle toggled! Now: {value}")
            update_tz_leds()
            update_neopixels_for_current_state()
        await asyncio.sleep(interval)

async def watch_toggle_tz(interval):
    last_value_west = toggle_tz_west.value
    last_value_east = toggle_tz_east.value
    while True:
        if (toggle_tz_west.value != last_value_west) or (toggle_tz_east.value != last_value_east):
            last_value_west = toggle_tz_west.value
            last_value_east = toggle_tz_east.value

            tz_mode = get_tz_mode()
            print(f"TZ toggled! Now: {tz_mode}")

            update_tz_leds()
            update_neopixels_for_current_state()
        await asyncio.sleep(interval)

async def watch_encoder(interval):
    global encoder_last_pos, i_day_offset, neopixel_brightness, i_DATE_INCREMENT
    while True:
        pos = rotary_encoder.position
        # If the button is pushed, reset the day offset
        delta = floor(pos - encoder_last_pos)
        if delta:
            encoder_last_pos = pos
            if is_dynamic_mode_enabled():
                i_day_offset += (delta * i_DATE_INCREMENT)
                print(f"The day offset has changed by {delta} to {i_day_offset}")
            else:
                neopixel_brightness += delta * BRIGHTNESS_INCREMENT
                if neopixel_brightness > 0.8:
                    neopixel_brightness = 0.8
                if neopixel_brightness < 0:
                    neopixel_brightness = 0

                print(f"The brightness has changed to {neopixel_brightness}")
            update_neopixels_for_current_state()
        if not rotary_encoder_button.value:
            # print("YAY")
            if is_dynamic_mode_enabled():
                i_day_offset = 0
                print(f"Reset day offset to 0 {i_day_offset}")
            else:
                neopixel_brightness = DEFAULT_NEOPIXEL_BRIGHTNESS
                print(f"Reset brightness to default")
            update_neopixels_for_current_state()
        await asyncio.sleep(interval)


def print_time():
    t = rtc.datetime
    print(f"Date is {DAYS[int(t.tm_wday)]} {t.tm_mday}/{t.tm_mon}/{t.tm_year}")
    print(f"Time is {t.tm_hour}:{t.tm_min:02}:{t.tm_sec:02}")


#####
# Main loop
#####

async def main():
    update_tz_leds()
    update_neopixels_for_current_state()

    light_task = asyncio.create_task(refresh_neopixels(30))
    toggle_task = asyncio.create_task(watch_toggle_dynamic_mode(.1))
    tz_toggle_task = asyncio.create_task(watch_toggle_tz(.1))
    slider_task = asyncio.create_task(watch_slider(.1))
    encoder_task = asyncio.create_task(watch_encoder(.1))
    await asyncio.gather(light_task, toggle_task, tz_toggle_task, slider_task, encoder_task)
    print("done")

asyncio.run(main())
