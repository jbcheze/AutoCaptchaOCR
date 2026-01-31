# ======================================================================
# HUMAN VERIFICATION KEYWORDS PARSER
# ======================================================================
import requests
import csv


URL = "https://raw.githubusercontent.com/DNGros/R-U-A-Robot/master/data/v1.0.0/"


def download_csv(file):
    csv_url = URL + file

    try:
        response = requests.get(csv_url, timeout=10)

        if response.status_code == 200:
            return response.text

        print(f"Error {response.status_code}")
        return None

    except Exception as e:
        print(f"Error {e}")
        return None


def extract_keywords(csv_str):

    if not csv_str:
        return set()

    keywords = set()

    try:
        lines = csv_str.strip().split("\n")
        reader = csv.DictReader(lines)

        for row in reader:

            text = row.get("text", "").strip()

            if 2 < len(text) < 30:
                keywords.add(text.lower())

    except Exception as e:
        print(f"Error: {e}")

    return keywords


def main():

    # =====================================================
    # CSV FILES
    # =====================================================

    csv_files = [
        "amb.train.csv", "amb.test.csv", "amb.val.csv",
        "neg.train.csv", "neg.test.csv", "neg.val.csv",
        "pos.train.csv", "pos.test.csv", "pos.val.csv",
    ]

    store_keywords = set()

    # =====================================================
    # DOWNLOAD + PARSE
    # =====================================================

    for csv_file in csv_files:

        print(csv_file)

        csv_content = download_csv(csv_file)

        if not csv_content:
            print(f"Failed to download {csv_file}")
            continue

        keywords = extract_keywords(csv_content)
        store_keywords.update(keywords)

    print(f"Total unique keywords: {len(store_keywords)}")

    # =====================================================
    # FILTERING
    # =====================================================

    verification_words = [
        "robot", "bot", "chatbot", "machine", "computer",
        "human", "verify", "prove", "confirm", "check",
        "captcha", "security",
    ]

    filtered_keywords = set()

    for keyword in store_keywords:

        for word in verification_words:

            if word in keyword:
                filtered_keywords.add(keyword)
                break

    print(f"Filtered keywords: {len(filtered_keywords)}")

    # =====================================================
    # MANUAL ADD
    # =====================================================

    manual_keywords = [
        "i'm not a robot",
        "verify you are human",
        "complete the captcha",
        "security check",
        "checking your browser",
        "just a moment",
    ]

    filtered_keywords.update(manual_keywords)

    verification_keywords = sorted(filtered_keywords)

    print(f"Final total: {len(verification_keywords)} keywords")

    # =====================================================
    # SAVE FILE
    # =====================================================

    output_file = "src/webscraping/utils/human_verification_keywords.py"

    with open(output_file, "w", encoding="utf-8") as f:

        f.write("# VERIFICATION KEYWORDS\n")
        f.write("verification_keywords = [\n")

        for k in verification_keywords:

            k = k.replace("'", "\\'")
            f.write(f"    '{k}',\n")

        f.write("]\n")

    print(f"Saved to {output_file}")


# =========================================================
# PROTECTION
# =========================================================

if __name__ == "__main__":
    main()