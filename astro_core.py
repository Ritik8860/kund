"""
Core sidereal (Vedic) astrology calculations.
Uses Swiss Ephemeris with Lahiri ayanamsa (the standard used by AstroSage, 
most Indian panchang software, and most professional Vedic astrologers).
"""
import swisseph as swe
from datetime import datetime
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
import pytz

swe.set_sid_mode(swe.SIDM_LAHIRI)

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

RASHIS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NAKSHATRA_SPAN = 360.0 / 27.0  # 13.3333...
RASHI_SPAN = 30.0
PADA_SPAN = NAKSHATRA_SPAN / 4.0


def geocode_place(place_name: str):
    """Resolve a place name to (lat, lon). Returns None if not found."""
    geolocator = Nominatim(user_agent="kundli_matcher_app")
    location = geolocator.geocode(place_name, timeout=10)
    if location is None:
        return None
    return location.latitude, location.longitude


def get_timezone(lat: float, lon: float) -> str:
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon)
    return tz_name or "Asia/Kolkata"


def compute_moon_position(dob: str, tob: str, place: str):
    """
    dob: 'YYYY-MM-DD'
    tob: 'HH:MM' (24hr, local time at place of birth)
    place: free text place name, e.g. 'Jaipur, Rajasthan, India'

    Returns dict with rashi, nakshatra, pada, moon_longitude, and resolved location info.
    """
    coords = geocode_place(place)
    if coords is None:
        raise ValueError(f"Could not resolve location: '{place}'. Try a more specific place name.")
    lat, lon = coords

    tz_name = get_timezone(lat, lon)
    tz = pytz.timezone(tz_name)

    naive_dt = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
    local_dt = tz.localize(naive_dt)
    utc_dt = local_dt.astimezone(pytz.utc)

    jd_ut = swe.julday(
        utc_dt.year, utc_dt.month, utc_dt.day,
        utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    )

    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    moon_pos, _ = swe.calc_ut(jd_ut, swe.MOON, flags)
    moon_longitude = moon_pos[0] % 360.0

    nakshatra_index = int(moon_longitude // NAKSHATRA_SPAN)
    rashi_index = int(moon_longitude // RASHI_SPAN)
    pada = int((moon_longitude % NAKSHATRA_SPAN) // PADA_SPAN) + 1

    return {
        "moon_longitude": moon_longitude,
        "nakshatra": NAKSHATRAS[nakshatra_index],
        "nakshatra_index": nakshatra_index,
        "rashi": RASHIS[rashi_index],
        "rashi_index": rashi_index,
        "pada": pada,
        "resolved_place": place,
        "lat": lat,
        "lon": lon,
        "timezone": tz_name,
    }


if __name__ == "__main__":
    # quick sanity test
    result = compute_moon_position("1995-08-15", "14:30", "New Delhi, India")
    print(result)
