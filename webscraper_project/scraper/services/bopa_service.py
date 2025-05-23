from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_bopa(driver, url, keywords):
    results = []
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2)
        dls = driver.find_elements(By.TAG_NAME, "dl")
        for dl in dls:
            try:
                dt = dl.find_element(By.TAG_NAME, "dt")
                dd = dl.find_element(By.TAG_NAME, "dd")
                title = dt.text.strip()
                pdf_spans = dd.find_elements(By.CSS_SELECTOR, "span.pdfResultadoBopa")
                for span in pdf_spans:
                    links = span.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        href = link.get_attribute("href")
                        text = title  
                        if href and href.endswith(".pdf"):
                            for keyword in keywords:
                                if keyword.lower() in text.lower():
                                    results.append({
                                        "url_base": url,
                                        "title": text,
                                        "link": href,
                                        "pdf_url": href
                                    })
                                    break
            except Exception as e:
                print(f"⚠️ Error procesando un <dl>: {e}")
    except Exception as e:
        print(f"⚠️ Error BOPA: {e}")
    return results