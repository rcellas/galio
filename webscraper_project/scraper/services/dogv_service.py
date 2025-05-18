from selenium.webdriver.common.by import By

def scrape_dogv(driver, url):
    results = []
    links = driver.find_elements(By.TAG_NAME, "a")
    for link in links:
        href = link.get_attribute("href")
        text = link.text.strip()
        if href and not href.lower().endswith(".pdf"):
            results.append({
                "url_base": url,
                "title": text,
                "link": href,
                "pdf_url": None
            })
    return results