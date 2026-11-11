# https://hannahilea.com/blog/magtag-mbta-display

from os import getenv
import time
from adafruit_magtag.magtag import MagTag
import json
import board
import alarm

MAX_NUM_DEPARTURES = 2
MAX_REFRESH_BEFORE_SLEEP = 6
GREEN = (0, 255, 0)
YELLOW = (255, 127, 0)

# Get WiFi details, ensure these are setup in settings.toml
ssid = getenv("CIRCUITPY_WIFI_SSID")
password = getenv("CIRCUITPY_WIFI_PASSWORD")

if None in [ssid, password]:
    raise RuntimeError(
        "WiFi settings are kept in settings.toml, "
        "please add them there. The settings file must contain "
        "'CIRCUITPY_WIFI_SSID', 'CIRCUITPY_WIFI_PASSWORD', "
        "at a minimum."
    )

with open('mbta_routes.json') as f:
    DATA_SOURCES = json.load(f)


def get_stuct_time_from_iso_str(iso_str):
    time_now_split = iso_str.replace('-', ' ').replace(":", " ").replace("T", " ").replace(".", " ").split(" ")
    # (year, month, mday, hour, minute, second, wday, yday, isdst)
    ts = time.struct_time((int(time_now_split[0]), int(time_now_split[1]), int(time_now_split[2]),
                                int(time_now_split[3]), int(time_now_split[4]), int(time_now_split[5]),
                                1, 1, 1))
    return ts

# Get our username, key and desired timezone
ssid = getenv("CIRCUITPY_WIFI_SSID")
password = getenv("CIRCUITPY_WIFI_PASSWORD")
aio_username = getenv("ADAFRUIT_AIO_USERNAME")
aio_key = getenv("ADAFRUIT_AIO_KEY")
timezone = getenv("TIMEZONE")
TIME_URL = f"https://io.adafruit.com/api/v2/{aio_username}/integrations/time/strftime?x-aio-key={aio_key}&tz={timezone}"
TIME_URL += "&fmt=%25Y-%25m-%25d+%25H%3A%25M%3A%25S.%25L+%25j+%25u+%25z+%25Z"

magtag = MagTag()
magtag.network.connect()

# Set up lights
magtag.peripherals.neopixel_disable = False
magtag.peripherals.neopixels.brightness = 0.01
magtag.peripherals.neopixels[0] = GREEN

for i in range(0, len(DATA_SOURCES)):
    magtag.add_text(
        text_font="fonts/Arial-Bold-12.pcf",
        text_position=(10, 10 + 20*i),
        text_anchor_point=(0, 0)
    )
for i in range(0, len(DATA_SOURCES)):
    magtag.add_text(
        text_font="fonts/Arial-Bold-12.pcf",
        text_position=(.75*magtag.graphics.display.width, 10 + 20*i),
        text_anchor_point=(1, 0)
    )

# Time
magtag.add_text(
    text_font="fonts/Arial-Bold-12.pcf",
    text_position=(magtag.graphics.display.width, 10),
    text_anchor_point=(1, 0)
)

# Battery
magtag.add_text(
    text_font="fonts/Arial-Italic-12.bdf",
    text_position=(magtag.graphics.display.width, 100),
    text_anchor_point=(1, 0)
)

for i in range(1, 2*len(DATA_SOURCES)+2):
    magtag.set_text("...", index=i, auto_refresh=False)
magtag.refresh()


def update_board():
    response = magtag.network.fetch(TIME_URL)
    time_now = get_stuct_time_from_iso_str(response.text)

    def _to_min_wait_time(iso_date_string):
        t = get_stuct_time_from_iso_str(iso_date_string)
        diff_sec = time.mktime(t) - time.mktime(time_now)
        return round(diff_sec/60)

    i_text = 0
    for item in DATA_SOURCES:
        print()
        label = item["label"]
        source_url = item["url"]
        str_out = ""
        try:
            print(f"\nFetching {label}")
            response = magtag.network.fetch(source_url)
            if response.status_code == 200:
                data_js = response.json()
                for i in range(0, min(len(data_js["data"]), MAX_NUM_DEPARTURES)):
                    d = data_js["data"][i]["attributes"]["departure_time"]
                    if i > 0:
                        str_out += ", "
                    d_str = f"{_to_min_wait_time(d)}m" if isinstance(d, str) else "???"
                    str_out += str(d_str)
                if not len(data_js["data"]):
                    str_out += " - "

            else:
                str_out += "HTTP ERROR " + str(response.status_code)

        except Exception as e:
            print("OH NO failed to get ", label)
            print(str(e))
            str_out += "ERROR " + str(e)

        # print(f"\nSETTING {str_out}")
        magtag.set_text(label, index=i_text, auto_refresh=False)
        magtag.set_text(str_out, index=i_text+len(DATA_SOURCES), auto_refresh=False)
        i_text += 1

    # Time
    min_str = str(time_now.tm_min)
    while len(min_str) < 2:
        min_str = f"0{min_str}"
    magtag.set_text(f"{time_now.tm_hour}:{min_str}", index=2*len(DATA_SOURCES), auto_refresh=False)

    # Battery
    bat_v = magtag.peripherals.battery
    bat_percent = round((bat_v - 3.3) / (4.2 - 3.3) * 100.)
    magtag.set_text(f"{bat_percent}%", index=2*len(DATA_SOURCES)+1, auto_refresh=False)

    magtag.refresh()


# MAIN LOOP
refresh_count = 0
while refresh_count < MAX_REFRESH_BEFORE_SLEEP:
    update_board()
    refresh_count += 1
    if refresh_count >= MAX_REFRESH_BEFORE_SLEEP - 2:
        magtag.peripherals.neopixels[0] = YELLOW

    # Wait 30s, polling every 0.01 s
    for _ in range(0, 30/0.01):
        if magtag.peripherals.any_button_pressed:
            refresh_count = 0
            magtag.peripherals.neopixels[0] = GREEN
        time.sleep(0.01)  # Small delay to keep the loop stable and responsive
    # time.sleep(30)

# Update to show that sleeping...
magtag.set_text("SLEEPING;\npress any button for transit times", index=0, auto_refresh=False)
for i in range(1, 2*len(DATA_SOURCES)+2):
    magtag.set_text("", index=i, auto_refresh=False)
magtag.refresh()

# wait 2 seconds for display to complete updating before actually going into hibernation
time.sleep(2)
magtag.peripherals.neopixel_disable = True

magtag.peripherals.deinit()
pin_alarms = [alarm.pin.PinAlarm(pin=pin, value=False, pull=True) for pin in [board.D11, board.D12, board.D14, board.D15]]

alarm.exit_and_deep_sleep_until_alarms(*pin_alarms)
