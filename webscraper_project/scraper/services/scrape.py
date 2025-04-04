from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time
from datetime import datetime, timedelta

# Function to calculate Good Friday and Easter Monday
def get_easter_dates(year):
    """Calculates the date of Good Friday and Easter Monday for a given year."""
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
    return maundy_thursday,good_friday, easter_monday

# Public holidays in Catalonia (reference year 2025)
def get_catalonia_holidays(year):
    _,good_friday, easter_monday = get_easter_dates(year)
    return {
        (1, 1),  # New Year
        (1, 6),  # Epiphany
        (good_friday.month, good_friday.day),  # Good Friday
        (easter_monday.month, easter_monday.day),  # Easter Monday
        (5, 1),  # Labor Day
        (6, 24), # St. John
        (8, 15), # Assumption
        (9, 11), # Catalonia Day
        (10, 12), # Spanish National Day
        (11, 1),  # All Saints' Day
        (12, 6),  # Constitution Day
        (12, 8),  # Immaculate Conception
        (12, 25), # Christmas
        (12, 26)  # St. Stephen
    }

# Public holidays in Madrid
def get_madrid_holidays(year):
    maundy_thursday,good_friday,_ = get_easter_dates(year)
    return {
        (1, 1),  # New Year
        (1, 6),  # Epiphany
        (maundy_thursday.month, maundy_thursday.day), # Maundy Thursday
        (good_friday.month, good_friday.day), # Good Friday
        (5, 1),  # Labor Day
        (5, 2),  # Community of Madrid Day
        (7, 25), # Santiago Apóstol
        (8, 15), # Assumption
        (11, 1),  # All Saints' Day
        (12, 6),  # Constitution Day
        (12, 8),  # Immaculate Conception
        (12, 25)  # Christmas
    }

def get_next_business_day(date):
    holidays = get_catalonia_holidays(date.year)
    while True:
        date += timedelta(days=1)
        if date.weekday() < 5 and (date.month, date.day) not in holidays:
            return date

def get_bocm_url():
    base_bocm_number = 72  # Número de boletín de referencia
    base_date = datetime(2025, 3, 26)  # Fecha de referencia
    today = datetime.today()
    days_difference = 0
    date = base_date
    while date < today:
        date += timedelta(days=1)
        if date.weekday() < 5 and (date.month, date.day) not in get_madrid_holidays(date.year):
            days_difference += 1
    num_bocm = base_bocm_number + days_difference
    formatted_date = today.strftime('%Y%m%d')
    base_url = f"https://www.bocm.es/boletin-completo/bocm-{formatted_date}/{num_bocm}/"
    return [
        base_url + "i.-comunidad-de-madrid/c%29-otras-disposiciones",
        base_url + "i.-comunidad-de-madrid/d%29-anuncios"
    ]


def get_dogc_url():
    base_dogc_number = 9376  # Reference DOGC number for 2025-03-25
    base_date = datetime(2025, 3, 24)
    today = datetime.today()
    days_difference = 0
    date = base_date
    while date < today:
        date += timedelta(days=1)
        if date.weekday() < 5 and (date.month, date.day) not in get_catalonia_holidays(date.year):
            days_difference += 1

    num_dogc = base_dogc_number + days_difference
    return f"https://dogc.gencat.cat/es/sumari-del-dogc/?numDOGC={num_dogc}"


def get_boe_url():
    today = datetime.today()
    holidays = get_catalonia_holidays(today.year)

    if today.weekday() < 5 and (today.month, today.day) not in holidays:
        date = today  # Si hoy es hábil, usa la fecha actual
    else:
        date = get_next_business_day(today)  # Si no, busca el próximo día hábil
    
    return f"https://www.boe.es/boe/dias/{date.year}/{date.month:02d}/{date.day:02d}/"

def scrape_multiple_websites(urls, keywords):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    service = Service("/usr/local/bin/geckodriver")
    driver = webdriver.Firefox(service=service, options=options)

    scraped_data = []

    try:
        for url in urls:
            print(f"🔎 Scraping URL: {url}")
            driver.get(url)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            time.sleep(5)

            if "boe.es" in url or "dogv.gva.es" in url or "sede.asturias.es" in url or "bocm.es" in url:
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                if iframes:
                    print(f"🔄 Se encontraron {len(iframes)} iframes en {url}. Cambiando al primero.")
                    driver.switch_to.frame(iframes[0])
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
            
            if "sede.asturias.es" in url:
                try:
                    WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.ID, "bopa-boletin"))
                    )
                    sections = driver.find_elements(By.ID, "bopa-boletin")
                except:
                    print(f"⚠️ No se encontró el ID 'bopa-boletin' en {url}")
                    continue
            else:
                class_mapping = {
                    "boe.es": "sumario",
                    "dogc.gencat.cat": "llistat_destacat_text_cont",
                    "dogv.gva.es": "imc--llistat",
                    "bocm.es": "view-grouping"
                }
                class_name = next((class_mapping[key] for key in class_mapping if key in url), "section")
                try:
                    WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.CLASS_NAME, class_name))
                    )
                    sections = driver.find_elements(By.CLASS_NAME, class_name)
                except:
                    print(f"⚠️ No se encontró la clase {class_name} en {url}")
                    continue

            for section in sections:
                lines = section.text.strip().split("\n")
                for line in lines:
                    if any(kw.lower() in line.lower() for kw in keywords):
                        scraped_data.append({"url": url, "title": line.strip()})

    except Exception as e:
        print("❌ Error processing URLs:", e)
    finally:
        driver.quit()

    print("✅ Scraped Data:", scraped_data)
    return scraped_data

urls = ["https://dogv.gva.es/es/inici", get_boe_url(), get_dogc_url(), "https://sede.asturias.es/ultimos-boletines?p_r_p_summaryLastBopa=true", *get_bocm_url()]
keywords = ["subvención", "subvenciones", "subvenció", "licitació", "licitación", "contrato", "contracte", "contractació", "contratos"]

scraped_data = scrape_multiple_websites(urls, keywords)