# ================================================================================================================================
# CONSENT SELECTOR PARSER
# The goal is to scrape button selectors from Consent-O-Matic GitHub public repo to extract selectors for the main scraper script.
# ================================================================================================================================

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import json

# Consent-O-Matic is a public open source GitHub containing rule lists for CMPs (ref. rules.json in utils)
url = "https://github.com/cavi-au/Consent-O-Matic/tree/master/rules"
absolute_url = "https://raw.githubusercontent.com/cavi-au/Consent-O-Matic/master/rules/"
css_selectors = []
xpath_selectors = []

def get_text_if_exist(element):
    if element:
        return element.text.strip()
    return None

# ================================================================================================================================
# Chrome webdriver config
# ================================================================================================================================
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")

driver = webdriver.Chrome(options=options) 
wait = WebDriverWait(driver, 10)

# ================================================================================================================================
# Get all JSON files from the GitHub repo with Selenium + bs4
# ================================================================================================================================
def get_json_files(driver, wait, url):
    # Using Selenium to render JS
    try:
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.Link--primary")))
        
       # Parse with bs4
        html = driver.page_source
        print(f"Page HTML length: {len(html)} char") 
        soup = BeautifulSoup(html, 'lxml')
        
        # Searching all JSON links with class 'Link--primary'
        links = soup.find_all('a', class_='Link--primary')
        json_files = []

        for link in links:
            link_url=link.get('href')
            if link_url and '.json' in link_url:
                file=link.text.strip()
                if file:
                    json_files.append(file)
        return json_files 
    
    except Exception as e:
        return []
    
    finally:
        driver.quit()

json_files = get_json_files(driver,wait,url) # 408 files are too long to check, a) long with bs4 b) giant platforms do not use text captcha anymore, 

# ================================================================================================================================
# Filtering main JSON files by keywords (ookie related & top cookie governance platforms 
# ================================================================================================================================
keywords = ['consent', 'cookie', 'cookiebot', 'cookiefirst', 'cookiepro', 'onetrust', 'quantcast', 'consentmanager', 'google', 'cloudflare', 'pwc', 'cookieyes',  'cookiehub', 'popup']

main_files = []

for file in json_files:
    file_lower=file.lower()
    for keyword in keywords:
        if keyword in file_lower:
            main_files.append(file)
            break
print(f"Filtered: {len(main_files)} main files from {len(json_files)} total on GitHub repo") # 408 to 68 files

# ================================================================================================================================
# Parsing JSON files to extract CSS selectors
# ================================================================================================================================
for file in main_files:
    json_url = absolute_url + file
    print(file) 
    
    json_response = requests.get(json_url)
    if json_response.status_code == 200:
        data = json.loads(json_response.text)
        
        # Extract selectors
        for name, json_file in data.items():
            if name.startswith('$schema'): # skip schema info, first loop is for detecting not for solving (type css)
                continue
            
            # methods -> action -> type -> target -> selector
            if 'methods' in json_file:
                for method in json_file['methods']:
                    if 'action' in method:
                        action = method['action']
                        
                        target = action.get('target', {})
                        selector = target.get('selector', "")
                        
                        if (selector.startswith('#') or selector.startswith('.')) and selector not in css_selectors:
                            css_selectors.append(selector)
    else:
        print(f"Error: {json_response.status_code}")

print(f"Parsed {len(css_selectors)} selectors")


# ================================================================================================================================
# Adding XPATH selectors manually (GITHUB COPILOT)
# ================================================================================================================================
# During demo testing we had searched for international sites, hence adding simple button XPATH selectors in different languages
xpath_selectors = [
    "//button[contains(text(),'Accept')]", # button
    "//button[contains(text(),'Accept all')]",
    "//button[contains(text(),'I agree')]",
    "//button[contains(text(),'I accept')]",
    "//button[contains(text(),'Agree')]",
    "//button[contains(text(),'Accepter')]",
    "//button[contains(text(),'Tout accepter')]",
    "//button[contains(text(),'Aceptar')]",
    "//button[contains(text(),'Acepto')]",
    "//a[contains(text(),'Accepter')]",
    "//a[contains(text(),'Aceptar')]",
    "//a[contains(text(),'Accept')]", # links
    "//a[contains(text(),'I accept')]",
    "//a[contains(text(),'Agree')]",
    "//input[@value='Accept']", # input
    "//input[@value='Accept']",
    "//input[@value='Accepter']",
    
    # Russian (for the real forum POC site we tested (rutracker.org))
    "//input[@value='Я согласен с этими правилами']"
]

print(f"{len(css_selectors)} CSS + {len(xpath_selectors)} XPath = {len(css_selectors)+len(xpath_selectors)} in total") # 37 CSS + 18 XPath = 55 in total

# Saving in utils
with open('src/webscraping/utils/consent_selectors.py', 'w', encoding='utf-8') as file:
    file.write('# CSS SELECTORS \n')
    file.write('css_selectors = [')
    for selector in css_selectors:
        selector = selector.replace("'", "\\'")
        file.write(f"'{selector}',")
    file.write(']\n')
    file.write('# XPATH SELECTORS \n')
    file.write('xpath_selectors = [')
    for selector in xpath_selectors:
        selector = selector.replace("'", "\\'")
        file.write(f"'{selector}',")
    file.write(']\n')