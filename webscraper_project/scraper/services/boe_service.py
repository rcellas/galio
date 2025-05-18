from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_boe(driver, url):
    results = []
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "li.puntoPDF a"))
        )
        li_pdf = driver.find_element(By.CSS_SELECTOR, "li.puntoPDF a")
        pdf_url = li_pdf.get_attribute("href")
        base_boe_url = "https://www.boe.es"
        full_pdf_url = base_boe_url + pdf_url if pdf_url.startswith("/") else pdf_url
        title = li_pdf.text.strip()
        results.append({
            "url_base": url,
            "title": title,
            "link": url,
            "pdf_url": full_pdf_url
        })
    except Exception as e:
        print(f"⚠️ Error extrayendo PDF del BOE: {e}")
    return results