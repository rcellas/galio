from datetime import datetime, timedelta

def get_easter_dates(year):
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    easter_sunday = datetime(year, month, day)
    maundy_thursday = easter_sunday - timedelta(days=3)
    good_friday = easter_sunday - timedelta(days=2)
    easter_monday = easter_sunday + timedelta(days=1)
    return maundy_thursday, good_friday, easter_monday

def get_spain_holidays(year):
    _, good_friday, _ = get_easter_dates(year)
    return {
        (1, 1), (1, 6), (good_friday.month, good_friday.day), (5, 1),
        (8, 15), (10, 12), (11, 1), (12, 6), (12, 8), (12, 25)
    }

def get_catalonia_holidays(year):
    spain = get_spain_holidays(year)
    _, _, easter_monday = get_easter_dates(year)
    return spain | {(easter_monday.month, easter_monday.day), (6, 24), (9, 11), (12, 26)}

def get_madrid_holidays(year):
    spain = get_spain_holidays(year)
    maundy_thursday, _, _ = get_easter_dates(year)
    return spain | {(maundy_thursday.month, maundy_thursday.day), (5, 2), (7, 25)}

def get_holidays(year, region):
    if region == "madrid":
        return get_madrid_holidays(year)
    elif region == "catalonia":
        return get_catalonia_holidays(year)
    elif region == "spain":
        return get_spain_holidays(year)
    else:
        raise ValueError("Región no reconocida. Usa 'catalonia', 'madrid' o 'spain'.")

def get_previous_business_day(date, region):
    holidays = get_holidays(date.year, region)
    while date.weekday() >= 5 or (date.month, date.day) in holidays:
        date -= timedelta(days=1)
    return date

def get_previous_saturday_business_day(date, region):
    holidays = get_holidays(date.year, region)
    while date.weekday() == 6 or (date.month, date.day) in holidays: 
        date -= timedelta(days=1)
    return date