from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time
from datetime import datetime, timedelta

# Función para calcular la fecha del Viernes Santo
def get_good_friday(year):
    """Calcula la fecha del Viernes Santo para un año dado."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime(year, month, day) - timedelta(days=2)  # Viernes Santo

# Festivos generales en Cataluña
FESTIVOS_CATALUYA_BASE = [
    (1, 1),   # Año Nuevo
    (1, 6),   # Reyes
    (5, 1),   # Día del Trabajador
    (6, 24),  # San Juan
    (8, 15),  # Asunción
    (9, 11),  # Diada de Cataluña
    (10, 12), # Fiesta Nacional de España
    (11, 1),  # Todos los Santos
    (12, 6),  # Día de la Constitución
    (12, 8),  # Inmaculada Concepción
    (12, 25)  # Navidad
]

def get_boe_url():
    today = datetime.today()
    return f"https://www.boe.es/boe/dias/{today.year}/{today.month:02d}/{today.day:02d}/"

def get_dogc_url():
    today = datetime.today()
    good_friday = get_good_friday(today.year)
    festivos_catalunya = FESTIVOS_CATALUYA_BASE + [(good_friday.month, good_friday.day)]
    
    while True:
        today += timedelta(days=1)
        if today.weekday() in [5, 6] or (today.month, today.day) in festivos_catalunya:
            continue
        break
    return f"https://dogc.gencat.cat/es/sumari-del-dogc/?numDOGC={9324 + (today - datetime(2025, 3, 24)).days}"

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

            # Determinar la clase a buscar según la URL
            if "boe.es" in url:
                class_name = "sumario"
            elif "dogc.gencat.cat" in url:
                class_name = "wrapper-disposicions"
            else:
                class_name = "imc--llistat"
            
            # Buscar los elementos con la clase específica que contiene la información
            sections = driver.find_elements(By.CLASS_NAME, class_name)

            # Procesar los elementos encontrados y filtrar por palabras clave
            for section in sections:
                lines = section.text.strip().split("\n")  # Separar el texto en líneas
                for line in lines:
                    if any(kw.lower() in line.lower() for kw in keywords):
                        scraped_data.append({"url": url, "title": line.strip()})  # Guardar el texto en `title`

    except Exception as e:
        print("❌ Error al procesar las URLs:", e)
    finally:
        driver.quit()  # Cerrar el navegador al finalizar

    print("✅ Scraped Data:", scraped_data)  # Mostrar los datos extraídos
    return scraped_data

# Definir URLs a analizar y palabras clave para filtrar
urls = ["https://dogv.gva.es/es/inici", get_boe_url(), get_dogc_url()]
keywords = ["subvención", "subvenciones","subvenció","licitació", "licitación", "contrato","contracte","contractació","contratos"]

# Ejecutar la función de scraping
scraped_data = scrape_multiple_websites(urls, keywords)
