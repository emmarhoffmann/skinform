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
        'sunscreen', 'after-sun', 'perfume', 'cologne', 'facial-toner-skin-toner', 'mens-grooming', 'body-wash-shower-gel', 'vegan-makeup',
        'setting-powder-face-powder', 'tinted-moisturizer', 'dry-skin-treatment',
        'mens-personal-care', 'eye-treatment-dark-circle-treatment', 'skin-care-sets-travel-value',
        'concealer', 'clean-skin-care', 'fake-eyelashes-false-eyelashes', 'skin-care-solutions',
        'mens-hair-care', 'complexion-sets', 'travel-size-toiletries', 'mens-body-wash',
        'anti-aging-tools', 'blotting-paper-oil-control', 'body-dry-skin-products', 'face-wipes',
        'foundation-makeup', 'blush', 'bb-cream-cc-cream', 'cleansing-oil-face-oil', 'lip-gloss',
        'acne-treatment-blemish-remover', 'mini-makeup', 'self-tanning-products', 'makeup-brush-sets',
        'facial-treatments', 'fragrance', 'dark-spot-remover', 'body-texture-kp-products',
        'damaged-hair-treatment', 'sheet-masks', 'cheek-palettes', 'sunscreen', 'skin-care-tools',
        'under-eye-concealer', 'lip-oil', 'facial-cleansing-brushes', 'makeup-removers',
        'hair-treatment-dry-scalp-treatment', 'body-lotion-body-oil', 'luminizer-luminous-makeup',
        'face-makeup', 'foundation-brushes-face-brushes', 'makeup-primer-face-primer', 'bronzer-makeup',
        'skin-care-sets-for-men', 'eye-mask', 'night-cream', 'makeup-kits-makeup-sets', 'mens-hair-products',
        'skincare', 'pedicure-tools-manicure-tools', 'eyeshadow-palettes', 'cleanser', 
        'wrinkle-cream-wrinkle-remover', 'face-tanner-self-tanner-face', 'neck-cream-decollete', 
        'makeup-palettes', 'moisturizing-cream-oils-mists', 'vegan-skin-care', 'exfoliating-scrub-exfoliator',
        'eyeliner', 'face-wash-for-men', 'color-correcting', 'body-hyperpigmentation-products',
        'sunscreen-men', 'facial-peels', 'skin-brighteners-dull-skin-treatments', 'lipstick',
        'moisturizer-skincare', 'makeup-accessories', 'body-care', 'body-stretch-mark-firming-cream',
        'eyeliner-brushes-eyeshadow-brushes', 'eyebrow-makeup-pencils', 'makeup-cosmetics',
        'body-moisturizers', 'lip-palettes-gloss-sets', 'hand-sanitizer-soap', 'sunscreen-sun-protection',
        'body-mist-hair-mist', 'makeup-bags-cosmetic-bags', 'face-serum', 'body-scrub-exfoliant',
        'makeup-brush-cleaner', 'pore-minimizing-products', 'hand-lotion-foot-cream', 'eye-makeup',
        'eyeshadow', 'face-mask', 'lip-plumper', 'skin-care-gift-sets', 'face-sunscreen', 'lips-makeup',
        'clean-makeup', 'exclusive-products', 'lip-balm-lip-care', 'mens-shampoo-conditioner',
        'face-mist-face-spray', 'cheek-makeup', 'lip-brushes-lipstick-brushes', 'wellness-skincare',
        'mens-facial-products', 'anti-aging-skin-care', 'eye-sets', 'makeup-tools', 'mascara',
        'eye-cream-dark-circles', 'liquid-lipstick', 'lip-liner-lip-pencils', 'acne-products-acne-cream',
        'moisturizer-men', 'contour-palette-brush', 'makeup-sponges', 'face-wash-facial-cleanser', 
        'lip-stain', 'makeup-brushes', 'eye-cream-men', 'eyeshadow-primer-eye-primer', 'aftershave',
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
    
    for index, product_url in enumerate(product_links, 1):
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
        
        print(f"Progress: {index}/{total_products} products processed. New products added: {new_products_count}")
        time.sleep(1)  # Be polite to the server

    print(f"Scraping completed. Total new products added: {new_products_count}")

if __name__ == "__main__":
    main()