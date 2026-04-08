"""
Islamic Calendar App
Converts Gregorian dates to Hijri (Islamic lunar) dates,
displays the current month's calendar, and lists key Islamic events.

No external dependencies — standard library only.
"""

import math
from datetime import date, timedelta


# ── Hijri month names ──────────────────────────────────────────────────────────

HIJRI_MONTHS = [
    "Muharram", "Safar", "Rabi' al-Awwal", "Rabi' al-Thani",
    "Jumada al-Awwal", "Jumada al-Thani", "Rajab", "Sha'ban",
    "Ramadan", "Shawwal", "Dhu al-Qi'dah", "Dhu al-Hijjah",
]

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# ── Key Islamic events (Hijri month, day, name) ────────────────────────────────

ISLAMIC_EVENTS = {
    (1, 1):   "Islamic New Year (Ra's al-Sana)",
    (1, 10):  "Day of Ashura",
    (3, 12):  "Mawlid al-Nabi (Prophet's Birthday)",
    (7, 27):  "Isra' and Mi'raj",
    (8, 15):  "Laylat al-Bara'at (Mid-Sha'ban)",
    (9, 1):   "Start of Ramadan",
    (9, 27):  "Laylat al-Qadr (Night of Power)",
    (10, 1):  "Eid al-Fitr",
    (12, 8):  "Start of Hajj",
    (12, 9):  "Day of Arafah",
    (12, 10): "Eid al-Adha",
}


# ── Core conversion algorithm (Kuwaiti algorithm) ─────────────────────────────

def gregorian_to_hijri(year: int, month: int, day: int) -> tuple:
    """Convert a Gregorian date to a Hijri (Islamic) date."""
    if month < 3:
        year -= 1
        month += 12

    A = math.floor(year / 100)
    B = 2 - A + math.floor(A / 4)
    jd = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + B - 1524

    l = jd - 1948440 + 10632
    n = math.floor((l - 1) / 10631)
    l = l - 10631 * n + 354
    j = (math.floor((10985 - l) / 5316)) * (math.floor((50 * l) / 17719)) + \
        (math.floor(l / 5670)) * (math.floor((43 * l) / 15238))
    l = l - (math.floor((30 - j) / 15)) * (math.floor((17719 * j) / 50)) - \
        (math.floor(j / 16)) * (math.floor((15238 * j) / 43)) + 29
    h_month = math.floor((24 * l) / 709)
    h_day = l - math.floor((709 * h_month) / 24)
    h_year = 30 * n + j - 30

    return int(h_year), int(h_month), int(h_day)


def hijri_to_gregorian(h_year: int, h_month: int, h_day: int) -> date:
    """Convert a Hijri date back to a Gregorian date (approximate)."""
    n = h_day + math.ceil(29.5001 * (h_month - 1)) + \
        (h_year - 1) * 354 + math.floor((3 + (11 * h_year)) / 30) + 1948440 - 385

    if n <= 2299160:
        a = n
    else:
        x = math.floor((n - 1867216.25) / 36524.25)
        a = n + 1 + x - math.floor(x / 4)

    b = a + 1524
    c = math.floor((b - 122.1) / 365.25)
    d = math.floor(365.25 * c)
    e = math.floor((b - d) / 30.6001)

    day   = int(b - d - math.floor(30.6001 * e))
    month = int(e - 1) if e < 14 else int(e - 13)
    year  = int(c - 4716) if month > 2 else int(c - 4715)

    return date(year, month, day)


# ── Calendar display helpers ───────────────────────────────────────────────────

def days_in_hijri_month(h_year: int, h_month: int) -> int:
    """Approximate days in a Hijri month (29 or 30)."""
    first = hijri_to_gregorian(h_year, h_month, 1)
    next_m = h_month + 1 if h_month < 12 else 1
    next_y = h_year if h_month < 12 else h_year + 1
    first_next = hijri_to_gregorian(next_y, next_m, 1)
    return (first_next - first).days


def get_event(h_month: int, h_day: int):
    return ISLAMIC_EVENTS.get((h_month, h_day))


