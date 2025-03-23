from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time

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
                print(f"🔄 Se encontraron {len(iframes)} iframes.")
                
                # Mostrar los src de los iframes para analizar si son de otro dominio
                for i, iframe in enumerate(iframes):
                    print(f"🔍 Iframe {i+1} src:", iframe.get_attribute("src"))
                
                # Cambiar al primer iframe
                driver.switch_to.frame(iframes[0])
                time.sleep(5)  # Espera adicional para que el contenido cargue

                # Verificar si hay más iframes dentro del iframe
                nested_iframes = driver.find_elements(By.TAG_NAME, "iframe")
                if nested_iframes:
                    print(f"🔄 Dentro del primer iframe hay {len(nested_iframes)} iframes adicionales.")

            # Esperar a que aparezcan los elementos con la clase deseada
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "imc--llistat"))
            )

            # Extraer los elementos
            sections = driver.find_elements(By.CLASS_NAME, "imc--llistat")

            # Capturar y mostrar el contenido del iframe para verificar si hay datos
            full_text = driver.find_element(By.TAG_NAME, "body").text.strip()
            print(f"📜 Texto encontrado en el iframe:\n{full_text}")

            # Filtrar y dividir el contenido en líneas
            for section in sections:
                lines = section.text.strip().split("\n")  # Separar por líneas
                for line in lines:
                    if any(kw.lower() in line.lower() for kw in keywords):
                        scraped_data.append({"text": line.strip()})

    except Exception as e:
        print("❌ Error al procesar las URLs:", e)
    finally:
        driver.quit()

    print("✅ Scraped Data:", scraped_data)
    return scraped_data

# Definir URLs y palabras clave
urls = ["https://dogv.gva.es/es/inici"]
keywords = ["subvención", "licitación", "contratos"]

# Ejecutar la función
scraped_data = scrape_multiple_websites(urls, keywords)
