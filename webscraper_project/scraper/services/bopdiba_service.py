from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin

def scrape_bopdiba(driver, url, keywords):
    results = []
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "a.stretched-link.text-reset.text-decoration-none"))
        )
        main_links = driver.find_elements(By.CSS_SELECTOR, "a.stretched-link.text-reset.text-decoration-none")
        for main_link in main_links:
            sub_url = main_link.get_attribute("href")
            driver.get(sub_url)
            pdf_url = None
            title = None
            try:
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "li.list-group-item.bg-transparent a"))
                )
                try:
                    h1 = driver.find_element(By.CSS_SELECTOR, "h1.mb-5.font-weight-light")
                    title = h1.text.strip()
                except Exception:
                    title = None
                pdf_links = driver.find_elements(By.CSS_SELECTOR, "li.list-group-item.bg-transparent a")
                for pdf_link in pdf_links:
                    pdf_href = pdf_link.get_attribute("href")
                    if "descarrega-pdf" in pdf_href:
                        pdf_url = urljoin(sub_url, pdf_href)
                        break
            except Exception as e:
                print(f"⚠️ No se pudo extraer PDF en la subpágina {sub_url}: {e}")
            finally:
                driver.back()
            # Filtrado por keywords en el título
            if title and any(keyword.lower() in title.lower() for keyword in keywords):
                results.append({
                    "url_base": url,
                    "title": title, 
                    "link": sub_url,
                    "pdf_url": pdf_url,
                    "region": "Cataluña",
                    "organism": "BOP DIBA"
                })
    except Exception as e:
        print(f"⚠️ Error extrayendo PDFs del BOP DIBA: {e}")
    return results