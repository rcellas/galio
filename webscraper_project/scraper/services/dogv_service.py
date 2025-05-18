from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_dogv(driver, url):
    results = []
    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            driver.switch_to.frame(iframes[0])
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            # Aquí puedes añadir lógica específica para DOGV si necesitas extraer PDFs o enlaces
            # Por ejemplo:
            pdf_links = driver.find_elements(By.CSS_SELECTOR, "a")
            for link in pdf_links:
                href = link.get_attribute("href")
                title = link.text.strip()
                if href and href.lower().endswith(".pdf"):
                    results.append({
                        "url_base": url,
                        "title": title,
                        "link": href,
                        "pdf_url": href
                    })
            driver.switch_to.default_content()
    except Exception as e:
        print(f"⚠️ Error extrayendo PDFs del DOGV: {e}")
    return results