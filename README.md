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
