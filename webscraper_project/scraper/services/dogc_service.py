from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin

def scrape_dogc(driver, url, keywords):
    results = []
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "destacat_text_cont"))
        )
        items = driver.find_elements(By.CLASS_NAME, "destacat_text_cont")
        for item in items:
            try:
                title_elem = item.find_element(By.TAG_NAME, "a")
                title = title_elem.text.strip()
                link = urljoin(url, title_elem.get_attribute("href"))

                pdf_elem = item.find_element(By.CSS_SELECTOR, "div.download a")
                pdf_url = pdf_elem.get_attribute("href")
                
                if any(keyword.lower() in title.lower() for keyword in keywords):
                    results.append({
                        "url_base": url,
                        "title": title,
                        "link": link,
                        "pdf_url": pdf_url,
                        "region": "Cataluña",
                        "organism": "DOGC"
                    })
            except Exception:
                pass
    except Exception as e:
        print(f"⚠️ Error extrayendo PDF del DOGC: {e}")
    return results