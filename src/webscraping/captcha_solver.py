# ================================================================================================================================
# CAPTCHA SOLVER
# ================================================================================================================================

import random
import json
import time
from datetime import datetime
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from src.webscraping.captcha_scraper import CaptchaScraper


class CaptchaSolver(CaptchaScraper):

    def __init__(self, chrome_driver_path=None):
        super().__init__(chrome_driver_path)
        self.input_field = None
        self.initial_url = None


    # =====================================================================
    # INPUT FIELD SEARCH
    # =====================================================================

    def search_input_field(self):

        print("Searching input field")

        input_field_names = ["captcha", "code", "type_code", "captcha_code", "cap_code"]

        # By ID
        for name in input_field_names:
            try:
                element = self.driver.find_element(By.ID, name)
                if element.is_displayed():
                    self.input_field = element
                    print(f"Found by ID: {name}")
                    return element
            except:
                pass

        # By NAME
        for name in input_field_names:
            try:
                element = self.driver.find_element(By.NAME, name)
                if element.is_displayed():
                    self.input_field = element
                    print(f"Found by NAME: {name}")
                    return element
            except:
                pass

        # Near CAPTCHA
        if self.captcha_element:

            try:
                current = self.captcha_element

                for _ in range(5):

                    parent = current.find_element(By.XPATH, "..")
                    inputs = parent.find_elements(By.TAG_NAME, "input")

                    for inp in inputs:

                        if inp.is_displayed() and inp.is_enabled():

                            if inp.get_attribute("type") in ["text", ""]:

                                self.input_field = inp
                                print("Found near CAPTCHA")
                                return inp

                    current = parent

            except:
                pass

        # Last chance
        try:

            inputs = self.driver.find_elements(By.XPATH, "//input[@type='text']")

            for inp in inputs:

                if not inp.is_displayed():
                    continue

                self.input_field = inp
                print("Found generic text input")
                return inp

        except:
            pass

        print("No input found")
        return None


    # =====================================================================
    # TYPING
    # =====================================================================

    def tap_solution(self, answer):

        if not self.input_field:
            return False

        try:

            self.input_field.click()
            time.sleep(0.3)

            self.input_field.clear()
            time.sleep(0.2)

            print("Human typing...")

            for char in answer:
                self.input_field.send_keys(char)
                time.sleep(random.uniform(0.15, 0.4))

            return True

        except Exception as e:
            print("Typing error:", e)
            return False


    def fast_solution(self, answer):

        try:
            self.input_field.clear()
            self.input_field.send_keys(answer)
            return True

        except:
            return False


    # =====================================================================
    # SUBMIT
    # =====================================================================

    def submit_captcha(self):

        print("Submitting")

        try:

            btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")

            if btn.is_displayed():
                btn.click()
                time.sleep(1)
                return True

        except:
            pass

        if self.input_field:
            try:
                self.input_field.send_keys(Keys.RETURN)
                time.sleep(1)
                return True
            except:
                pass

        print("Submit failed")
        return False


    # =====================================================================
    # SUCCESS CHECK
    # =====================================================================

    def check_success(self):

        time.sleep(2)

        url = self.driver.current_url

        if self.initial_url and url != self.initial_url:
            return True

        page = self.driver.page_source.lower()

        if any(w in page for w in ["success", "thank you", "merci"]):
            return True

        if any(e in page for e in ["wrong captcha", "invalid captcha", "incorrect"]):
            return False

        return None


    # =====================================================================
    # SCREENSHOT
    # =====================================================================

    def save_screenshot(self, label="result"):

        try:

            Path("data/solved").mkdir(parents=True, exist_ok=True)

            name = datetime.now().strftime("%Y%m%d_%H%M%S")

            path = f"data/solved/{label}_{name}.png"

            self.driver.save_screenshot(path)

            return path

        except:
            return None


    # =====================================================================
    # MAIN SOLVER (CORRECTED)
    # =====================================================================

    def solve_with_model(self, url, model_callback, human_like=True):

        """
        Page is ALREADY loaded by API
        Do NOT reload here
        """

        result = {
            "url": url,
            "captcha_found": False,
            "captcha_path": None,
            "solution": None,
            "success": None,
        }

        try:

            # STEP 1 — NO RELOAD
            print("[1] Using already loaded page")

            self.initial_url = self.driver.current_url


            try:
                self.wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except TimeoutException:
                print("Timeout")
                return result


            # STEP 2 — CAPTCHA
            print("[2] Extracting CAPTCHA")

            found = self.extract_captcha()
            result["captcha_found"] = found

            if not found:
                return result


            # STEP 3 — SAVE IMAGE
            print("[3] Saving CAPTCHA")

            path = self.save_captcha_image()
            result["captcha_path"] = path

            if not path:
                return result


            # STEP 4 — OCR
            print("[4] Solving")

            solution = model_callback(path)
            result["solution"] = solution


            # STEP 5 — INPUT
            print("[5] Filling")

            if not self.search_input_field():
                return result

            if human_like:

                if not self.tap_solution(solution):
                    return result

            else:

                if not self.fast_solution(solution):
                    return result


            # STEP 6 — SUBMIT
            print("[6] Submitting")

            if not self.submit_captcha():
                return result


            # STEP 7 — CHECK
            print("[7] Checking")

            result["success"] = self.check_success()


            if path:
                self.save_metadata(path, url)

            self.save_screenshot("final")


            return result


        except Exception as e:

            print("Solver error:", e)
            return result


# =====================================================================
# DEMO
# =====================================================================

def main():

    solver = CaptchaSolver()

    def demo_model(image):
        print("Processing:", image)
        return "abcde"

    solver.driver.get(
        "https://rutracker.org/forum/profile.php?mode=register"
    )

    result = solver.solve_with_model(
        url="https://rutracker.org/forum/profile.php?mode=register",
        model_callback=demo_model,
        human_like=True,
    )

    print(json.dumps(result, indent=2))

    input("Press Enter to close")

    solver.close()


if __name__ == "__main__":
    main()