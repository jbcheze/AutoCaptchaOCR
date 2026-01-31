# ================================================================================================================================
# CAPTCHA SOLVER
# The goal is to solve detected CAPTCHA - detect input field, tap the answer & submit it.
# ================================================================================================================================
import random
from captcha_scraper import CaptchaScraper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
from datetime import datetime
import time
from pathlib import Path


class CaptchaSolver(CaptchaScraper):
    # ================================================================================================================================
    # Inherit from CaptchaScraper
    # ================================================================================================================================
    def __init__(self, chrome_driver_path=None):
        super().__init__(chrome_driver_path)
        self.input_field = None
        self.initial_url = None
        
    def search_input_field(self):
        # ================================================================================================================================
        # Searching for input field for CAPTCHA
        # ================================================================================================================================
        print("Searching input field")
        
        input_field_names = ["captcha", "code", "type_code", "captcha_code", "cap_code"]
        
        # Searching field by ID
        for input_field_name in input_field_names:
            try:
                element = self.driver.find_element(By.ID, input_field_name)  
                if element.is_displayed():
                    self.input_field = element
                    print(f"Input field found by ID: {input_field_name}")
                    return element
            except:
                pass
        
        # Searching field by NAME
        for input_field_name in input_field_names:
            try:
                element = self.driver.find_element(By.NAME, input_field_name)
                if element.is_displayed():
                    self.input_field = element
                    print(f"Input field found by NAME: {input_field_name}")
                    return element
            except:
                pass

        # Searching field near the CAPTCHA by XPATH & TAG NAME
        if self.captcha_element:
            try:
                # Go up to max 5 levels from CAPTCHA
                current = self.captcha_element
                for level in range(5):
                    try:
                        up_element = current.find_element(By.XPATH, "..")
                        inputs = up_element.find_elements(By.TAG_NAME, "input")
                        
                        for inp in inputs:
                            try:
                                if inp.is_displayed() and inp.is_enabled():
                                    inp_type = inp.get_attribute('type')
                                    if inp_type in ['text', '']:
                                        self.input_field = inp
                                        print("Input field found near CAPTCHA!")
                                        return inp
                            except:
                                pass
                        
                        current=up_element
                    except:
                        break
            except:
                pass
        
        # Last attempt searching for text inputs
        try:
            inputs = self.driver.find_elements(By.XPATH, "//input[@type='text']")
            
            # Filter search boxes & common fields
            for inp in inputs:
                try:
                    if not inp.is_displayed():
                        continue
                    
                    # Skip if it is a search box or navigation element
                    inp_id = (inp.get_attribute('id') or '').lower()
                    inp_name = (inp.get_attribute('name') or '').lower()
                    inp_placeholder = (inp.get_attribute('placeholder') or '').lower()
                    
                    # Skip common non-CAPTCHA fields
                    skip_keywords = ['search', 'query', 'username', 'login', 'email', 'password', "поиск"]
                    if any(keyword in inp_id or keyword in inp_name or keyword in inp_placeholder 
                           for keyword in skip_keywords):
                        continue
                    
                    # If we got here it might be the CAPTCHA field
                    self.input_field = inp
                    print(f"Found text input (id='{inp_id}', name='{inp_name}')")
                    return inp
                except:
                    pass
        except:
            pass       

        print("No input field found")
        return None
    
    def tap_solution(self, answer):
        # ================================================================================================================================
        # Fill CAPTCHA solution 
        # ================================================================================================================================
        if not self.input_field:
            print("No input field")
            return False
        
        try:
            # Click on the input field
            self.input_field.click()
            time.sleep(0.5)  
            
            # Clear field
            self.input_field.clear()
            time.sleep(0.3)
            
            # Type each character with small random delays to humanize
            print("Typing the answer")
            for a in answer:
                self.input_field.send_keys(a)
                time.sleep(random.uniform(0.2, 0.8))  

            print(f"The answer entered : '{answer}'")
            return True
            
        except Exception as e:
            print(f"Error filling the answer : {e}")
            return False
    

    def submit_captcha(self):
        # ================================================================================================================================
        # Submit CAPTCHA answer
        # ================================================================================================================================
        print("Submitting the answer")
        
        # Try to find submit button by type first 
        try:
            submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            if submit_btn.is_displayed():
                submit_btn.click()
                print("Submit button clicked")
                time.sleep(1)
                return True
        except:
            pass
        
        # Try to find by common button text
        button_texts = ["Submit", "Verify", "Send", "Confirm", "Valider", "Envoyer", "Confirmer", "Подтвердить", "Отправить", "submit", "verify", "send", "confirm", "valider", "envoyer", "confirmer", "подтвердить", "отправить", "Я согласен с условиями"]
        
        for button_text in button_texts:
            try:
                button = self.driver.find_element(By.XPATH, f"//button[contains(text(), '{button_text}')]")
                if button.is_displayed():
                    button.click()
                    print(f"Clicked '{button_text}' button")
                    time.sleep(1)
                    return True
            except:
                pass
        
        # If no button found, trying pressing Enter in the input field
        if self.input_field:
            try:
                self.input_field.send_keys(Keys.RETURN)
                print("No button, submitting via Enter")
                time.sleep(1)
                return True
            except:
                pass
        
        print("Could not find submit button & Enter didn't work")
        return False
    

    def check_success(self):
        # ================================================================================================================================
        # Check if CAPTCHA was solved successfully
        # ================================================================================================================================
        print("Checking the output")
        time.sleep(2)
        
        # Method 1: Check if URL changed
        current_url = self.driver.current_url
        print(f"Current URL: {current_url}")
        
        if self.initial_url and current_url != self.initial_url:
            print("URL changed. Success !")
            return True
        
        # Method 2: Look for success messages on page, not that reliable for forum sites
        page_text = self.driver.page_source.lower()
        success_words = ["success", "thank you", "successfully", "merci", "succès"]
        for word in success_words:
            if word in page_text:
                print(f"Found success word.")
                return True
        
        # Method 3: Check if there's an error about other fields 
        if "username is required" in page_text or "email is required" in page_text:
            print("Form error found - CAPTCHA seems correct")
            return True
        
        # Method 4: Check if CAPTCHA error message exists
        if "incorrect captcha" in page_text or "wrong code" in page_text or "invalid captcha" in page_text:
            print("CAPTCHA error found - Failed")
            return False
        
        # If nothing clear, return uncertain
        print("Result uncertain")
        return None
    
    def save_screenshot(self, label="screenshot"):
        # ================================================================================================================================
        # Saving screenshot 
        # ================================================================================================================================  
        try:
            Path("data/solved").mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"data/solved/{label}_{timestamp}.png"
            self.driver.save_screenshot(path)
            print(f"Screenshot saved: {path}")
            return path
        
        except Exception as e:
            return None

    def solve_with_model(self, url, model_callback):
        # ================================================================================================================================
        # Complete workflow with model
        # ================================================================================================================================
        result = {
            'url': url,
            'captcha_found': False,
            'solution': None,
            'success': None
        }
        
        try:
            # Step 1: Load page
            print("1. Loading page")
            self.driver.get(url)
            self.initial_url = url
            time.sleep(2)
            print(f"Loaded {self.driver.title}")
            
            # Step 2: Find and save CAPTCHA with CaptchaScraper
            print("2. Looking for CAPTCHA")
            if not self.captcha_extracting():
                print("No CAPTCHA found")
                return result
            
            result['captcha_found'] = True
            captcha_path = self.save_captcha()
            print(f"CAPTCHA saved")
            
            # Step 3: Get solution from model
            print("3. Sending to model")
            solution = model_callback(captcha_path)
            result['solution'] = solution
            print(f"Got solution: '{solution}'")
            
            # Step 4: Find input field and fill it. This is solver exemple - input is tapped automatically, then we are using API orchestration.
            print("4. Filling CAPTCHA") 
            if not self.search_input_field():
                print("Could not find input field")
                return result
            
            if not self.tap_solution(solution): 
                print("Could not fill solution")
                return result
            
            # Step 5: Submit
            print("5. Submitting the answer")
            if not self.submit_captcha():
                print("Could not submit")
                return result
            
            # Step 6: Check if it worked
            print("6. Checking result")
            result['success'] = self.check_success()
            
            # Save metadata
            if captcha_path:
                self.save_metadata(captcha_path, url)
            self.save_screenshot(label="final_result")
            # Show result
            print("FINAL RESULTS")
            if result['success']:
                print("SUCCESS")
            elif result['success'] is False:
                print("FAILED")
            else:
                print("UNCERTAIN")
            return result
            
        except Exception as e:
            return result


def main():
    solver = CaptchaSolver()

    def demonstration_model(image_path):
        print(f"Model processing: {image_path}")
        solution = "abcde"
        return solution
    
    # Solve CAPTCHA
    result = solver.solve_with_model(
        url="https://rutracker.org/forum/profile.php?mode=register",
        model_callback=demonstration_model,
    )
    
    # Print result
    print(json.dumps(result, indent=2, default=str))

    # Close browser
    input("Press Enter to close browser")
    solver.close()
    print("Browser closed")


if __name__ == "__main__":
    main()
