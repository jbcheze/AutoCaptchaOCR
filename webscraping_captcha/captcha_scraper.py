# ================================================================================================================================
# CAPTCHA SCRAPER 
# The goal is to detect CAPTCHA type (text/reCAPTCHA/hCAPTCHA/Cloudflare/unknown) & extract text CAPTCHA on the page (visible area, consent buttons, scroll down, iframes) 
# ================================================================================================================================
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
import json
from datetime import datetime
import time
from pathlib import Path
from utils_captcha.consent_selectors import css_selectors, xpath_selectors
from utils_captcha.human_verification_keywords import verification_keywords


class CaptchaScraper:
    # ================================================================================================================================
    # Webdriver config
    # ================================================================================================================================
    def __init__(self, chrome_driver_path=None):
        print("Browser initialization")
        
        # Chrome options
        # self.options.add_argument('--headless') 
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        
        # Initialize driver
        if chrome_driver_path:
            self.driver = webdriver.Chrome(
                service=Service(chrome_driver_path), 
                options=self.options
            )
        else:
            try:
                self.driver = webdriver.Chrome(options=self.options)
            except Exception as e:
                raise Exception(f"ChromeDriver not found in system PATH. "
                                "Specify the path or add it to the system PATH.\n"
                                f"Error: {str(e)}"
                                )
        
        self.wait = WebDriverWait(self.driver, 10)

        self.captcha_element = None
        self.captcha_type = None

    def detect_images(self, images, context=""):
        # ================================================================================================================================
        # Search for CAPTCHA images
        # ================================================================================================================================
        for image in images:
            try:
                # Filtering by size
                width = image.size['width']
                height = image.size['height']
                if 30 < width < 400 and 30 < height < 300:
                    # Filterinf by logo or banner
                    src = (image.get_attribute("src") or "").lower()
                    if "logo" in src or "banner" in src:
                        continue
                    
                    print(f"Potential CAPTCHA found: {width}x{height}")
                    return image
            
            except:
                continue
        
        return None

    def click_consent_buttons(self):
        # ================================================================================================================================
        # Click consent/cookie buttons
        # ================================================================================================================================
        # Scroll to load pop ups
        self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(2)
        self.driver.execute_script('window.scrollTo(0, 0);')
        time.sleep(1)
        
        # Trying CSS selectors 
        for css_selector in css_selectors:
            try:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, css_selector)
                for button in buttons:
                    if button.is_displayed():
                        button.click()
                        print("Consent button clicked with CSS selector")
                        time.sleep(1)
                        return True
            
            except:
                continue
        
        # Trying XPath selectors
        for xpath_selector in xpath_selectors:
            try:
                buttons = self.driver.find_elements(By.XPATH, xpath_selector)
                for button in buttons:
                    if button.is_displayed():
                        button.click()
                        print("Consent button clicked with XPath selector")
                        time.sleep(1)
                        return True
            
            except:
                continue
        
        print("No consent buttons found")
        return False

    def check_iframes(self):
        # ================================================================================================================================
        # Check for reCAPTCHA/hCAPTCHA/Cloudflare iframes
        # ================================================================================================================================
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            print(f"Found {len(iframes)} iframes")
            
            for iframe in iframes:
                try:
                    # Get iframe source & title
                    src = (iframe.get_attribute('src') or '').lower()
                    title = (iframe.get_attribute('title') or '').lower()
                    
                    # Check for reCAPTCHA
                    if 'recaptcha' in src or 'recaptcha' in title:
                        print("reCAPTCHA detected")
                        self.captcha_type="recaptcha_v2_v3"
                        return True
                    
                    # Check for hCAPTCHA
                    if 'hcaptcha' in src or 'hcaptcha' in title:
                        print("hCaptcha detected")
                        self.captcha_type="hcaptcha"
                        return True
                    
                    # Check for Cloudflare
                    if 'cloudflare' in src:
                        print("Cloudflare detected")
                        self.captcha_type="cloudflare"
                        return True
                
                except:
                    continue
        
        except Exception as e:
            print(f"Error checking iframes: {e}")
        
        print("No CAPTCHA iframes found")
        return False

    def check_verification_messages(self):
        # ================================================================================================================================
        # Check for verification messages like "I'm not a robot"
        # ================================================================================================================================
        try:
            body = self.driver.find_element(By.TAG_NAME, 'body')
            page_text = body.text.lower()
            
            # Check for each keyword
            for keyword in verification_keywords:
                keyword_lower = keyword.lower()
                
                if keyword_lower in page_text:
                    print(f"Verification message : '{keyword}'")
                    self.captcha_type = "verification_text"
                    return True
            
            print("No verification messages found")
            return False
        
        except Exception as e:
            print(f"Error checking verification pop up: {e}")
            return False

    def captcha_extracting(self):
        # ================================================================================================================================
        # Extract CAPTCHA: consent -> iframes -> text CAPTCHA -> scrolling -> iframes
        # ================================================================================================================================
        # 1. Click consent buttons
        print("Checking consent buttons")
        consent_clicked = self.click_consent_buttons()
        if consent_clicked:
            time.sleep(2)
        
        # 2. Check for modern CAPTCHAs (reCAPTCHA/hCAPTCHA/Cloudflare)
        print("Checking iframes")
        if self.check_iframes():
            print(f"{self.captcha_type} found")
            return True
        
        # 3. Check for text CAPTCHA
        print("Checking for text CAPTCHA")
        captcha = None
        
        # Check visible area
        print("1) Visible area")
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//img | //canvas")))
            elements = self.driver.find_elements(By.XPATH, "//img | //canvas")
            print(f"Found {len(elements)} images")
            
            captcha = self.detect_images(elements, "visible area")
        
        except TimeoutException:
            print("No images in visible area")
        
        if captcha:
            self.captcha_element = captcha
            self.captcha_type = "text"
            print("Text CAPTCHA found in visible area !")
            return True
        
        # Scroll down and check again
        print("2) After scrolling")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        try:
            elements = self.driver.find_elements(By.XPATH, "//img | //canvas")
            print(f"Found {len(elements)} images")
            
            captcha = self.detect_images(elements, "after scroll")
        
        except Exception as e:
            print(f"Error {e}")
        
        if captcha:
            self.captcha_element = captcha
            self.captcha_type = "text"
            print("Text CAPTCHA found after scrolling !")
            return True
        
        # Check inside iframes
        print("3) Inside iframes")
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            print(f"Found {len(iframes)} iframes")
            
            for iframe in iframes:
                try:
                    # Switch to iframe
                    self.driver.switch_to.frame(iframe)
    
                    elements = self.driver.find_elements(By.XPATH, "//img | //canvas")
                    print(f"Iframe: {len(elements)} images")
                    
                    captcha = self.detect_images(elements, f"iframe")
                    
                    if captcha:
                        self.captcha_element = captcha
                        self.captcha_type = "text"
                        print(f"Text CAPTCHA found in iframe !")
                        return True
                    
                    # Back to default
                    self.driver.switch_to.default_content()
                
                except Exception as e:
                    print(f"Iframe error: {e}")
                    self.driver.switch_to.default_content()
                    continue
        
        except Exception as e:
            self.driver.switch_to.default_content()
        
        # Check for verification messages
        print("4) Checking verification messages")
        if self.check_verification_messages():
            return True
        
        print("No CAPTCHA detected")
        return False

    def save_captcha(self):
        # ================================================================================================================================
        # Saving CAPTCHA : extracting directly else screenshot
        # ================================================================================================================================
        if not self.captcha_element:
            print("No CAPTCHA to save")
            return None
        
        try:
            # Create directory
            data_dir = Path("data/raw")
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"captcha_{timestamp}.png"
            filepath = data_dir / filename
            
            # Try downloading from src
            tag_name = self.captcha_element.tag_name.lower()
            
            if tag_name == 'img':
                src = self.captcha_element.get_attribute('src')
                
                # Check if we can download
                if src and not src.startswith('data:'):
                    try:
                        print("Downloading image from src")
                        
                        # Make URL absolute
                        if src.startswith('/'):
                            current_url = self.driver.current_url
                            url_parts = current_url.split('/')
                            base_url = url_parts[0] + '//' + url_parts[2]
                            src = base_url + src
                        
                        # Get cookies
                        cookies = self.driver.get_cookies()
                        session = requests.Session()
                        
                        for cookie in cookies:
                            session.cookies.set(cookie['name'], cookie['value'])
                        
                        response = session.get(src, timeout=10)
                        
                        if response.status_code == 200:
                            with open(filepath, 'wb') as f:
                                f.write(response.content)
                            
                            print(f"Image downloaded: {filepath}")
                            return str(filepath)
                    
                    except Exception as e:
                        print(f"Download failed: {e}")
            
            # Take screenshot instead
            print("Taking screenshot")
            script = "arguments[0].scrollIntoView({block: 'center'});"
            self.driver.execute_script(script, self.captcha_element)
            time.sleep(0.5)
            
            # Screenshot
            self.captcha_element.screenshot(str(filepath))
            print(f"Screenshot saved: {filepath}")
            
            return str(filepath)
        
        except Exception as e:
            print(f"Save failed: {e}")
            return None

    def save_metadata(self, filename, url):
        # ================================================================================================================================
        # Saving CAPTCHA
        # ================================================================================================================================
        data_dir = Path("data/processed")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        metadata_path = data_dir / "scraping_captchas_metadata.json"
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                all_metadata = json.load(f)
        except:
            all_metadata = []
        
        # Create new entry
        metadata_entry = {
            'filename': filename,
            'url': url,
            'page_title': self.driver.title,
            'captcha_type': self.captcha_type
        }
        
        all_metadata.append(metadata_entry)
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(all_metadata, f, indent=2, ensure_ascii=False)
        
        print(f"Metadata saved to {metadata_path}")

    def scrape_url(self, url):
        # ================================================================================================================================
        # Main scraping func
        # ================================================================================================================================
        try:
            print(f"Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for page load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)
            
            # Detect CAPTCHA
            if self.captcha_extracting():
                if self.captcha_type == "text":
                    captcha_path = self.save_captcha()
                    
                    if captcha_path:
                        self.save_metadata(captcha_path, url)
                        return True
                    else:
                        self.save_metadata("save_failed", url)
                        return True
                
                # For reCAPTCHA v2 v3/hCAPTCHA/Cloudflare saving metadata only
                else:
                    self.save_metadata("modern_captcha", url)
                    return True
            
            return False
        
        except Exception as e:
            print(f"Error: {e}")
            return False
        
        finally:
            # Resetting 
            self.driver.switch_to.default_content()
            self.captcha_element = None
            self.captcha_type = None

    def close(self):
        self.driver.quit()


def main():
    scraper = CaptchaScraper()
    
    # Test URLs
    urls = [
        "https://rutracker.org/forum/profile.php?mode=register", # Main POC site text CAPTCHA + cookie
        
        "https://nopecha.com/captcha/textcaptcha", # Text CAPTCHA demo
        "https://solvecaptcha.com/demo/image-captcha", # Text CAPTCHA demo
        #"https://www.metropolegrandparis.fr/fr/formulaire-de-contact", # Text CAPTCHA real (small size)
        #"https://www.rdv-prefecture.interieur.gouv.fr/rdvpref/reservation/demarche/4443/cgu/", # Text CAPTCHA real
        #"https://secure.aarp.org/applications/user/register?response_type=code&client_id=0oadzmafi2ZcytYcq2p7&redirect_uri=https%3A%2F%2Fapi.eventive.org%2Fauth%2Faarp%2Fcallback&state=274a4a5862f2cedca05c10706059ee23&scope=bui+bmi+ba+em+ln&promo=MFG" # 3D text CAPTCHA real
        
        #"https://www.google.com/recaptcha/api2/demo", # reCAPTCHA demo
        #"https://neal.fun/not-a-robot/", # reCAPTCHA demo
        #"https://recaptcha-demo.appspot.com/recaptcha-v2-checkbox.php" # reCAPTCHA v2 demo
        
        #"https://accounts.hcaptcha.com/demo", # hCAPCTHA demo
        #"https://forum.vbulletin.com/register" #hCAPTCHA real

        #"https://2captcha.com/demo/cloudflare-turnstile", # Cloudflare demo
        #"https://2captcha.com/demo/cloudflare-turnstile" # Cloudflare demo

        #"https://www.emerson.com/global", # no captchas but cookie
        #"https://www.phpbb.com/community/ucp.php?mode=register" # no captchas but cookie
    ]
    for url in urls:
        scraper.scrape_url(url)

    scraper.close()
    print("Browser closed")


if __name__ == "__main__":
    main()





"""
Browser initialization
Navigating to: https://rutracker.org/forum/profile.php?mode=register
Checking consent buttons
Consent button clicked with XPath selector
Checking iframes
Found 0 iframes
No CAPTCHA iframes found
Checking for text CAPTCHA
1) Visible area
Found 4 images
Potential CAPTCHA found: 120x72
Text CAPTCHA found in visible area !
Downloading image from src
Image downloaded: data/raw/captcha_20260130_183701.png
Metadata saved to data/processed/scraping_captchas_metadata.json

Navigating to: https://nopecha.com/captcha/textcaptcha
Checking consent buttons
No consent buttons found
Checking iframes
Found 48 iframes
No CAPTCHA iframes found
Checking for text CAPTCHA
1) Visible area
No images in visible area
2) After scrolling
Found 0 images
3) Inside iframes
Found 48 iframes
Iframe: 1 images
Potential CAPTCHA found: 200x80
Text CAPTCHA found in iframe !
Downloading image from src
Image downloaded: data/raw/captcha_20260130_183731.png
Metadata saved to data/processed/scraping_captchas_metadata.json

Navigating to: https://solvecaptcha.com/demo/image-captcha
Checking consent buttons
No consent buttons found
Checking iframes
Found 0 iframes
No CAPTCHA iframes found
Checking for text CAPTCHA
1) Visible area
Found 19 images
Potential CAPTCHA found: 250x50
Text CAPTCHA found in visible area !
Downloading image from src
Image downloaded: data/raw/captcha_20260130_183745.png
Metadata saved to data/processed/scraping_captchas_metadata.json
Browser closed
"""
