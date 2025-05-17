from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from urllib.parse import urljoin
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

def get_spain_holidays(year):
    _, good_friday, _ = get_easter_dates(year)
    return {
        (1, 1),  
        (1, 6),  
        (good_friday.month, good_friday.day),  
        (5, 1),
        (8, 15),  
        (10, 12),  
        (11, 1), 
        (12, 6),  
        (12, 8),  
        (12, 25),  
    }


# Public holidays in Catalonia
def get_catalonia_holidays(year):
    spain = get_spain_holidays(year)
    _, _, easter_monday = get_easter_dates(year)
    return spain | {
        (easter_monday.month, easter_monday.day),  
        (6, 24), 
        (9, 11),  
        (12, 26),  
    }


# Public holidays in Madrid
def get_madrid_holidays(year):
    spain = get_spain_holidays(year)
    maundy_thursday, _, _ = get_easter_dates(year)
    return spain | {
        (maundy_thursday.month, maundy_thursday.day),
        (5, 2),  
        (7, 25),
    }

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


def get_bocm_url():
    base_bocm_number = 116  
    base_date = datetime(2025, 5, 16)

    today = get_previous_business_day(datetime.today(), "madrid")
    
    days_difference = 0
    date = base_date
    while date < today:
        date += timedelta(days=1)
        if date.weekday() < 5 and (date.month, date.day) not in get_holidays(date.year, "madrid"):
            days_difference += 1

    num_bocm = base_bocm_number + days_difference
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
    days_difference = 0
    date = base_date
    while date < today:
        date += timedelta(days=1)
        if date.weekday() < 5 and (date.month, date.day) not in get_holidays(date.year, "catalonia"):
            days_difference += 1
    num_dogc = base_dogc_number + days_difference
    return f"https://dogc.gencat.cat/es/sumari-del-dogc/?numDOGC={num_dogc}"

def get_bopdiba_url():
    base_bopdiba_number = 221
    date = get_previous_business_day(datetime.today(), "catalonia")
    days_difference = 0
    base_date = datetime(2025, 5, 16)

    while base_date < date:
        base_date += timedelta(days=1)
        if base_date.weekday() < 5 and (base_date.month, base_date.day) not in get_holidays(base_date.year, "catalonia"):
            days_difference += 1

    num_bopdiba = base_bopdiba_number + days_difference
    return f"https://bop.diba.cat/butlleti-del-dia?bopb_dia%5BtipologiaAnunciant%5D={num_bopdiba}"

def get_boe_url():
    today = datetime.today()
    holidays = get_catalonia_holidays(today.year)

    if today.weekday() < 6 and (today.month, today.day) not in holidays:
        date = today  
    else:
        date = get_previous_business_day(today,"spain")  
    
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

            if "boe.es" in url:
                try:
                    WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "li.puntoPDF a"))
                    )
                    li_pdf = driver.find_element(By.CSS_SELECTOR, "li.puntoPDF a")
                    pdf_url = li_pdf.get_attribute("href")
                    base_boe_url = "https://www.boe.es"
                    full_pdf_url = base_boe_url + pdf_url if pdf_url.startswith("/") else pdf_url
                    title = li_pdf.text.strip()
                    scraped_data.append({
                        "url_base": url,
                        "title": title,
                        "link": url,
                        "pdf_url": full_pdf_url
                    })
                except Exception as e:
                    print(f"⚠️ Error extrayendo PDF del BOE: {e}")
            
            
            if "sede.asturias.es" in url:
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.pdfResultadoBopa a"))
                    )
                    pdf_links = driver.find_elements(By.CSS_SELECTOR, "span.pdfResultadoBopa a")
                    for link in pdf_links:
                        href = link.get_attribute("href")
                        # if href.endswith(".pdf"):
                        #     scraped_data.append({
                        #         "url": url,
                        #         "pdf_url": href
                        #     })
                except Exception as e:
                    print(f"⚠️ Error extrayendo PDFs del BOPA: {e}")
            
            if "dogc.gencat.cat" in url:
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "div.download a"))
                )
                download_divs = driver.find_elements(By.CSS_SELECTOR, "div.download")
                for div_download in download_divs:
                    try:
                        a_tag_pdf = div_download.find_element(By.TAG_NAME, "a")
                        pdf_url = a_tag_pdf.get_attribute("href")
                        if pdf_url.startswith("/"):
                            pdf_url = urljoin(url, pdf_url)
                    except Exception:
                        pass

         
            if "bop.diba.cat" in url:
                try:
                    WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "a.stretched-link.text-reset.text-decoration-none"))
                    )
                    main_links = driver.find_elements(By.CSS_SELECTOR, "a.stretched-link.text-reset.text-decoration-none")
                    for main_link in main_links:
                        sub_url = main_link.get_attribute("href")
                        title = main_link.text.strip()
                        driver.get(sub_url)
                        pdf_url = None
                        try:
                            WebDriverWait(driver, 10).until(
                                EC.visibility_of_element_located((By.CSS_SELECTOR, "li.list-group-item.bg-transparent a"))
                            )
                            pdf_links = driver.find_elements(By.CSS_SELECTOR, "li.list-group-item.bg-transparent a")
                            for pdf_link in pdf_links:
                                pdf_href = pdf_link.get_attribute("href")
                                if "descarrega-pdf" in pdf_href:
                                    pdf_url = urljoin(sub_url, pdf_href)
                                    break
                        except Exception as e:
                            print(f"⚠️ No se pudo extraer PDF en la subpágina {sub_url}: {e}")
                        finally:
                            driver.back()
                        scraped_data.append({
                            "url_base": url,
                            "title": title,
                            "link": sub_url,
                            "pdf_url": pdf_url
                        })
                except Exception as e:
                    print(f"⚠️ Error extrayendo PDFs del BOP DIBA: {e}")
                continue
                
            if "bocm.es" in url:
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.file a"))
                    )
                    pdf_links = driver.find_elements(By.CSS_SELECTOR, "span.file a")
                    for link in pdf_links:
                        href = link.get_attribute("href")
                except Exception as e:
                    print(f"⚠️ Error extrayendo PDFs del BOCM: {e}")


            if "dogv.gva.es" in url:
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
                    text = link.text.strip().lower()
                    href = link.get_attribute("href")
                    for keyword in keywords:
                        if keyword.lower() in text:
                            data = {
                                "url": url,
                                "keyword": keyword,
                                "text": link.text.strip(),
                                "link": href
                            }
                            if href.lower().endswith(".pdf"):
                                data["pdf_url"] = href
                            scraped_data.append(data)

    except Exception as e:
        print("❌ Error processing URLs:", e)
    finally:
        driver.quit()

    print("✅ Scraped Data:", scraped_data)
    return scraped_data

urls = ["https://dogv.gva.es/es/inici", get_boe_url(), get_dogc_url(), "https://sede.asturias.es/ultimos-boletines?p_r_p_summaryLastBopa=true", *get_bocm_url(), get_bopdiba_url()]
keywords = ["subvención", "subvenciones", "subvenció", "licitació", "licitación", "contrato", "contracte", "contractació", "contratos"]

scraped_data = scrape_multiple_websites(urls, keywords)