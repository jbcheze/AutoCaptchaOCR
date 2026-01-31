# ================================================================================================================================
# CAPTCHA SOLVER
# The goal is to solve detected CAPTCHA - detect input field, tap the response from the model & submit it
# ================================================================================================================================

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import os
from datetime import datetime
import time
import random
from utils.consent_selectors import css_selectors, xpath_selectors
from captcha_scraper import CaptchaScraper

class CaptchaSolver(CaptchaScraper):
    # ================================================================================================================================
    # Inherit from CaptchaScraper
    # ================================================================================================================================
    def __init__(self, chrome_driver_path=None):
        super().__init__(chrome_driver_path)
        self.input_field = None
        self.initial_url = None
        
    def find_captcha_input_field(self):
        # ================================================================================================================================
        # Find input field for CAPTCHA
        # ================================================================================================================================
        print("Looking for input field...")
        
        # List of possible input selectors
        input_selectors = [
            (By.ID, "captcha"),
            (By.ID, "captcha_code"),
            (By.ID, "code"),
            (By.ID, "cap_code"),
            (By.NAME, "cap_code"),
            (By.NAME, "captcha"),
            (By.NAME, "code"),
            (By.XPATH, "//input[contains(@name, 'cap')]"),
            (By.XPATH, "//input[contains(@id, 'cap')]"),
            (By.XPATH, "//input[@type='text']"),
        ]
        
        # Try each selector
        for selector_type, selector in input_selectors:
            try:
                elements = self.driver.find_elements(selector_type, selector)
                
                if elements:
                    for element in elements:
                        try:
                            # Check if element is visible and enabled
                            if element.is_displayed() and element.is_enabled():
                                self.input_field = element
                                
                                # Highlight field in red
                                script = "arguments[0].style.border='3px solid red'"
                                self.driver.execute_script(script, element)
                                
                                print(f"Input field found!")
                                return element
                        except:
                            continue
            except:
                continue
        
        # Try to find input near CAPTCHA
        if self.captcha_element:
            print("Searching near CAPTCHA...")
            try:
                current = self.captcha_element
                
                # Check parent elements
                for level in range(5):
                    try:
                        parent = current.find_element(By.XPATH, "..")
                        inputs = parent.find_elements(By.TAG_NAME, "input")
                        
                        for inp in inputs:
                            try:
                                if inp.is_displayed() and inp.is_enabled():
                                    inp_type = inp.get_attribute('type')
                                    
                                    if inp_type in ['text', '']:
                                        self.input_field = inp
                                        
                                        script = "arguments[0].style.border='3px solid red'"
                                        self.driver.execute_script(script, inp)
                                        
                                        print(f"Input found near CAPTCHA!")
                                        return inp
                            except:
                                continue
                        
                        current = parent
                    except:
                        break
            except:
                pass
        
        print("No input field found")
        return None
    

    def fill_captcha_solution(self, solution, human_like=True):
        # ================================================================================================================================
        # Fill CAPTCHA solution with human-like typing
        # ================================================================================================================================
        if not self.input_field:
            print("No input field")
            return False
        
        try:
            # Pause before typing (like human thinking)
            if human_like:
                think_time = random.uniform(0.5, 1.5)
                print(f"Thinking {think_time:.1f}s...")
                time.sleep(think_time)
            
            # Click on input field
            try:
                self.input_field.click()
                if human_like:
                    time.sleep(random.uniform(0.1, 0.3))
            except:
                pass
            
            # Clear field
            self.input_field.clear()
            time.sleep(0.2)
            
            # Type solution
            if human_like:
                print("Typing solution")
                
                for i in range(len(solution)):
                    char = solution[i]
                    
                    # Random typing speed
                    delay = random.uniform(0.1, 0.3)
                    if random.random() < 0.15:
                        delay = delay + random.uniform(0.3, 0.8)
                    
                    # Type character
                    self.input_field.send_keys(char)
                    time.sleep(delay)
                    
                    # Rarely make typo
                    if random.random() < 0.05 and i < len(solution) - 1:
                        print("  Typo! Fixing...")
                        time.sleep(0.1)
                        self.input_field.send_keys(Keys.BACKSPACE)
                        time.sleep(0.3)
                        self.input_field.send_keys(char)
                        time.sleep(0.2)
                
                # Pause after typing (reviewing)
                review_time = random.uniform(0.3, 0.8)
                print(f"Reviewing {review_time:.1f}s...")
                time.sleep(review_time)
            
            else:
                # Fast typing
                for char in solution:
                    self.input_field.send_keys(char)
                    time.sleep(0.05)
            
            print(f"Solution entered: '{solution}'")
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            return False
    

    def submit_captcha(self):
        # ================================================================================================================================
        # Submit CAPTCHA
        # ================================================================================================================================
        print("Submitting...")
        
        # List of submit button selectors
        submit_selectors = [
            "//button[contains(text(), 'Submit')]",
            "//button[contains(text(), 'Verify')]",
            "//button[contains(text(), 'Valider')]",
            "//button[contains(text(), 'Send')]",
            "//button[contains(text(), 'Envoyer')]",
            "//button[@type='submit']",
            "//input[@type='submit']",
        ]
        
        # Try each selector
        for selector in submit_selectors:
            try:
                buttons = self.driver.find_elements(By.XPATH, selector)
                
                if buttons:
                    for button in buttons:
                        try:
                            if button.is_displayed() and button.is_enabled():
                                button.click()
                                print("Submit button clicked")
                                time.sleep(1)
                                return True
                        except:
                            continue
            except:
                continue
        
        # Try Enter key
        if self.input_field:
            try:
                self.input_field.send_keys(Keys.RETURN)
                print("Submitted via Enter")
                time.sleep(1)
                return True
            except Exception as e:
                print(f"Error: {e}")
                return False
        
        print("No submit method found")
        return False
    

    def check_captcha_success(self):
        # ================================================================================================================================
        # Check if CAPTCHA was solved successfully
        # ================================================================================================================================
        print("Checking result...")
        time.sleep(2)
        
        # Check current URL
        current_url = self.driver.current_url
        print(f"Current URL: {current_url}")
        
        # Check if URL changed (usually means success)
        if self.initial_url and current_url != self.initial_url:
            # Split URL into parts
            url_parts_before = self.initial_url.split('?')[0].split('/')
            url_parts_after = current_url.split('?')[0].split('/')
            
            # If main path changed
            if url_parts_before != url_parts_after:
                print("URL changed - Success!")
                return True
        
        # Get page text
        page_source = self.driver.page_source.lower()
        
        
        # Check for form errors (CAPTCHA correct but other fields missing)
        form_errors = [
            "username is required",
            "email is required",
            "password is required",
            "required field",
            "champ requis",
        ]
        
        # If there's an error message
        if "error" in page_source or "erreur" in page_source or "ошибка" in page_source:
            # Check if it's about form fields
            found_form_error = False
            
            for field_error in form_errors:
                if field_error in page_source:
                    print(f"Form error: {field_error}")
                    print("CAPTCHA appears correct")
                    found_form_error = True
                    break
            
            if found_form_error:
                return True
            else:
                print("Generic error - uncertain")
                return None
        
        # Check for success messages
        success_phrases = [
            "message sent",
            "message envoyé",
            "votre message a été envoyé",
            "merci pour votre message",
            "thank you for your message",
            "successfully sent",
        ]
        
        for phrase in success_phrases:
            if phrase in page_source:
                print(f"Success phrase: '{phrase}'")
                return True
        
        # Check if CAPTCHA disappeared
        try:
            captcha_images = self.driver.find_elements(By.XPATH, "//img")
            captcha_found = False
            
            for img in captcha_images:
                try:
                    width = img.size['width']
                    height = img.size['height']
                    
                    # Check if CAPTCHA-sized
                    if 30 < width < 400 and 30 < height < 300:
                        src = (img.get_attribute('src') or '').lower()
                        
                        if 'logo' not in src and 'banner' not in src:
                            captcha_found = True
                            break
                except:
                    continue
            
            if not captcha_found and self.captcha_element:
                print("CAPTCHA disappeared - likely success")
                return True
        except:
            pass
        
        # No clear result
        print("UNCERTAIN")
        return None
    

    def save_screenshot(self, label="screenshot"):
        """Save screenshot"""
        try:
            # Create directory
            if not os.path.exists("data/solved"):
                os.makedirs("data/solved")
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"data/solved/{label}_{timestamp}.png"
            
            # Save screenshot
            self.driver.save_screenshot(path)
            print(f"Screenshot: {path}")
            
            return path
        
        except Exception as e:
            print(f"Screenshot error: {e}")
            return None
    

    def solve_with_model(self, url, model_callback, human_like=True, max_retries=3):
        # ================================================================================================================================
        # Complete workflow with model and RETRY logic
        # If CAPTCHA refreshes during model processing, automatically retry with new CAPTCHA
        # This solves the Streamlit "double page load" problem
        # ================================================================================================================================
        
        for attempt in range(max_retries):
            print(f"\n{'='*70}")
            print(f"[ATTEMPT {attempt + 1}/{max_retries}]")
            print(f"{'='*70}")
            
            result = {
                'url': url,
                'captcha_found': False,
                'captcha_path': None,
                'input_found': False,
                'solution': None,
                'filled': False,
                'submitted': False,
                'success': None,
                'error': None,
                'attempt': attempt + 1
            }
            
            try:
                # Step 1: Load page (only on first attempt)
                if attempt == 0:
                    print(f"\n{'='*70}")
                    print("[STEP 1] Loading page...")
                    
                    self.driver.get(url)
                    self.initial_url = url
                    
                    try:
                        wait_condition = EC.presence_of_element_located((By.TAG_NAME, "body"))
                        self.wait.until(wait_condition)
                        
                        print(f"Page loaded: {self.driver.title}")
                        time.sleep(1)
                    
                    except TimeoutException:
                        print("Timeout loading page")
                        result['error'] = 'page_load_timeout'
                        continue
                else:
                    # On retry: refresh page for new CAPTCHA
                    print(f"\n{'='*70}")
                    print("[RETRY] Refreshing page for new CAPTCHA...")
                    self.driver.refresh()
                    time.sleep(2)
                
                # Step 2: Extract CAPTCHA
                print(f"\n{'='*70}")
                print("[STEP 2] Extracting CAPTCHA...")
                
                captcha_found = self.captcha_extracting()
                result['captcha_found'] = captcha_found
                
                if not captcha_found:
                    print("No CAPTCHA found")
                    result['error'] = 'no_captcha_found'
                    if attempt < max_retries - 1:
                        print("Retrying...")
                        continue
                    else:
                        return result
                
                # Step 3: Save CAPTCHA
                print(f"\n{'='*70}")
                print("[STEP 3] Saving CAPTCHA...")
                
                captcha_path = self.save_captcha()
                result['captcha_path'] = captcha_path
                
                if not captcha_path:
                    print("Could not save CAPTCHA")
                    result['error'] = 'captcha_save_failed'
                    if attempt < max_retries - 1:
                        print("Retrying...")
                        continue
                    else:
                        return result
                
                print(f"CAPTCHA saved: {captcha_path}")
                
                # Step 4: Get solution from model
                print(f"\n{'='*70}")
                print("[STEP 4] Getting solution from model...")
                
                try:
                    solution = model_callback(captcha_path)
                    result['solution'] = solution
                    print(f"Model returned: '{solution}'")
                
                except Exception as e:
                    print(f"Model error: {e}")
                    result['error'] = f'model_error: {str(e)}'
                    if attempt < max_retries - 1:
                        print("Retrying with new CAPTCHA...")
                        continue
                    else:
                        return result
                
                # Step 5: Find input field
                print(f"\n{'='*70}")
                print("[STEP 5] Finding input field...")
                
                input_found = self.find_captcha_input_field()
                result['input_found'] = input_found
                
                if not input_found:
                    print("Cannot proceed without input field")
                    result['error'] = 'input_field_not_found'
                    if attempt < max_retries - 1:
                        print("Retrying...")
                        continue
                    else:
                        return result
                
                # Step 6: Fill solution (FAST - no delays to minimize CAPTCHA refresh risk)
                print(f"\n{'='*70}")
                print("[STEP 6] Filling solution...")
                
                # On retry attempts, use FAST typing (no human_like delays)
                use_human_like = human_like if attempt == 0 else False
                
                if use_human_like:
                    print("Using human-like typing")
                else:
                    print("Using fast typing (retry mode)")
                
                filled = self.fill_captcha_solution(solution, human_like=use_human_like)
                result['filled'] = filled
                
                if not filled:
                    print("Failed to fill solution")
                    result['error'] = 'fill_solution_failed'
                    if attempt < max_retries - 1:
                        print("Retrying...")
                        continue
                    else:
                        return result
                
                # Step 7: Submit
                print(f"\n{'='*70}")
                print("[STEP 7] Submitting...")
                
                submitted = self.submit_captcha()
                result['submitted'] = submitted
                
                if not submitted:
                    print("Failed to submit")
                    result['error'] = 'submit_failed'
                    if attempt < max_retries - 1:
                        print("Retrying...")
                        continue
                    else:
                        return result
                
                # Step 8: Check result
                print(f"\n{'='*70}")
                print("[STEP 8] Checking result...")
                
                success = self.check_captcha_success()
                result['success'] = success
                
                # If success or uncertain (not explicit failure), consider it done
                if success or success is None:
                    # Save metadata
                    if captcha_path:
                        self.save_metadata(captcha_path, url)
                    
                    # Switch back to default content
                    self.driver.switch_to.default_content()
                    
                    # Print summary
                    print(f"\n{'='*70}")
                    print(f"SUMMARY (Attempt {attempt + 1}):")
                    print(f"{'='*70}")
                    
                    if result['captcha_found']:
                        print(f"  CAPTCHA found:  YES")
                    else:
                        print(f"  CAPTCHA found:  NO")
                    
                    if result['input_found']:
                        print(f"  Input found:    YES")
                    else:
                        print(f"  Input found:    NO")
                    
                    print(f"  Solution:       {result['solution']}")
                    
                    if result['filled']:
                        print(f"  Filled:         YES")
                    else:
                        print(f"  Filled:         NO")
                    
                    if result['submitted']:
                        print(f"  Submitted:      YES")
                    else:
                        print(f"  Submitted:      NO")
                    
                    if result['success']:
                        print(f"  Success:        YES")
                    elif result['success'] is False:
                        print(f"  Success:        NO")
                    else:
                        print(f"  Success:        UNCERTAIN")
                    
                    print(f"  Attempts:       {attempt + 1}")
                    
                    if result['error']:
                        print(f"  Error:          {result['error']}")
                    
                    print(f"{'='*70}")
                    
                    return result
                
                else:
                    # Explicit failure - retry if attempts remaining
                    print(f"❌ Failed on attempt {attempt + 1}")
                    result['error'] = 'captcha_verification_failed'
                    
                    if attempt < max_retries - 1:
                        print("Retrying with new CAPTCHA...")
                        continue
                    else:
                        return result
            
            except Exception as e:
                print(f"Error on attempt {attempt + 1}: {e}")
                import traceback
                traceback.print_exc()
                result['error'] = f'exception: {str(e)}'
                
                if attempt < max_retries - 1:
                    print("Retrying...")
                    continue
                else:
                    return result
            
            finally:
                # Always switch back
                try:
                    self.driver.switch_to.default_content()
                except:
                    pass
        
        # If all retries exhausted
        print(f"\n❌ All {max_retries} attempts failed")
        return result


