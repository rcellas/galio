from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

def scrape_multiple_websites(urls, keywords):
    # Configuración del driver
    options = Options()
    options.add_argument('--headless')  
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    service = Service("/usr/local/bin/geckodriver")
    driver = webdriver.Firefox(service=service, options=options)

    scraped_data = []

    try:
        for url in urls:
            print(f"🔎 Scraping URL: {url}")
            driver.get(url)

            # Esperar que la página cargue completamente
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Comprobar si hay iframes en la página
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            if iframes:
                print(f"🔄 Se encontraron {len(iframes)} iframes. Cambiando al primero.")
                driver.switch_to.frame(iframes[0])

            # Esperar a que aparezcan los elementos con la clase deseada
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "imc--dogv-llistat"))
            )

            # Extraer los elementos
            sections = driver.find_elements(By.CLASS_NAME, "imc--dogv-llistat")

            # Filtrar los textos que contienen las palabras clave
            filtered_texts = [
                {"text": section.text.strip()}
                for section in sections
                if any(kw.lower() in section.text.lower() for kw in keywords)
            ]

            # Guardar resultados
            scraped_data.extend(filtered_texts)

    except Exception as e:
        print("❌ Error al procesar las URLs:", e)
    finally:
        driver.quit()

    print("✅ Scraped Data:", scraped_data)
    return scraped_data

# Definir URLs y palabras clave
urls = ["https://dogv.gva.es/es/inici"]
keywords = ["subvención", "licitación", "oposiciones", "empleo público", "contratos"]

# Ejecutar la función
scraped_data = scrape_multiple_websites(urls, keywords)
