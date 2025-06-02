from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime, timedelta
from scraper.models import ScrapedItem

from scraper.services.boe_service import scrape_boe
from scraper.services.dogc_service import scrape_dogc
from scraper.services.dogv_service import scrape_dogv
from scraper.services.bocm_service import scrape_bocm
from scraper.services.bopdiba_service import scrape_bopdiba
from scraper.services.bopa_service import scrape_bopa
from scraper.services.holidays import get_previous_business_day, get_holidays, get_previous_saturday_business_day

def get_bocm_url():
    base_bocm_number = 121
    base_date = datetime(2025, 5, 22)
    today = get_previous_saturday_business_day(datetime.today(), "madrid")
    days_difference = 0
    date = base_date
    while date < today:
        date += timedelta(days=1)
        if date.weekday() < 7 and (date.month, date.day) not in get_holidays(date.year, "madrid"):
            days_difference += 1
    num_bocm = base_bocm_number + days_difference - 2
    formatted_date = today.strftime('%Y%m%d')
    base_url = f"https://www.bocm.es/boletin-completo/bocm-{formatted_date}/{num_bocm}/"
    return [
        base_url + "i.-comunidad-de-madrid/c%29-otras-disposiciones",
        base_url + "i.-comunidad-de-madrid/d%29-anuncios"
    ]

def get_dogc_url():
    base_dogc_number = 9414
    base_date = datetime(2025, 5, 16)
    today = datetime.today()
    holidays = get_holidays(today.year, "catalonia")
  
    while today.weekday() >= 5 or (today.month, today.day) in holidays:
        today -= timedelta(days=1)
    days_difference = 0
    date = base_date
    while date < today:
        date += timedelta(days=1)
        if date.weekday() < 5 and (date.month, date.day) not in get_holidays(date.year, "catalonia"):
            days_difference += 1
    num_dogc = base_dogc_number + days_difference - 1
    return f"https://dogc.gencat.cat/es/sumari-del-dogc/?numDOGC={num_dogc}"

def get_boe_url():
    today = datetime.today()
    holidays = get_holidays(today.year, "spain")
    if today.weekday() <= 5 and (today.month, today.day) not in holidays:
        date = today
    else:
        date = get_previous_saturday_business_day(today, "spain")
    return f"https://www.boe.es/boe/dias/{date.year}/{date.month:02d}/{date.day:02d}/"

def get_urls():
    """Función para obtener las URLs dinámicamente"""
    return [
        "https://dogv.gva.es/es/inici",
        get_boe_url(),
        get_dogc_url(),
        "https://sede.asturias.es/ultimos-boletines?p_r_p_summaryLastBopa=true",
        *get_bocm_url(),
        "https://bop.diba.cat/butlleti-del-dia?bopb_dia%5BtipologiaAnunciant%5D=221"
    ]

def get_keywords():
    """Función para obtener las keywords"""
    return ["subvención", "subvenciones", "subvenció", "licitació", "licitación", "contrato", "contracte", "contractació", "contratos"]

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
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(5)

            if "boe.es" in url:
                scraped_data.extend(scrape_boe(driver, url, keywords))
                continue
            if "dogc.gencat.cat" in url:
                scraped_data.extend(scrape_dogc(driver, url, keywords))
                continue
            if "dogv.gva.es" in url:
                scraped_data.extend(scrape_dogv(driver, url, keywords))
                continue
            if "sede.asturias.es" in url:
                scraped_data.extend(scrape_bopa(driver, url, keywords))
                continue
            if "bocm.es" in url:
                scraped_data.extend(scrape_bocm(driver, url, keywords))
                continue
            if "bop.diba.cat" in url:
                scraped_data.extend(scrape_bopdiba(driver, url, keywords))
                continue

            class_mapping = {
                "boe.es": "sumario",
                "dogc.gencat.cat": "llistat_destacat_text_cont",
                "bop.diba.cat": "div.col-md-6.col-lg-8.py-5.px-lg-5.bg-light",
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
                links = section.find_elements(By.TAG_NAME, "a")
                for link in links:
                    text = link.text.strip()
                    href = link.get_attribute("href")
                    pdf_url = href if href and href.lower().endswith(".pdf") else None
                    for keyword in keywords:
                        if keyword.lower() in text.lower():
                            scraped_data.append({
                                "url_base": url,
                                "title": text,
                                "link": href,
                                "pdf_url": pdf_url
                            })

    except Exception as e:
        print("❌ Error processing URLs:", e)
    finally:
        driver.quit()

    print("✅ Scraped Data:", scraped_data)
    return scraped_data

def save_scraped_data(scraped_data):
    """Función para guardar los datos scrapeados en la base de datos"""
    for item in scraped_data:
        try:
            # Determinar región y organismo basado en la URL
            url_base = item.get("url_base", "")
            
            if "boe.es" in url_base:
                region = "Nacional"
                organism = "BOE"
            elif "bocm.es" in url_base:
                region = "Madrid"
                organism = "BOCM"
            elif "dogc.gencat.cat" in url_base:
                region = "Cataluña"
                organism = "DOGC"
            elif "dogv.gva.es" in url_base:
                region = "Valencia"
                organism = "DOGV"
            elif "sede.asturias.es" in url_base:
                region = "Asturias"
                organism = "BOPA"
            elif "bop.diba.cat" in url_base:
                region = "Cataluña"
                organism = "BOPDIBA"
            else:
                region = "Nacional"
                organism = "BOE"

            obj = ScrapedItem.objects.create(
                url_base=item.get("url_base"),
                title=item.get("title"),
                link=item.get("link"),
                pdf_url=item.get("pdf_url"),
                region=region,
                organism=organism
            )
            print("Guardado:", obj)
        except Exception as e:
            print("❌ Error guardando:", e)

urls = get_urls()
keywords = get_keywords()


if __name__ == "__main__":
    scraped_data = scrape_multiple_websites(urls, keywords)
    save_scraped_data(scraped_data)