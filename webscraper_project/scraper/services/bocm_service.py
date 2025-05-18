from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_bocm(driver, url, keywords):
    results = []
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.file a"))
        )
        pdf_links = driver.find_elements(By.CSS_SELECTOR, "span.file a")
       
        field_items = driver.find_elements(By.CSS_SELECTOR, "div.field-item.even p")
        titles = [p.text.strip() for p in field_items]

        for i, link in enumerate(pdf_links):
            href = link.get_attribute("href")
            title = titles[i] if i < len(titles) else link.text.strip()
            if href.lower().endswith(".pdf") and any(keyword.lower() in title.lower() for keyword in keywords):
                results.append({
                    "url_base": url,
                    "title": title,
                    "link": href,
                    "pdf_url": href
                })
    except Exception as e:
        print(f"⚠️ Error extrayendo PDFs del BOCM: {e}")
    return results