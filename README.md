# amazonscraper
# Amazon Scraper & WooCommerce Importer

This project demonstrates how to scrape product URLs from multiple Amazon domains using a Python script, then import or integrate the scraped data into a WordPress WooCommerce store.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [1. Prepare `words.txt`](#1-prepare-wordstxt)
  - [2. Run the Scraper](#2-run-the-scraper)
  - [3. WooCommerce Import](#3-woocommerce-import)
- [Notes](#notes)
- [License](#license)

## Prerequisites
1. **Python 3.x** installed on your local machine or server.
2. **requests** and **BeautifulSoup4** Python libraries (install via `pip install requests beautifulsoup4`).
3. A working **WordPress + WooCommerce** setup.
4. A **WooCommerce product importer** plugin or a built-in importer that can read CSV or a custom format.

## Installation

1. **Clone or download** this repository into your preferred directory.
2. Navigate to the folder with the Python script, for example:
   ```bash
   cd /path/to/amazon-scraper/
   Usage
Below is a **complete Python scraper** (in English) that uses a `words.txt` file (which you will fill with search words). The script will:

1. Read search terms from the `words.txt` file (one term per line).  
2. For each word, it will search on all the main Amazon domains.  
3. Scrape product links (those containing `"/dp/"`).  
4. Append those links to a file named `urls.txt`.  

> **Important Notes**  
> - Large-scale scraping may violate Amazon's Terms of Service and can lead to rate-limits or CAPTCHA.  
> - Use this script for **educational** and **demonstration** purposes only.  
> - To reduce the chance of being blocked, you may need to:  
>   - Increase the **time.sleep** between requests.  
>   - Use proxies and rotate IP addresses.  
>   - Handle CAPTCHA responses gracefully.

```python
# -*- coding: utf-8 -*-

import requests
import random
import time
from bs4 import BeautifulSoup

# A list of 20 different User-Agents to randomly choose from
USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/535.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/606.4.5 (KHTML, like Gecko) Version/12.1.1 Safari/606.4.5",
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.19 (KHTML, like Gecko) Ubuntu/11.10 Chrome/90.0.4444.5 Safari/535.19",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Windows NT 6.1; rv:32.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:85.0) Gecko/20100101 Firefox/85.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/90.0.4430.24 Safari/536.5",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/90.0.4430.24 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 OPR/74.0.3911.75",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:85.0) Gecko/20100101 Firefox/85.0",
    "Mozilla/5.0 (Linux; Android 10; SM-A505F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.66 Mobile Safari/537.36"
]

# Main Amazon domains to scrape
AMAZON_DOMAINS = [
    "amazon.com",
    "amazon.ca",
    "amazon.co.uk",
    "amazon.de",
    "amazon.es",
    "amazon.fr",
    "amazon.it",
    "amazon.nl",
    "amazon.sa",
    "amazon.ae",
    "amazon.com.au",
    "amazon.com.br",
    "amazon.sg",
    "amazon.com.tr",
    "amazon.co.jp",
    "amazon.in",
]

def read_words_from_file(filename):
    """
    Reads search terms from the given text file (one term per line).
    Returns a list of these terms.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f if line.strip()]
        return words
    except FileNotFoundError:
        print(f"File '{filename}' not found. Make sure it exists or provide the correct path.")
        return []

def scrape_amazon(url, output_file='urls.txt'):
    """
    Sends a GET request to the given Amazon URL, searches for product links
    containing '/dp/', and appends these links to the specified output file.
    """
    user_agent = random.choice(USER_AGENTS)
    headers = {"User-Agent": user_agent}

    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Request error for URL '{url}': {e}")
        return

    if response.status_code != 200:
        print(f"Request failed with status {response.status_code} for URL '{url}'")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # Find all <a> tags containing "/dp/" in the href
    links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if "/dp/" in href:
            # If it's a relative link, prepend the base domain
            if not href.startswith("http"):
                base_url = url.split("/")[0] + "//" + url.split("/")[2]
                href = base_url + href
            links.append(href)

    if not links:
        print(f"No product links found on {url}.")
        return

    # Append each link to the output file
    with open(output_file, "a", encoding="utf-8") as f:
        for link in links:
            f.write(link + "\n")

    print(f"Found {len(links)} links on {url}, appended to '{output_file}'.")

def scrape_multiple_domains(search_terms, output_file='urls.txt'):
    """
    Loops over each search term and each Amazon domain,
    constructing a search URL, then calls 'scrape_amazon' to handle the scraping.
    """
    for term in search_terms:
        for domain in AMAZON_DOMAINS:
            search_url = f"https://{domain}/s?k={term}"
            print(f"Searching '{term}' on: {search_url}")

            scrape_amazon(url=search_url, output_file=output_file)

            # Short delay between requests to reduce chance of blocking
            time.sleep(random.uniform(1, 3))

if __name__ == "__main__":
    # Read your search terms from words.txt
    search_list = read_words_from_file("words.txt")

    # If there are no search terms, exit
    if not search_list:
        print("No search terms found or file missing. Exiting.")
    else:
        # Run the scraper with the search terms, storing results in urls.txt
        scrape_multiple_domains(search_terms=search_list, output_file="urls.txt")
```

### How to use this script:

1. **Create/Edit `words.txt`**  
   - Put one search term on each line. For example:
     ```
     laptop
     smartphone
     camera
     headphones
     book
     ```
   - Ensure that `words.txt` is in the same folder as the Python script (or provide a full path).

2. **Run the script**  
   - In a terminal/command line, type:
     ```bash
     python amazon_scraper.py
     ```
   - The script will read each word in `words.txt`, iterate through all the Amazon domains, and search for those terms.

3. **Check the `urls.txt` file**  
   - The script will append any product links found (`/dp/`) to `urls.txt`.  
   - If you want a fresh file for each run, you can manually delete `urls.txt` before running again or open it in write mode (`"w"`) instead of append mode (`"a"`).

### Additional tips:
- If you plan to do many searches (thousands of words × multiple domains), **increase the sleep time** or **rotate proxies**. Amazon tends to block repeated or suspicious scraping activity.  
- Consider adding **CAPTCHA** detection logic, because Amazon often shows CAPTCHAs if it detects high-volume automated requests.  
- The script is for **educational** and **demonstration** purposes only. Use responsibly.
