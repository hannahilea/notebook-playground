# Sunrise / sunset calculations to support Daylight Clock
# https://hannahilea.com/blog/daylight-clock
#
# Code is ported from Rust and lightly (very lightly!) adapted from cceckman's
# https://cceckman.com/writing/aclock, specifically the following script:
# https://github.com/cceckman/aclock/blob/5547d8490151eafa77f33dc697cbb58ea0035c70/server/src/riseset.rs#L60
#
#
# From that script:
# > Equations are derived from two resources from
# > [NOAA](https://gml.noaa.gov/grad/solcalc/calcdetails.html).
# > I started with [this equations sheet](https://gml.noaa.gov/grad/solcalc/solareqns.PDF),
# > but got results inconsistent with other sources.
# > The spreadsheets on [this page](https://gml.noaa.gov/grad/solcalc/calcdetails.html)
# > align with other sources.
#
# > Spreadsheet computation:
# > Sunrise is (X2 * 1440 - W2 * 4) / 1440 (fraction of a day)
# > Sunset is (X2 * 1440 + W2 * 4) / 1440
# > W2: HA of sunrise (in degrees)
# > X2: Solar noon:
# >     720 - 4 * longitude + tzoffset - V2
# > V2: equation of time

from datetime import datetime, timedelta
from math import pi, cos, sin, radians, tan, acos, degrees
from zoneinfo import ZoneInfo


# TODO: Update these values for the location the clock will be hung!
# Current default is for Boston, MA, USA
LATITUDE = 42.3588336
LONGITUDE = -71.0578303
TIME_ZONE = ZoneInfo("America/New_York")


def min_past_midnight_utc_to_datetime_utc(date, minutes_past_midnight):
    offset_midnight_utc = timedelta(minutes=minutes_past_midnight)
    dt = datetime.combine(date, datetime.min.time(), ZoneInfo("UTC")) + offset_midnight_utc
    return dt


# /// Compute sun rise/noon/set times in hours-past-midnight UTC
def riseset_in_noaa_min_utc(date, latitude, longitude, tz):
    # // The NOAA equations produce rise and set times in minutes past UTC midnight.
    # // We'll complete the NOAA equations then convert back to DateTime.

    # // START OF NOAA EQUATIONS
    leap_year = date.year % 4 == 0 and date.year % 100 != 0
    days = 366 if leap_year else 365

    # // Fractional year in radians. We don't include a fractional day from the hour.
    ordinal_day = date.timetuple().tm_yday  # NOT date.toordinal() , which is different from rust!!

    gamma = (2.0 * pi) * (ordinal_day) / days

    # // equation of time, relating mean solar time and true solar time
    eqtime = 229.18 * (0.000075 + 0.001868 * cos(gamma)
            - 0.032077 * sin(gamma)
            - 0.014615 * cos(2.0 * gamma)
            - 0.040849 * sin(2.0 * gamma))

    # // solar declination angle (in radians):
    decl = 0.006918 - 0.399912 * cos(gamma) + 0.070257 * sin(gamma)
    - 0.006758 * cos(2.0 * gamma)
    + 0.000907 * sin(2.0 * gamma)
    - 0.002697 * cos(3.0 * gamma)
    + 0.00148 * sin(3.0 * gamma)

    # // The hour angle of the sunrise and sunset is:
    zenith = radians(90.833)
    lat = radians(latitude)

    # // We diverge from the PDF here and use the spreadsheet's form:
    # // sunrise and sunset are computed as a difference from solar noon.
    ha = acos(cos(zenith) / (cos(lat) * cos(decl)) - tan(lat) * tan(decl))

    snoon = 720.0 - 4.0 * longitude - eqtime
    sunrise = snoon - 4.0 * degrees(ha)
    sunset = snoon + 4.0 * degrees(ha)
    # // END OF NOAA EQUATIONS

    # print("\nha:", ha,
    #       "\nzenith:", zenith,
    #       "\nlat:", lat,
    #       "\nsnoon:", snoon,
    #       "\nsunrise:", sunrise,
    #       "\nsunset:", sunset,
    #       "\ndecl:", decl,
    #       "\nordinal_day:", ordinal_day,
    #       "\ngamma:", gamma,
    #       "\neqtime:", eqtime,
    #       )

    # Convert min past midnight to hours
    return (min_past_midnight_utc_to_datetime_utc(date.date(), sunrise, tz),
            min_past_midnight_utc_to_datetime_utc(date.date(), snoon, tz),
            min_past_midnight_utc_to_datetime_utc(date.date(), sunset, tz))


# /// Compute a range of rise and set times.
# /// Usees the local timezone and the current time.
# ///
# /// This is mostly useful for debugging.
def ephemerides(latitude=LATITUDE, longitude=LONGITUDE, tz=TIME_ZONE):
    day = datetime.now(ZoneInfo("UTC"))
    out = ""
    for day_offset in range(-1, 0):
        date = day + timedelta(days=day_offset)
        (sunrise, snoon, sunset) = riseset_in_noaa_min_utc(date, latitude,
                                                           longitude, tz)
        # str = f"{date.date()}: {sunrise} / {snoon} / {sunset}\n"
        str = f"DATE: {date.date()} \n- RISE: {sunrise} \n- SET: {sunset}\n"
        print(str)
        out += str
    return out
