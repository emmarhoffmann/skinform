from pymongo import MongoClient
import html
import sys

# Connect to MongoDB
client = MongoClient('') # Paste in connection string
db = client['skinform'] 
collection = db['products'] 

# Function to decode HTML entities
def decode_html_entities(text):
    return html.unescape(text)

# Modify the query to only fetch documents where `name` or `brand` contains '&#'
regex_pattern = r"&#\d+;"
cursor = collection.find({
    "$or": [
        {"name": {"$regex": regex_pattern}},
        {"brand": {"$regex": regex_pattern}}
    ]
})

# Iterate through the filtered documents in the collection
for document in cursor:
    # Decode HTML entities
    new_name = decode_html_entities(document['name'])
    new_brand = decode_html_entities(document['brand'])
    
    # Show the current and new values
    print("Current Name: ", document['name'])
    print("New Name: ", new_name)
    print("Current Brand: ", document['brand'])
    print("New Brand: ", new_brand)
    
    # Ask for approval
    response = input("Approve update? (y/n): ")
    if response.lower() == 'y':
        # Update the document with the decoded values if approved
        collection.update_one(
            {'_id': document['_id']},
            {'$set': {'name': new_name, 'brand': new_brand}}
        )
        print("Document updated.")
    else:
        print("Update skipped.")