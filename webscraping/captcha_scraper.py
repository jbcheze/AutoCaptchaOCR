# ================================================================================================================================
# CAPTCHA SCRAPER 
# The goal is to detect captcha on the page (visible area, consent buttons, scroll down, iframes) 

# Save text CAPTCHA (data/raw) & determine type for reCAPTCHA/hCaptcha/Cloudflare (data/processed/scraping_metadata)
# ================================================================================================================================

# recaptcha v2 v3 https://github.com/2captcha/captcha-solver-selenium-python-examples/tree/main/examples/reCAPTCHA
# hcaptcha https://github.com/maximedrn/hcaptcha-solver-python-selenium
# cloudflare https://github.com/2captcha/captcha-solver-selenium-python-examples/tree/main/examples/cloudflare

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager # for WIFI connection, if hotspot - no service option needed
from selenium.common.exceptions import TimeoutException
import json
import os
import requests
from datetime import datetime
import time
from src.webscraping.utils.human_verification_keywords import verification_keywords
from src.webscraping.utils.consent_selectors import css_selectors, xpath_selectors

class CaptchaScraper:
    def __init__(self, chrome_driver_path=None):
        # ================================================================================================================================
        # Webdriver : config + initialization
        # ================================================================================================================================
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        #self.options.add_argument('--headless')
        if chrome_driver_path:
            self.driver = webdriver.Chrome(service=Service(chrome_driver_path), options=self.options)
        else:
            try:
                # self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options) If connected to WIFI 
                self.driver = webdriver.Chrome(options=self.options) # If connected to personal hotspot 
            except Exception as e:
                raise Exception(
                    "ChromeDriver not found in system PATH. "
                    "Specify the path or add it to the system PATH.\n"
                    f"Error: {str(e)}"
                )

        self.wait = WebDriverWait(self.driver, 10)
        self.captcha_element = None
        self.captcha_type = None  # text/recaptcha_v2/hcaptcha/cloudflare/unknown
        self.detection_method = None


    def find_captcha_in_elements(self, images, context=""):
        # ================================================================================================================================
        # Search for CAPTCHA-like elements among given images
        # ================================================================================================================================
        for image in images:
            try:
                width = image.size['width']
                height = image.size['height']

                src = (image.get_attribute('src') or '').lower()
                alt = (image.get_attribute('alt') or '').lower()
                 
                if 30 < width < 400 and 30 < height < 300:
                    # Logo and banner filtering
                    if "logo" in src or "banner" in src:
                        continue

                    # Check for CAPTCHA keywords
                    if 'captcha' in src or 'captcha' in alt:
                        print(f"Text CAPTCHA found {context}, size {width} x {height}")
                        return image

                    print(f"Potential CAPTCHA {context}, size {width} x {height}")
                    return image
            except:
                continue
        return None

    def click_consent_buttons(self):
        print("Handling consent buttons")
        self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(0.5)
        self.driver.execute_script('window.scrollTo(0, 0);')
        time.sleep(0.5)
        
        # Try CSS selectors first
        for index, css_selector in enumerate(css_selectors, 1):
            try:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, css_selector)
                if buttons:
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            button.click()
                            print(f"Clicked using CSS selector #{index}")
                            time.sleep(1)
                            return True
            except Exception:
                continue

        # Try XPath selectors
        for index, xpath_selector in enumerate(xpath_selectors, 1):
            try:
                buttons = self.driver.find_elements(By.XPATH, xpath_selector)
                if buttons:
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            button.click()
                            print(f"Clicked using XPath selector #{index}")
                            time.sleep(1)
                            return True
            except Exception:
                continue

        print("No consent buttons found")
        return False

    def check_third_party_iframes(self):
        # THird parts
        print("Checking third-party iframes...")
        
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            print(f"Found {len(iframes)} iframe(s)")
            
            for i, iframe in enumerate(iframes, 1):
                try:
                    src = (iframe.get_attribute('src') or '').lower()
                    title = (iframe.get_attribute('title') or '').lower()
                    
                    # reCAPTCHA detection
                    if 'recaptcha' in src or 'google.com/recaptcha' in src or 'recaptcha' in title:
                        print(f"reCAPTCHA iframe")
                        self.captcha_type = "recaptcha_v2"
                        self.detection_method = "recaptcha_iframe"
                        # IMPORTANT: Do NOT save iframe element (prevents stale element error)
                        return True
                    
                    # hCaptcha detection
                    if 'hcaptcha' in src or 'hcaptcha' in title:
                        print(f"hCaptcha iframe")
                        self.captcha_type = "hcaptcha"
                        self.detection_method = "hcaptcha_iframe"
                        return True
                    
                    # Cloudflare Turnstile detection
                    if 'cloudflare' in src or 'challenges.cloudflare' in src or 'turnstile' in src:
                        print(f"Cloudflare Turnstile iframe")
                        self.captcha_type = "cloudflare"
                        self.detection_method = "cloudflare_iframe"
                        return True
                    
                except:
                    continue
        except Exception as e:
            print(f"Error checking iframes: {e}")
        
        print("No third-party CAPTCHA iframes found")
        return False

    def check_verification_messages(self):
        print("Checking verification messages...")
        
        try:
            body = self.driver.find_element(By.TAG_NAME, 'body')
            page_text = body.text.lower()
            
            for keyword in verification_keywords:
                if keyword.lower() in page_text:
                    print(f"Verification message: '{keyword[:50]}...'")
                    self.detection_method = f"verification_text"
                    self.captcha_type = "unknown"
                    return True
            
            print("No verification messages found")
            return False
        except Exception as e:
            print(f"Error checking messages: {e}")
            return False

    def extract_captcha(self):
        # Step 1: Handle consent buttons
        consent_clicked = self.click_consent_buttons()
        if consent_clicked:
            print("CONSENT Handled successfully\n")
            time.sleep(1)
        
        # Step 2: PRIORITY - Check third-party iframes FIRST
        # This is the most reliable method for modern CAPTCHAs (professor's requirement)
        if self.check_third_party_iframes():
            print(f"SUCCESS: {self.captcha_type.upper()} DETECTED")
            return True
        
        # Step 3: Search for text-based CAPTCHA images
        print("3. Searching for text-based CAPTCHAs...")
        
        # Step 3.1: Visible area
        print("3.1 Checking visible area...")
        captcha = None
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//img | //canvas")))
            elements = self.driver.find_elements(By.XPATH, "//img | //canvas")
            print(f"Found {len(elements)} image/canvas elements")

            captcha = self.find_captcha_in_elements(elements, "in visible area")
            
        except TimeoutException:
            print("No images found in visible area")
        
        if captcha:
            self.captcha_element = captcha
            self.captcha_type = "text"
            self.detection_method = "text_image_visible"
            print("SUCCESS: TEXT CAPTCHA DETECTED")
            return True
        
        # Step 3.2: After scrolling
        print("3.2 Scrolling down...")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        try:
            elements = self.driver.find_elements(By.XPATH, "//img | //canvas")
            print(f"Found {len(elements)} image/canvas elements")
            captcha = self.find_captcha_in_elements(elements, "after scrolling")
            
        except Exception as e:
            print(f"Error after scrolling: {e}")

        if captcha:
            self.captcha_element = captcha
            self.captcha_type = "text"
            self.detection_method = "text_image_scroll"
            print("SUCCESS: TEXT CAPTCHA DETECTED")
            return True
        
        # Step 3.3: Inside iframes
        print("3.3 Checking iframes for images...")
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            print(f"Found {len(iframes)} iframe(s)")
            
            for i, iframe in enumerate(iframes):
                try:
                    print(f"Checking iframe {i+1}...")
                    self.driver.switch_to.frame(iframe)
                    time.sleep(0.5)
                    
                    elements = self.driver.find_elements(By.XPATH, "//img | //canvas")
                    print(f"Found {len(elements)} elements in iframe")
                    captcha = self.find_captcha_in_elements(elements, f"in iframe {i+1}")
                    
                    if captcha:
                        self.captcha_element = captcha
                        self.captcha_type = "text"
                        self.detection_method = f"text_image_iframe_{i+1}"
                        print("\n" + "="*70)
                        print(f"SUCCESS: TEXT CAPTCHA IN IFRAME {i+1}")
                        print("="*70)
                        return True
                    
                    self.driver.switch_to.default_content()
                    
                except Exception as e:
                    print(f"   Error in iframe {i+1}: {e}")
                    self.driver.switch_to.default_content()
                    continue
                
        except Exception as e:
            print(f"Error checking iframes: {e}")
            self.driver.switch_to.default_content()
        
        # Step 4: Fallback check verification messages
        if self.check_verification_messages():
            print("SUCCESS: VERIFICATION MESSAGE DETECTED")
            return True
        
        print("NO CAPTCHA DETECTED")
        return False

    def save_captcha_image(self):
        if not self.captcha_element:
            print("No CAPTCHA element to save")
            return None
        
        try:
            os.makedirs("data/raw", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"captcha_{timestamp}.png"
            path = f"data/raw/{filename}"
            
            # Method 1: Try downloading from src
            tag_name = self.captcha_element.tag_name.lower()
            if tag_name == 'img':
                src = self.captcha_element.get_attribute('src')
                
                if src and not src.startswith('data:'):
                    try:
                        print(f"Downloading from src...")
                        
                        # Make URL absolute if relative
                        if src.startswith('/'):
                            base_url = '/'.join(self.driver.current_url.split('/')[:3])
                            src = base_url + src
                        
                        # Download with session cookies
                        cookies = self.driver.get_cookies()
                        session = requests.Session()
                        for cookie in cookies:
                            session.cookies.set(cookie['name'], cookie['value'])
                        
                        response = session.get(src, timeout=10)
                        
                        if response.status_code == 200:
                            with open(path, 'wb') as f:
                                f.write(response.content)
                            print(f"Image downloaded: {path}")
                            return path
                    except Exception as e:
                        print(f" Download failed: {e}")
            
            # Method 2: Take screenshot
            print(f"Taking screenshot...")
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", 
                                      self.captcha_element)
            time.sleep(0.5)
            
            self.captcha_element.screenshot(path)
            print(f"SAVED Screenshot: {path}")
            return path
            
        except Exception as e:
            print(f"ERROR Save failed: {e}")
            return None

    def save_metadata(self, filename, url):
        os.makedirs("data/processed", exist_ok=True)
        metadata_path = "data/processed/captcha_metadata.json"
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                all_metadata = json.load(f)
        except:
            all_metadata = []
        
        metadata_entry = {
            'filename': filename,
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'page_title': self.driver.title,
            'captcha_type': self.captcha_type,
            'detection_method': self.detection_method
        }
        
        all_metadata.append(metadata_entry)
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(all_metadata, f, indent=2, ensure_ascii=False)
        
        print(f"METADATA saved to {metadata_path}")

    def scrape_url(self, url):
        try:
            print(f"Navigating to: {url}")
            self.driver.get(url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            print(f"Page loaded: {self.driver.title}")
            time.sleep(1)
            
            # Detect CAPTCHA
            if self.extract_captcha():
                # Text CAPTCHA: save image
                if self.captcha_type == "text":
                    captcha_path = self.save_captcha_image()
                    if captcha_path:
                        self.save_metadata(captcha_path, url)
                        return True
                    else:
                        # Detected but save failed
                        self.save_metadata("save_failed", url)
                        return True
                else:
                    # Modern CAPTCHA (reCAPTCHA/hCaptcha/Cloudflare)
                    # Save type only, NO image
                    print(f"\n[{self.captcha_type.upper()}] Saving type to metadata only")
                    self.save_metadata("modern_captcha_detected", url)
                    return True
            
            return False
        
        except Exception as e:
            print(f"[ERROR] {e}")
            return False
        
        finally:
            self.driver.switch_to.default_content()
            # Reset state
            self.captcha_element = None
            self.captcha_type = None
            self.detection_method = None

    def close(self):
        self.driver.quit()


def main(): 
    print("Initializing WebDriver")
    scraper = CaptchaScraper()

    # Test URLs
    urls = [
        "https://www.metropolegrandparis.fr/fr/formulaire-de-contact",
        "https://www.google.com/recaptcha/api2/demo",
        "https://accounts.hcaptcha.com/demo",
        "https://2captcha.com/demo/cloudflare-turnstile",
        "https://www.metropolegrandparis.fr/fr/formulaire-de-contact",
       "https://www.rdv-prefecture.interieur.gouv.fr/rdvpref/reservation/demarche/4443/cgu/", 
       "https://rutracker.org/forum/profile.php?mode=register",
       "https://recaptcha-demo.appspot.com/recaptcha-v2-checkbox.php?utm_source=chatgpt.com",
        "https://www.wigglypaint.art/ru/popular-games/im-not-a-robot?utm_source=chatgpt.com",
        "https://visa.vfsglobal.com/gbr/en/aut/book-an-appointment",
        "https://www.google.com/recaptcha/api2/demo?utm_source=chatgpt.com",
        "https://neal.fun/not-a-robot/",
        "https://secure.aarp.org/applications/user/register?response_type=code&client_id=0oadzmafi2ZcytYcq2p7&redirect_uri=https%3A%2F%2Fapi.eventive.org%2Fauth%2Faarp%2Fcallback&state=274a4a5862f2cedca05c10706059ee23&scope=bui+bmi+ba+em+ln&promo=MFG"
        "https://www.emerson.com/global",
        "https://www.phpbb.com/community/ucp.php?mode=register" #-> rajouter button1 class in consetn
        "https://forum.vbulletin.com/register" #HCPATCHA
        "https://www.google.com/recaptcha/api2/demo" #-> GOOCLE RECAP
        "https://recaptcha-demo.appspot.com/recaptcha-v2-checkbox.php"
        "https://accounts.hcaptcha.com/demo"
        "https://2captcha.com/demo/cloudflare-turnstile" # coudflare demo

    ]

    print("Beginning CAPTCHA scraping")
    
    success_count = 0
    for idx, url in enumerate(urls, 1):
        print(f"[{idx}/{len(urls)}] Processing URL")
        
        if scraper.scrape_url(url):
            success_count += 1
            print(f"Success for URL {idx}")
        else:
            print(f"Failed for URL {idx}")
        
        time.sleep(1) 

    print(f"URLs processed: {len(urls)}")

    scraper.close()
    print("Browser closed")


if __name__ == "__main__":
    main()
