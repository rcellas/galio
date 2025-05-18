from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin

def scrape_dogc(driver, url):
    results = []
    try:
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
                title = a_tag_pdf.text.strip()
                results.append({
                    "url_base": url,
                    "title": title,
                    "link": url,
                    "pdf_url": pdf_url
                })
            except Exception:
                pass
    except Exception as e:
        print(f"⚠️ Error extrayendo PDF del DOGC: {e}")
    return results