def print_month_calendar(h_year: int, h_month: int):
    """Print a formatted calendar for a Hijri month."""
    month_name = HIJRI_MONTHS[h_month - 1]
    title = f"  {month_name} {h_year} AH"
    print("\n" + "=" * 52)
    print(title.center(52))
    print("=" * 52)

    print("  " + "  ".join(WEEKDAYS))
    print("  " + "-" * 48)

    first_greg = hijri_to_gregorian(h_year, h_month, 1)
    total_days = days_in_hijri_month(h_year, h_month)
    start_weekday = first_greg.weekday()

    today_h = gregorian_to_hijri(*date.today().timetuple()[:3])

    row = "  " + "     " * start_weekday
    for day in range(1, total_days + 1):
        is_today = (h_year, h_month, day) == today_h
        has_event = (h_month, day) in ISLAMIC_EVENTS
        cell = f"[{day:2d}]" if is_today else f" {day:2d}* " if has_event else f"  {day:2d} "
        row += cell
        col = (start_weekday + day - 1) % 7
        if col == 6:
            print(row)
            row = "  "

    if row.strip():
        print(row)

    print()
    print("  [ ] = today   * = Islamic event")
    print()

    print("  Events this month:")
    found = False
    for day in range(1, total_days + 1):
        ev = get_event(h_month, day)
        if ev:
            greg = first_greg + timedelta(days=day - 1)
            print(f"    {day:2d} {month_name[:3]} ({greg.strftime('%d %b %Y')}): {ev}")
            found = True
    if not found:
        print("    None")
    print()


def print_today():
    """Print today's Gregorian and Hijri dates."""
    today = date.today()
    hy, hm, hd = gregorian_to_hijri(today.year, today.month, today.day)
    hm_name = HIJRI_MONTHS[hm - 1]
    print("\n" + "=" * 52)
    print("  Today's Date".center(52))
    print("=" * 52)
    print(f"  Gregorian : {today.strftime('%A, %d %B %Y')}")
    print(f"  Hijri     : {hd} {hm_name} {hy} AH")
    ev = get_event(hm, hd)
    if ev:
        print(f"  Event     : {ev}")
    print()


def convert_date(year: int, month: int, day: int):
    """Convert and display any Gregorian date to Hijri."""
    g = date(year, month, day)
    hy, hm, hd = gregorian_to_hijri(year, month, day)
    hm_name = HIJRI_MONTHS[hm - 1]
    print(f"\n  {g.strftime('%d %B %Y')}  →  {hd} {hm_name} {hy} AH")
    ev = get_event(hm, hd)
    if ev:
        print(f"  Event: {ev}")
    print()


def print_upcoming_events(n: int = 5):
    """Print the next n upcoming Islamic events."""
    today = date.today()
    hy, hm, hd = gregorian_to_hijri(today.year, today.month, today.day)

    upcoming = []
    for year_offset in range(2):
        yr = hy + year_offset
        for (m, d), name in sorted(ISLAMIC_EVENTS.items()):
            try:
                greg = hijri_to_gregorian(yr, m, d)
                if greg >= today:
                    upcoming.append((greg, d, HIJRI_MONTHS[m - 1], yr, name))
            except Exception:
                pass

    upcoming.sort()
    print("  Upcoming Islamic events:")
    print("  " + "-" * 48)
    for greg, hday, hmonth, hyear, name in upcoming[:n]:
        delta = (greg - today).days
        soon = f"in {delta} day{'s' if delta != 1 else ''}" if delta > 0 else "today"
        print(f"  {hday:2d} {hmonth:<18} {hyear} AH  ({greg.strftime('%d %b %Y')}, {soon})")
        print(f"     → {name}")
    print()


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 52)
    print("      Islamic (Hijri) Calendar App".center(52))
    print("=" * 52)

    print_today()

    today = date.today()
    hy, hm, hd = gregorian_to_hijri(today.year, today.month, today.day)
    print_month_calendar(hy, hm)

    print_upcoming_events(n=5)

    print("  Date conversion examples:")
    print("  " + "-" * 48)
    convert_date(2025, 3, 30)
    convert_date(2025, 6, 6)
    convert_date(2024, 9, 16)


if __name__ == "__main__":
    main()