def main():
    print("="*70)
    print("CAPTCHA SOLVER - WITH MODEL & RETRY LOGIC")
    print("="*70)
    
    # Create solver
    solver = CaptchaSolver()
    
    # Example model (replace with your actual model)
    def example_model(image_path):
        print(f"\nModel processing: {image_path}")
        print("Look at the CAPTCHA image in data/raw/")
        solution = input("Enter CAPTCHA text: ")
        return solution
    
    # Solve CAPTCHA with retry logic (max 3 attempts)
    result = solver.solve_with_model(
        url="https://rutracker.org/forum/profile.php?mode=register",
        model_callback=example_model,
        human_like=True,
        max_retries=3
    )
    
    # Print result
    print("\n" + "="*70)
    print("FINAL RESULT:")
    print("="*70)
    print(json.dumps(result, indent=2, default=str))
    print("="*70)
    
    if result['success']:
        print(f"\n✅ SUCCESS! CAPTCHA solved on attempt {result['attempt']}!")
    elif result['success'] is False:
        print(f"\n❌ FAILED after {result['attempt']} attempts")
    else:
        print(f"\n❓ UNCERTAIN after {result['attempt']} attempts")
    
    # Close browser
    input("\nPress Enter to close browser...")
    solver.close()
    print("Browser closed")


if __name__ == "__main__":
    main()
