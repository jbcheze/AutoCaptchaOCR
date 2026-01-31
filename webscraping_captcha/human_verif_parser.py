# ================================================================================================================================
# HUMAN VERIFICATION KEYWORDS PARSER FROM CSV DATASET
# The goal is to scrape verification keywords from R-U-A-Robot GitHub public repo to extract keywords for the main scraper script.
# ================================================================================================================================

import requests
import csv

# R-U-A-Robot is a public open source GitHub containing datasets with human verification phrases 
url = "https://raw.githubusercontent.com/DNGros/R-U-A-Robot/master/data/v1.0.0/"
verification_keywords = []

# ================================================================================================================================
# Download CSV files from R-U-A-Robot GitHub repo
# ================================================================================================================================
def download_csv(file):
    csv_url = url + file
    
    try:
        response = requests.get(csv_url, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Error {response.status_code}")
            return None
   
    except Exception as e:
        print(f"Error {e}")
        return None


# ================================================================================================================================
# Extract keywords from CSV "text" column
# ================================================================================================================================
def extract_keywords(csv_str):
    if not csv_str:
        return set()

    keywords = set()
    
    try:
        # Split CSV into lines
        lines = csv_str.strip().split('\n')
        reader = csv.DictReader(lines)

        for row in reader:
                text = row.get('text', '').strip()
                
                # Filtering too short/long phrases
                if 2 < len(text) < 30:
                    keywords.add(text.lower())
    except Exception as e:
        print(f"Error: {e}")
    
    return keywords


# ================================================================================================================================
# Parse all CSV files (3 groups of pop ups: ambiguous, negative, positive)
# ================================================================================================================================
store_keywords = set()

# There are 3 groups: amb = ambiguous, neg = negative, pos = positive
csv_files = [
    'amb.train.csv', 'amb.test.csv', 'amb.val.csv',
    'neg.train.csv', 'neg.test.csv', 'neg.val.csv',
    'pos.train.csv', 'pos.test.csv', 'pos.val.csv'
]

for csv_file in csv_files:
    print(csv_file)
    csv_content = download_csv(csv_file)
    
    if csv_content:
        # Extracting keywords from each csv
        keywords = extract_keywords(csv_content)
        store_keywords.update(keywords)
    else:
        print(f"Failed to download {csv_file}")

print(f"Total unique keywords: {len(store_keywords)}")


# ================================================================================================================================
# Filtering keywords (2418 words are too many - filtering only verification-related phrases) 
# ================================================================================================================================
verification_words = [
    'robot', 'bot', 'chatbot', 'machine', 'computer',
    'human', 'verify', 'prove', 'convince', 'confirm', 'check',
    'i am', "i'm", 'not a', 'i am not', "i'm not",
    'are you', 'you are', 'you\'re', 'you\'re not', 'you are not',
    'weird', 'spam', 'suspicious', 'suspicion',
    'security', 'captcha', 'challenge', 'test', 'checkup',
    'access', 'blocked', 'unblock', 'restriction', 'restricted',
] # Github Copilot propositions

filtered_keywords = set()

for keyword in store_keywords:
    found=False
    for word in verification_words:
        if word in keyword:
            found=True
            break
    if found:
        filtered_keywords.add(keyword)

print(f"Filtered keywords: {len(filtered_keywords)}")


# ================================================================================================================================
# Adding manual phrases (standard common CAPTCHA phrases)
# ================================================================================================================================
manual_keywords = [
    "i'm not a robot",
    "i am not a robot",
    'verify you are human',
    'are you a robot',
    'prove you are human',
    'complete the captcha',
    'security check',
    'human verification',
    'please complete the security check',
    'checking your browser',
    'just a moment',
    'please verify you are human',
    'to continue, please verify you are human'
] # Github Copilot propositions

filtered_keywords.update(manual_keywords)
verification_keywords = sorted(filtered_keywords)
print(f"Final total: {len(verification_keywords)} keywords") # 1447 keywords

# ================================================================================================================================
# Saving in utils
# ================================================================================================================================
with open('webscraping_captcha/utils_captcha/human_verification_keywords.py', 'w', encoding='utf-8') as file:
    file.write('# VERIFICATION KEYWORDS\n')
    file.write('verification_keywords = [\n')
    
    for keyword in verification_keywords:
        keyword_escaped = keyword.replace("'", "\\'")
        file.write(f"'{keyword_escaped}',\n")
    
    file.write(']\n')
