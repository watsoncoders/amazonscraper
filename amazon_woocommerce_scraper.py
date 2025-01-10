# -*- coding: utf-8 -*-
"""
WooCommerce Direct DB Script (Demo)
-----------------------------------

This script:
1. Reads Amazon product links from 'urls.txt'.
2. Scrapes each product page for basic data (title, price, SKU, etc.).
3. Inserts/updates a WooCommerce product in the MySQL database directly.

WARNING:
- Direct DB manipulation is risky and bypasses official WP/WooCommerce APIs.
- Use at your own risk for demonstration only.
- Real-world usage should use WP/Woo REST API or official importers when possible.
"""

import requests
import random
import time
from bs4 import BeautifulSoup
import mysql.connector  # If you prefer pymysql, adjust accordingly.

# -------------- CONFIGURATION --------------
DB_HOST = "localhost"
DB_USER = "your_db_user"
DB_PASS = "your_db_password"
DB_NAME = "your_wp_database"
TABLE_PREFIX = "wp_"  # Change if your WP tables have a different prefix

# Potential random user-agents to reduce quick blocking
USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    # ... (add more if needed)
]

# -------------- FUNCTIONS --------------

def scrape_amazon_product(url):
    """
    Scrapes an Amazon product page and returns basic product data in a dict:
    {
        "title": str,
        "price": str,
        "sku": str,  # we will craft or parse an SKU (e.g., from ASIN)
        "description": str,
        "images": [list of image URLs], (optional)
    }
    Note: This function is purely demonstrative. Amazon's page structure changes frequently.
    """
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            print(f"[!] Failed to fetch {url}, status code {resp.status_code}")
            return None
    except requests.RequestException as e:
        print(f"[!] Request error for {url}: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Very basic scraping approach
    # Title: often in <span id="productTitle">
    title_elem = soup.find("span", id="productTitle")
    title = title_elem.get_text(strip=True) if title_elem else "No Title"

    # Price: often in <span id="priceblock_ourprice"> or something similar
    # This is not reliable as Amazon changes frequently, but let's demonstrate
    price_elem = soup.find("span", id=["priceblock_ourprice", "priceblock_dealprice"])
    price_text = price_elem.get_text(strip=True) if price_elem else "0.00"

    # Extract the ASIN if possible, from the URL or a hidden field
    # Typically an Amazon product URL might contain /dp/XXXXXXXXXX
    # We'll do a quick parse:
    sku = "N/A"
    parts = url.split("/dp/")
    if len(parts) > 1:
        # The ASIN might be up to 10 chars after /dp/
        asin_part = parts[1].split("/")[0]
        sku = asin_part.strip()

    # Description (very rough)
    # Maybe from the product description <div id="productDescription">?
    desc_elem = soup.find("div", id="productDescription")
    description = desc_elem.get_text(strip=True) if desc_elem else ""

    # (Optional) parse images, etc. For brevity, we skip that part.

    data = {
        "title": title,
        "price": price_text.replace("$", ""),  # remove $ sign for numeric usage
        "sku": sku,
        "description": description
    }
    return data


def connect_db():
    """Establishes and returns a MySQL connection using mysql.connector."""
    cnx = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )
    return cnx


def find_existing_product(cursor, sku):
    """
    Checks if there's a product with the same SKU in postmeta.
    We assume _sku in wp_postmeta = SKU.
    Returns the post_id if found, else None.
    """
    sql = f"""
    SELECT post_id 
    FROM {TABLE_PREFIX}postmeta
    WHERE meta_key = '_sku'
      AND meta_value = %s
    LIMIT 1
    """
    cursor.execute(sql, (sku,))
    row = cursor.fetchone()
    return row[0] if row else None


