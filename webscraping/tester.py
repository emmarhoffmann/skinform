import re
import openai
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from openaikey.env file
load_dotenv('openaikey.env')

# Get the OpenAI API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

# Since the file is in the same folder, just refer to it by name
file_name = "product_page_scripts.txt"

# Function to interact with OpenAI API and clean the ingredients
def get_cleaned_ingredients(ingredient_desc):
    prompt = f"""
    Extract only the ingredients from the actual list, which is typically comma-separated. Ignore any text, symbols, or descriptions before or after the comma-separated ingredients. The list should consist of individual ingredients, each placed between single quotes, separated by commas, and all ingredients enclosed in brackets. Do not include any text, sentences, or irrelevant information that is not part of the comma-separated list of ingredients. 

    ingredientDesc: {ingredient_desc}
    """
    client = OpenAI()
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Updated to use a supported model
            messages=[
                {"role": "system", "content": "You are an assistant that cleans ingredient lists."},
                {"role": "user", "content": prompt},
            ],
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return None

# Function to extract ingredientDesc from the file content
def extract_ingredient_desc_from_file(file_content):
    try:
        # Use regex to find the ingredientDesc field
        match = re.search(r'"ingredientDesc":"([^"]+)"', file_content)
        if match:
            # Decode any HTML escape characters (if necessary)
            ingredient_desc = match.group(1).replace('<br>', ', ').replace('&nbsp;', ' ')
            return ingredient_desc
        else:
            print("No ingredient description found in file.")
            return None
    except Exception as e:
        print(f"Error extracting ingredients from file: {e}")
        return None

def main():
    # Read the file content
    with open(file_name, 'r', encoding='utf-8') as f:
        file_content = f.read()

    # Extract the ingredient description
    ingredient_desc = extract_ingredient_desc_from_file(file_content)

    if ingredient_desc:
        print(f"Original Ingredient Description: {ingredient_desc}")
        
        # Clean the ingredients using OpenAI
        cleaned_ingredients = get_cleaned_ingredients(ingredient_desc)
        
        if cleaned_ingredients:
            print(f"Cleaned Ingredients: {cleaned_ingredients}")
        else:
            print("Failed to clean the ingredients.")
    else:
        print("No ingredient description found.")

if __name__ == "__main__":
    main()