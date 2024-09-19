import requests
from bs4 import BeautifulSoup
import re
import csv
import time
import uuid
import os
import xml.etree.ElementTree as ET

# User-Agent to mimic browser behavior and avoid blocking
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Save progress to a file (using the last processed product URL)
def save_progress(product_url):
    with open("progress.txt", "w") as f:
        f.write(product_url)

# Read the last processed product URL
def get_last_processed_url():
    try:
        with open("progress.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None  # If no progress file exists, start from the beginning


def get_all_products():
    all_product_links = []
    sitemap_url = "https://www.sephora.com/sitemaps/products-sitemap.xml"
    
    response = requests.get(sitemap_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to access sitemap. Status code: {response.status_code}")
        return all_product_links
    
    root = ET.fromstring(response.content)
    
    for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
        if '/product/' in url.text:
            all_product_links.append(url.text)
    
    print(f"Collected {len(all_product_links)} product links.")
    return all_product_links

def filter_products(product_data):
    relevant_categories = [
        'skincare', 'makeup', 'face', 'body', 'hair', 'bath', 'fragrance',
        'sun', 'self tanner', 'moisturizer', 'cleanser', 'treatment',
        'mask', 'eye cream', 'lip balm', 'serum', 'toner', 'exfoliator',
        'foundation', 'concealer', 'powder', 'blush', 'bronzer', 'highlighter',
        'eyeshadow', 'eyeliner', 'mascara', 'lipstick', 'lip gloss',
        'shampoo', 'conditioner', 'hair treatment', 'styling product',
        'body wash', 'soap', 'lotion', 'cream', 'oil', 'scrub', 'deodorant',
        'sunscreen', 'after-sun', 'facial-toner-skin-toner', 'body-wash-shower-gel', 'vegan-makeup',
        'setting-powder-face-powder', 'tinted-moisturizer', 'dry-skin-treatment',
        'mens-personal-care', 'eye-treatment-dark-circle-treatment', 'skin-care-sets-travel-value',
        'concealer', 'clean-skin-care', 'skin-care-solutions', 'mens-hair-care', 'complexion-sets',
        'travel-size-toiletries', 'mens-body-wash', 'body-dry-skin-products', 'face-wipes',
        'foundation-makeup', 'blush', 'bb-cream-cc-cream', 'cleansing-oil-face-oil', 'lip-gloss',
        'acne-treatment-blemish-remover', 'mini-makeup', 'self-tanning-products',
        'facial-treatments', 'dark-spot-remover', 'body-texture-kp-products',
        'damaged-hair-treatment', 'sheet-masks', 'cheek-palettes', 'sunscreen',
        'under-eye-concealer', 'lip-oil', 'makeup-removers',
        'hair-treatment-dry-scalp-treatment', 'body-lotion-body-oil', 'luminizer-luminous-makeup',
        'face-makeup', 'makeup-primer-face-primer', 'bronzer-makeup',
        'skin-care-sets-for-men', 'eye-mask', 'night-cream', 'makeup-kits-makeup-sets', 'mens-hair-products',
        'skincare', 'eyeshadow-palettes', 'cleanser', 
        'wrinkle-cream-wrinkle-remover', 'face-tanner-self-tanner-face', 'neck-cream-decollete', 
        'makeup-palettes', 'moisturizing-cream-oils-mists', 'vegan-skin-care', 'exfoliating-scrub-exfoliator',
        'eyeliner', 'face-wash-for-men', 'color-correcting', 'body-hyperpigmentation-products',
        'sunscreen-men', 'facial-peels', 'skin-brighteners-dull-skin-treatments', 'lipstick',
        'moisturizer-skincare', 'makeup-accessories', 'body-care', 'body-stretch-mark-firming-cream', 'eyebrow-makeup-pencils',
        'makeup-cosmetics', 'body-moisturizers', 'lip-palettes-gloss-sets', 'hand-sanitizer-soap', 'sunscreen-sun-protection',
        'body-mist-hair-mist', 'makeup-bags-cosmetic-bags', 'face-serum', 'body-scrub-exfoliant',
        'pore-minimizing-products', 'hand-lotion-foot-cream', 'eye-makeup',
        'eyeshadow', 'face-mask', 'lip-plumper', 'skin-care-gift-sets', 'face-sunscreen', 'lips-makeup',
        'clean-makeup', 'lip-balm-lip-care', 'mens-shampoo-conditioner',
        'face-mist-face-spray', 'cheek-makeup', 'wellness-skincare',
        'mens-facial-products', 'anti-aging-skin-care', 'eye-sets',
        'eye-cream-dark-circles', 'liquid-lipstick', 'lip-liner-lip-pencils', 'acne-products-acne-cream',
        'moisturizer-men', 'face-wash-facial-cleanser', 
        'lip-stain', 'eye-cream-men', 'aftershave',
        'hair-masks', 'conditioner-hair', 'mini-bath-products', 'shampoo-sulfate-free-shampoo', 
        'bubble-bath-oil', 'hair-products-treatments', 'kiss-holiday-lipstick-collection', 
        'deodorant-antiperspirant', 'hair-products', 'shampoo-conditioner', 'mini-skincare', 
        'leave-in-conditioner', 'bath-and-body-soap'
    ]
    
    if product_data:
        category = product_data.get('product_category', '').lower()
        for relevant_cat in relevant_categories:
            if relevant_cat in category:
                return True
    return False

# The rest of the functions remain the same
def read_existing_products(csv_filename):
    existing_products = set()
    if os.path.exists(csv_filename):
        with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                existing_products.add(row['product_url'])
    return existing_products

def clean_ingredient(ingredient):
    ingredient = re.sub(r'<[^>]+>', '', ingredient)
    ingredient = ingredient.strip()
    ingredient = re.sub(r'\s*\(\d+\)$', '', ingredient)
    return ingredient

def extract_product_data(product_url):
    response_product = requests.get(product_url, headers=headers, timeout=10)
    soup_product = BeautifulSoup(response_product.content, 'html.parser')

    try:
        script_content = " ".join(script.string for script in soup_product.find_all('script') if script.string)

        image_url = re.search(r'Sephora\.Util\.Perf\.markPageRender\("([^"]+)"\)', script_content).group(1)
        product_name = re.search(r'"@type":"Product".*?"name":"([^"]+)"', script_content, re.DOTALL).group(1)
        product_brand = re.search(r'"brand":"([^"]+)"', script_content).group(1)
        product_category = re.search(r'"productCategories".*?"displayName":"([^"]+)"', script_content).group(1)

        ingredients_match = re.search(r'"ingredientDesc":\s*"([^"]+)"', script_content)
        if ingredients_match:
            ingredients_text = ingredients_match.group(1)
            ingredients_text = bytes(ingredients_text, "utf-8").decode("unicode_escape")
            ingredients_text = ingredients_text.replace('\\"', '"')
            
            sections = ingredients_text.split('.')
            
            ingredients = []
            for section in sections:
                if section.count(',') > 5:
                    ingredients = [clean_ingredient(ingredient) for ingredient in section.split(',') if clean_ingredient(ingredient)]
                    break
            
            if not ingredients and sections:
                ingredients = [clean_ingredient(ingredient) for ingredient in sections[-1].split(',') if clean_ingredient(ingredient)]

        else:
            ingredients = []

        cleaned_data = {
            "_id": str(uuid.uuid4()),
            "name": product_name,
            "brand": product_brand,
            "product_category": product_category,
            "image_url": image_url,
            "product_url": product_url,
            "ingredients": ingredients
        }

        return cleaned_data

    except Exception as e:
        print(f"Error extracting product data from {product_url}: {e}")
        return None

def main():
    csv_filename = 'products.csv'
    existing_products = read_existing_products(csv_filename)
    product_links = get_all_products()
    
    new_products_count = 0
    total_products = len(product_links)

    # Get the last processed product URL
    last_processed_url = get_last_processed_url()
    
    # Flag to skip products until we reach the last processed one
    resume_scraping = False if last_processed_url else True
    
    for index, product_url in enumerate(product_links, 1):
        # Skip URLs until we reach the last processed URL
        if not resume_scraping:
            if product_url == last_processed_url:
                resume_scraping = True
            continue

        if product_url in existing_products:
            print(f"Product already exists in CSV: {product_url}")
            continue
        
        product_data = extract_product_data(product_url)
        if product_data and filter_products(product_data):
            fieldnames = product_data.keys()
            file_exists = os.path.isfile(csv_filename)
            
            with open(csv_filename, 'a', newline='', encoding='utf-8') as output_file:
                dict_writer = csv.DictWriter(output_file, fieldnames)
                if not file_exists:
                    dict_writer.writeheader()
                dict_writer.writerow(product_data)
            
            new_products_count += 1
            print(f"Added product: {product_data['name']} (Category: {product_data['product_category']})")
        else:
            print(f"Skipped product: {product_url} (Not in relevant categories)")
        
        # Save progress after processing each product
        save_progress(product_url)
        
        print(f"Progress: {index}/{total_products} products processed. New products added: {new_products_count}")
        time.sleep(1)  # Be polite to the server

    print(f"Scraping completed. Total new products added: {new_products_count}")



if __name__ == "__main__":
    main()