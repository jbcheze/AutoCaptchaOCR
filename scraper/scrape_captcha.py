from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import os

TMP_DIR = "tmp"
os.makedirs(TMP_DIR, exist_ok=True)


def scrape_captcha(url: str) -> str:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(url)

        wait.until(EC.presence_of_element_located((By.TAG_NAME, "img")))
        images = driver.find_elements(By.TAG_NAME, "img")

        for img in images:
            width = img.size["width"]
            height = img.size["height"]
            src = img.get_attribute("src") or ""

            if 100 < width < 400 and 40 < height < 150 and "logo" not in src:
                filename = f"captcha_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                path = os.path.join(TMP_DIR, filename)

                img.screenshot(path)
                return path

        raise RuntimeError("No captcha found")

    finally:
        driver.quit()
