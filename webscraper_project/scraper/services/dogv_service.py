from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_dogv(driver, url, keywords):
    results = []
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2)
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for index, iframe in enumerate(iframes):
            driver.switch_to.frame(iframe)
            try:
                WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "imc--llistat"))
                )
                sections = driver.find_elements(By.CLASS_NAME, "imc--llistat")
                for section in sections:
                    paragraphs = section.find_elements(By.CSS_SELECTOR, "p.card-text")
                    for p in paragraphs:
                        text = p.text.strip()
                        for keyword in keywords:
                            if keyword.lower() in text.lower():
                                results.append({
                                    "url_base": url,
                                    "title": text,
                                    "link": None,
                                    "pdf_url": None,
                                    "region": "Comunidad Valenciana",  # Región fija para DOGV
                                    "organism": "DOGV"  # Organismo fijo para DOGV
                                })
            except Exception:
                pass
            driver.switch_to.default_content()
    except Exception as e:
        print(f"⚠️ Error DOGV: {e}")
    return results