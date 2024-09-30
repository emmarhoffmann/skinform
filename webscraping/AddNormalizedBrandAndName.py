from pymongo import MongoClient
from pymongo import UpdateOne
from unidecode import unidecode
import re

# Connect to MongoDB
client = MongoClient('') # Paste in connection string
db = client['skinform'] 
collection = db['products'] 

def normalize_text(text):
    """Normalize text by removing special characters and keeping spaces."""
    text = unidecode(text.lower())  # Normalize accents and case
    text = re.sub(r"[^a-z0-9\s]", '', text)  # Remove special characters except spaces
    text = re.sub(r"\s+", ' ', text)  # Ensure only single spaces between words
    return text.strip()  # Remove leading and trailing spaces

def update_products():
    products = db.products.find({})
    updates = []
    for product in products:
        # Apply the new normalization function
        normalized_name = normalize_text(product['name'])
        normalized_brand = normalize_text(product.get('brand', ''))

        updates.append(UpdateOne(
            {'_id': product['_id']},
            {'$set': {
                'normalized_name': normalized_name,
                'normalized_brand': normalized_brand
            }},
            upsert=False
        ))

        # Execute the update in batches
        if len(updates) >= 1000:
            db.products.bulk_write(updates)
            updates = []
    
    if updates:
        db.products.bulk_write(updates)

    print("Database normalization update completed.")

if __name__ == "__main__":
    update_products()