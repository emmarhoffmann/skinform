from pymongo import MongoClient, UpdateOne
import re

# Connect to MongoDB
client = MongoClient('mongodb+srv://erhoffmann128:Rushlake12!!@skinform.coz0o.mongodb.net/?retryWrites=true&w=majority&appName=skinform') # Paste in connection string
db = client['skinform'] 
collection = db['products']

def normalize_text(text):
    """Normalize text by removing special characters and converting to lowercase."""
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters
    return text.lower().strip()

def update_search_keywords():
    products = collection.find({})
    updates = []

    for product in products:
        normalized_brand = normalize_text(product.get('normalized_brand', ''))
        normalized_name = normalize_text(product.get('normalized_name', ''))
        product_category = normalize_text(product.get('product_category', ''))

        # Combine normalized fields into a single search_keywords field
        search_keywords = f"{normalized_brand} {normalized_name} {product_category}"

        updates.append(UpdateOne(
            {'_id': product['_id']},
            {'$set': {
                'search_keywords': search_keywords
            }}
        ))

    # Execute bulk updates
    if updates:
        result = collection.bulk_write(updates)
        print(f"Updated {result.modified_count} products with search_keywords field.")

if __name__ == "__main__":
    update_search_keywords()