from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_bopa(driver, url, keywords):
    results = []
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2)
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for index, iframe in enumerate(iframes):
            driver.switch_to.frame(iframe)
            try:
                WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "span.pdfResultadoBopa"))
                )
                sections = driver.find_elements(By.CSS_SELECTOR, "span.pdfResultadoBopa")
                for section in sections:
                    links = section.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        href = link.get_attribute("href")
                        text = link.text.strip()
                        if href and href.endswith(".pdf"):
                            for keyword in keywords:
                                if keyword.lower() in text.lower():
                                    results.append({
                                        "url_base": url,
                                        "title": text,
                                        "link": href,
                                        "pdf_url": href
                                    })
            except Exception:
                pass
            driver.switch_to.default_content()
    except Exception as e:
        print(f"⚠️ Error BOPA: {e}")
    return results