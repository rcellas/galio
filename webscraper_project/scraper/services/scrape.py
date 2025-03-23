from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time

def scrape_multiple_websites(urls, keywords):
    # Configuración del driver de Selenium con opciones
    options = Options()
    options.add_argument('--headless')  # Ejecutar en modo sin interfaz gráfica
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Especificar la ruta del geckodriver
    service = Service("/usr/local/bin/geckodriver")
    driver = webdriver.Firefox(service=service, options=options)

    scraped_data = []  # Lista para almacenar los datos extraídos

    try:
        for url in urls:
            print(f"🔎 Scraping URL: {url}")
            driver.get(url)  # Cargar la URL en el navegador

            # Esperar hasta que el cuerpo de la página esté presente
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Buscar iframes dentro de la página
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            if iframes:
                print(f"🔄 Se encontraron {len(iframes)} iframes. Cambiando al primero.")
                driver.switch_to.frame(iframes[0])  # Cambiar al primer iframe
                
                # Esperar que el contenido del iframe cargue completamente
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

            # Agregar un retraso extra para asegurar la carga completa de la página
            time.sleep(5)

            # Buscar los elementos con la clase específica que contiene la información
            sections = driver.find_elements(By.CLASS_NAME, "imc--llistat")

            # Procesar los elementos encontrados y filtrar por palabras clave
            for section in sections:
                lines = section.text.strip().split("\n")  # Separar el texto en líneas
                for line in lines:
                    if any(kw.lower() in line.lower() for kw in keywords):
                        scraped_data.append({"text": line.strip()})  # Agregar la línea coincidente

    except Exception as e:
        print("❌ Error al procesar las URLs:", e)
    finally:
        driver.quit()  # Cerrar el navegador al finalizar

    print("✅ Scraped Data:", scraped_data)  # Mostrar los datos extraídos
    return scraped_data

# Definir URLs a analizar y palabras clave para filtrar
urls = ["https://dogv.gva.es/es/inici"]
keywords = ["subvención", "subvenciones","SUBVENCIONES" "licitación", "contrato", "contratos"]

# Ejecutar la función de scraping
scraped_data = scrape_multiple_websites(urls, keywords)
