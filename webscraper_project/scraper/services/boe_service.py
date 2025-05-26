from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_boe(driver, url, keywords):
    results = []
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "sumario"))
        )
        sumario = driver.find_element(By.CLASS_NAME, "sumario")
        dispo_items = sumario.find_elements(By.CSS_SELECTOR, "li.dispo")
        for item in dispo_items:
            try:
                p_elems = item.find_elements(By.TAG_NAME, "p")
                title = p_elems[0].text.strip() if p_elems else ""
                pdf_elem = item.find_element(By.CSS_SELECTOR, "li.puntoPDF a")
                pdf_url = pdf_elem.get_attribute("href")
                base_boe_url = "https://www.boe.es"
                full_pdf_url = base_boe_url + pdf_url if pdf_url.startswith("/") else pdf_url
                # Filtrado por keywords (corregido)
                if any(keyword.lower() in title.lower() for keyword in keywords):
                    results.append({
                        "url_base": url,
                        "title": title,
                        "link": url,
                        "pdf_url": full_pdf_url,
                        "region": "Nacional",  
                        "organism": "BOE"
                    })
            except Exception as e:
                print(f"⚠️ Error en item BOE: {e}")
                pass
    except Exception as e:
        print(f"⚠️ Error extrayendo PDF del BOE: {e}")
    return results