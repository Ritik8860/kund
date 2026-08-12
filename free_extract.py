"""
Free extraction of name/DOB/time/place from pasted text or screenshots.
No API calls, no cost. Uses Tesseract OCR (image) + regex/dateutil (parsing).

Tradeoff vs an LLM-based extractor: works well on clean, typed, reasonably
structured input (forms, typed notes, clear screenshots). Struggles more on
messy handwriting, heavily stylized fonts, or very unusual phrasing.
"""
import re
import pytesseract
from PIL import Image
from dateutil import parser as dateparser

TIME_PATTERN = re.compile(
    r'\b(\d{1,2})[:.](\d{2})\s*(am|pm|AM|PM)?\b'
)

DATE_PATTERNS = [
    r'\b\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}\b',   # 15/08/1995, 15-08-95
    r'\b\d{4}[/\-.]\d{1,2}[/\-.]\d{1,2}\b',      # 1995-08-15
    r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}\b',  # 15 Aug 1995
    r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{2,4}\b',  # Aug 15, 1995
]

NAME_LABEL_PATTERN = re.compile(r'(?:name)\s*[:\-]\s*([A-Za-z][A-Za-z .]{1,40})', re.IGNORECASE)
NAME_PHRASE_PATTERN = re.compile(r'(?:my name is|i am|i\'m)\s+([A-Za-z][A-Za-z .]{1,40})', re.IGNORECASE)
NAME_LEADWORD_PATTERN = re.compile(r'^\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s*,')
PLACE_LABEL_PATTERN = re.compile(
    r'(?:place of birth|birth\s*place|pob|place|city|born\s+(?:in|at))\s*[:\-]?\s*([A-Za-z][A-Za-z ,]{1,60})',
    re.IGNORECASE
)


def extract_text_from_image(image_bytes: bytes) -> str:
    """Free OCR using Tesseract."""
    from io import BytesIO
    img = Image.open(BytesIO(image_bytes))
    return pytesseract.image_to_string(img)


def _find_date(text: str):
    for pattern in DATE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                dt = dateparser.parse(match.group(0), dayfirst=True, fuzzy=True)
                return dt.strftime("%Y-%m-%d")
            except (ValueError, OverflowError):
                continue
    return None


def _find_time(text: str):
    match = TIME_PATTERN.search(text)
    if not match:
        return None
    hour, minute, meridiem = match.groups()
    hour = int(hour)
    if meridiem:
        if meridiem.lower() == "pm" and hour != 12:
            hour += 12
        elif meridiem.lower() == "am" and hour == 12:
            hour = 0
    if 0 <= hour <= 23:
        return f"{hour:02d}:{minute}"
    return None


def _find_name(text: str):
    for pattern in (NAME_LABEL_PATTERN, NAME_PHRASE_PATTERN):
        match = pattern.search(text)
        if match:
            name = re.split(r'\n', match.group(1))[0].strip().rstrip(",")
            # trim trailing words that are clearly not part of a name
            name = re.sub(r'\s+(dob|born|date|time).*$', '', name, flags=re.IGNORECASE).strip()
            if name:
                return name
    # fallback: "Ritik, born ..." style — leading capitalized word(s) before a comma
    match = NAME_LEADWORD_PATTERN.match(text.strip())
    if match:
        return match.group(1).strip()
    return None


PLACE_FALLBACK_PATTERN = re.compile(r'\bin\s+([A-Z][a-zA-Z]+(?:\s*,?\s*[A-Z][a-zA-Z]+){0,2})\s*$')


def _find_place(text: str):
    match = PLACE_LABEL_PATTERN.search(text)
    if match:
        place = match.group(1).strip().rstrip(".")
        place = re.split(r'\n|dob|tob|time|date', place, flags=re.IGNORECASE)[0].strip()
        if place:
            return place
    # fallback: trailing "... in <Place>" at end of a line/text (e.g. "born ... at 2:30pm in Delhi")
    for line in text.strip().splitlines():
        match = PLACE_FALLBACK_PATTERN.search(line.strip())
        if match:
            return match.group(1).strip()
    return None


def extract_details(raw_text: str) -> dict:
    """
    Best-effort free extraction. Returns dict with name/dob/tob/place,
    any of which may be None if not confidently found (user fills the gap manually).
    """
    return {
        "name": _find_name(raw_text),
        "dob": _find_date(raw_text),
        "tob": _find_time(raw_text),
        "place": _find_place(raw_text),
    }


if __name__ == "__main__":
    sample = """
    Name: Ritik Sharma
    DOB: 15 Aug 1995
    Time of Birth: 2:30 PM
    Place of Birth: Delhi
    """
    print(extract_details(sample))