def create_new_product(cursor, cnx, product_data):
    """
    Inserts a new product row into wp_posts and relevant meta into wp_postmeta.
    Returns the new post_id.
    """
    title = product_data["title"]
    price = product_data["price"]
    sku = product_data["sku"]
    desc = product_data["description"]

    # 1) Insert into wp_posts
    # post_type = 'product'
    # post_status = 'publish' (or 'draft' if you prefer)
    sql_posts = f"""
    INSERT INTO {TABLE_PREFIX}posts
    (post_author, post_date, post_date_gmt, post_content, post_title, post_status, comment_status, ping_status, post_name, post_type, post_modified, post_modified_gmt)
    VALUES
    (1, NOW(), NOW(), %s, %s, 'publish', 'open', 'closed', %s, 'product', NOW(), NOW())
    """
    # post_name can be slugified or just use the SKU
    post_name = sku.lower() if sku else f"product-{int(time.time())}"
    cursor.execute(sql_posts, (desc, title, post_name))
    new_id = cursor.lastrowid

    # 2) Insert basic product meta (price, SKU, product type)
    meta_inserts = [
        (new_id, '_sku', sku),
        (new_id, '_regular_price', price),
        (new_id, '_price', price),
        (new_id, '_stock_status', 'instock'),
        (new_id, '_visibility', 'visible'),
        (new_id, '_virtual', 'no'),
        (new_id, '_downloadable', 'no'),
        (new_id, '_product_version', '5.0.0'),  # example version
        (new_id, '_wc_product_type', 'simple')  # simple product
    ]
    for post_id, meta_key, meta_value in meta_inserts:
        sql_meta = f"""
        INSERT INTO {TABLE_PREFIX}postmeta (post_id, meta_key, meta_value)
        VALUES (%s, %s, %s)
        """
        cursor.execute(sql_meta, (post_id, meta_key, meta_value))

    cnx.commit()
    print(f"[+] Created new product (ID: {new_id}, SKU: {sku}).")
    return new_id


def update_product(cursor, cnx, post_id, product_data):
    """
    Updates an existing product's title, price, description in wp_posts / wp_postmeta.
    """
    title = product_data["title"]
    price = product_data["price"]
    desc = product_data["description"]
    sku = product_data["sku"]

    # Update wp_posts (title, content)
    sql_update_posts = f"""
    UPDATE {TABLE_PREFIX}posts
    SET post_title = %s, post_content = %s, post_modified = NOW(), post_modified_gmt = NOW()
    WHERE ID = %s
    """
    cursor.execute(sql_update_posts, (title, desc, post_id))

    # Update price etc. in postmeta
    meta_updates = {
        '_regular_price': price,
        '_price': price
    }
    for meta_key, meta_value in meta_updates.items():
        sql_update_meta = f"""
        UPDATE {TABLE_PREFIX}postmeta
        SET meta_value = %s
        WHERE post_id = %s
          AND meta_key = %s
        """
        cursor.execute(sql_update_meta, (meta_value, post_id, meta_key))

    # If needed, update _sku if changed
    # (Usually SKU doesn't change, but let's allow it)
    sql_update_sku = f"""
    UPDATE {TABLE_PREFIX}postmeta
    SET meta_value = %s
    WHERE post_id = %s
      AND meta_key = '_sku'
    """
    cursor.execute(sql_update_sku, (sku, post_id))

    cnx.commit()
    print(f"[~] Updated existing product (ID: {post_id}, SKU: {sku}).")


def process_product(url, cursor, cnx):
    """
    Scrapes product data from the given Amazon link and inserts/updates
    the product in WooCommerce DB.
    """
    product_data = scrape_amazon_product(url)
    if not product_data:
        return

    sku = product_data["sku"]
    if sku == "N/A":
        # No ASIN or unique identifier found. Use fallback or skip.
        # You can decide how to handle no SKU scenario.
        print(f"[!] No valid SKU found for {url}. Skipping.")
        return

    # Check if product with the same SKU exists
    existing_id = find_existing_product(cursor, sku)
    if existing_id:
        # Update existing
        update_product(cursor, cnx, existing_id, product_data)
    else:
        # Create new
        create_new_product(cursor, cnx, product_data)


def main():
    # Connect to DB
    cnx = connect_db()
    cursor = cnx.cursor()

    # Read all product links from urls.txt
    try:
        with open("urls.txt", "r", encoding="utf-8") as f:
            links = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("[!] 'urls.txt' not found. Please create it with one Amazon link per line.")
        return

    for link in links:
        print(f"[*] Processing link: {link}")
        process_product(link, cursor, cnx)
        # Add a small delay to reduce chance of blocking
        time.sleep(random.uniform(1, 3))

    # Close DB
    cursor.close()
    cnx.close()
    print("[+] All done.")


if __name__ == "__main__":
    main()
