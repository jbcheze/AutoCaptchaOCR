# ================================================================================================================================
# CAPTCHA Scraper for finetunning : scraping rutracker.org 1000 captchas for finetunning
# Next step : labelise them
# ================================================================================================================================

from multiprocessing import Process, Queue  
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import json
import os
from datetime import datetime
import time
from utils_captcha.consent_selectors import css_selectors, xpath_selectors

class CaptchaScraper:
    def __init__(self, worker_id=0):
        self.worker_id = worker_id
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-logging')

        try:
            self.driver = webdriver.Chrome(options=self.options)
        except Exception as e:
            raise Exception(e)

        self.wait = WebDriverWait(self.driver, 10)
        self.captcha_element = None
        

    def searching_captchas(self, images, context=""):
        for image in images:
            try:
                width = image.size['width']
                height = image.size['height']
                src = (image.get_attribute('src') or '').lower()
                 
                if 100<width<400 and 40<height<150:
                    if "logo" in src or "banner" in src:
                        continue
                    return image
            except:
                continue
        return None

       
    def click_consent_buttons(self):
        self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(0.5)
        self.driver.execute_script('window.scrollTo(0, 0);')
        time.sleep(0.5)
        
        for css_selector in css_selectors:
            try:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, css_selector)
                if buttons:
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            button.click()
                            time.sleep(1)
                            return True
            except:
                continue

        for xpath_selector in xpath_selectors:
            try:
                buttons = self.driver.find_elements(By.XPATH, xpath_selector)
                if buttons:
                    for button in buttons:
                        if button.is_displayed():
                            button.click()
                            time.sleep(1)
                            return True
            except:
                continue

        return False
    

    def extract_captcha(self):
        captcha = None
        
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//img | //canvas")))
            elements = self.driver.find_elements(By.XPATH, "//img | //canvas")
            captcha = self.searching_captchas(elements, "on main page")
        except:
            pass
        
        if captcha:
            self.captcha_element = captcha
            return True
        
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        try:
            elements = self.driver.find_elements(By.XPATH, "//img | //canvas")
            captcha = self.searching_captchas(elements, "after scroll")
        except:
            pass

        if captcha:
            self.captcha_element = captcha
            return True

        consent_clicked = self.click_consent_buttons()
        
        if consent_clicked:
            time.sleep(1)
            try:
                elements = self.driver.find_elements(By.XPATH, "//img | //canvas")
                captcha = self.searching_captchas(elements, "after consent")
            except:
                pass
        
        if captcha:
            self.captcha_element = captcha
            return True
        
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                try:
                    self.driver.switch_to.frame(iframe)
                    time.sleep(0.5)
                    elements = self.driver.find_elements(By.XPATH, "//img | //canvas")
                    captcha = self.searching_captchas(elements, f"in iframe")
                    
                    if captcha:
                        self.captcha_element = captcha
                        return True
                    self.driver.switch_to.default_content()
                except:
                    self.driver.switch_to.default_content()
                    continue
        except:
            self.driver.switch_to.default_content()
        
        self.captcha_element = captcha
        return False

    
    def save_captcha_image(self):
        if not self.captcha_element:
            return None
        
        try:
            os.makedirs("data/raw", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"captcha_w{self.worker_id}_{timestamp}.png"
            path = f"data/raw/{filename}"
            
            self.captcha_element.screenshot(path)
            return path
        except:
            return None
    

    def save_metadata(self, filename, url):
        os.makedirs("data/processed", exist_ok=True)
        metadata_path = f"data/processed/captcha_metadata_w{self.worker_id}.json"
        
        try:
            with open(metadata_path, 'r') as f:
                all_metadata = json.load(f)
        except:
            all_metadata = []
        
        metadata_entry = {
            'filename': filename,
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'worker_id': self.worker_id
        }
        
        all_metadata.append(metadata_entry)
        
        with open(metadata_path, 'w') as f:
            json.dump(all_metadata, f, indent=2)
    
    def collect(self, url, count, result_queue):
        # ================================================================================================================================
        # Multiproccesing
        # ================================================================================================================================
        success = 0
        
        print(f"Worker {self.worker_id}")
        try:
            self.driver.get(url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(1)
            print(f"Worker {self.worker_id}: Page loaded")
            
            for i in range(count):
                if self.extract_captcha():
                    captcha_path = self.save_captcha_image()
                    if captcha_path:
                        self.save_metadata(captcha_path, url)
                        success += 1
                        if (i + 1) % 20 == 0:
                            print(f"Worker {self.worker_id}. {success}/{i+1}")
                
                if i < count - 1:
                    self.driver.refresh()
                    time.sleep(1)
            
            print(f"Worker {self.worker_id}. Collected {success}/{count}")
            result_queue.put(success)
            
        except Exception as e:
            print(f"Worker {self.worker_id}. {e}")
            result_queue.put(success)
        finally:
            self.driver.quit()


def worker_process(worker_id, url, count_per_worker, result_queue):
    scraper = CaptchaScraper(worker_id=worker_id)
    scraper.collect(url, count_per_worker, result_queue)


def main():
    url = "https://rutracker.org/forum/profile.php?mode=register"
    total_count=1000
    nb_workers=3
    count_per_worker=total_count//nb_workers
    
    result_queue = Queue()
    processes = []
    start_time = time.time()
    
    # Start workers
    for i in range(nb_workers):
        p = Process(target=worker_process, args=(i, url, count_per_worker, result_queue))
        p.start()
        processes.append(p)
        print(f"Worker {i} started")

    
    for p in processes:
        p.join()
    
    # Collecting results
    total_success = 0
    while not result_queue.empty():
        total_success+=result_queue.get()
    
    elapsed = time.time()-start_time
    
    print(f"Collected {total_success}/{total_count}")
    print(f"Time {elapsed/60:.1f} minutes")
    print(f"Speed {total_success/elapsed*60:.1f} captchas/min")


if __name__ == "__main__":
    main()

# https://www.geeksforgeeks.org/python/multithreading-or-multiprocessing-with-python-and-selenium/