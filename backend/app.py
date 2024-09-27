from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()  # Ensure this is before accessing any environment variables

app = Flask(__name__)
CORS(app)

# MongoDB setup
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client.skinform

# Pore clogging ingredients, courtesy of Acne Clinc NYC: https://acneclinicnyc.com/pore-clogging-ingredients/
pore_clogging_ingredients = [
    "1-acetoxyhexadecane",
    "1-hexadecanol acetate",
    "1-hexadecanol",
    "Acetic acid hexadecyl ester",
    "Acetylated Lanolin",
    "Acetylated Lanolin Alcohol",
    "Acetylated wool fat",
    "Acetylated wool wax",
    "Adansonia digitata l.",
    "Agar",
    "Ahnfeltiopsis concinna extract",
    "Alaria esculenta extract",
    "Alga bladderwrack",
    "Algae",
    "Algae Extract",
    "Algin",
    "Alginate",
    "Alginic acid",
    "Algea",
    "Aphanothece sacrum polysaccharide",
    "Arthrospira plantensis",
    "Ascophyllum nodosum extract",
    "Asparagopsis armata extract",
    "Baobab",
    "Beeswax",
    "Bismuth",
    "Bryopsis africana",
    "Butyl Octadecanoate",
    "Butyl Stearate",
    "Butyl Stearic acid",
    "Butyrospermum",
    "Cacao seed butter",
    "Capea biruncinata var. denuda sonder",
    "Capea biruncinata var. elongata sonder",
    "Carageenan gum",
    "Carastay c",
    "Caulerpa lentillifera extract",
    "Caulerpa filiformis",
    "Carrageenan",
    "Carrageenan Moss",
    "Cera alba",
    "Cera bianca",
    "Cera flava",
    "Cera olea",
    "Cetearyl Alcohol + Ceteareth 20",
    "Cetyl Acetate",
    "Cetyl Alcohol",
    "Chaetomorpha linum aerea cladophora radiosa",
    "Chlamydomonas reinhardtii extract",
    "Chlorella",
    "Chlorophyceae",
    "Chondrus Crispus",
    "Cladophora cf. subsimplex",
    "Cladosiphon okamuranus extract",
    "Coal Tar",
    "Coco-caprate",
    "Coco-caprylate",
    "Cocoa Butter",
    "Coconut Alkanes",
    "Coconut Butter",
    "Coconut Extract",
    "Coconut Nucifera extract",
    "Coconut Oil",
    "Cocos nucifera oil",
    "cocos nucifera seed butter",
    "Coenochloris signiensis extract",
    "Colloidal Sulfur",
    "Cotton Awws Oil",
    "Cotton Seed Oil",
    "Corallina officinalis extract",
    "Corn",
    "Corn oil",
    "Creosote",
    "Cystoseira tamariscifolia extract",
    "D & C Red # 17",
    "D & C Red # 21",
    "D & C Red # 3",
    "D & C Red # 30",
    "D & C Red # 36",
    "Decyl Oleate",
    "Decyloleate",
    "Dicotyledons succinate",
    "Dictyopteris membranacea",
    "Dictyopteris polypodioides",
    "Diethylhexyl sodium sulfosuccinate",
    "Diisooctyl succinate",
    "Dilsea carnosa extract",
    "Dioctyl sodium sulfosuccinate",
    "Dioctyl Succinate",
    "Disodium laureth sulfosuccinate",
    "Disodium Monooleamido",
    "Disodium Monooleamido peg 2 sulfosuccinate",
    "Disodium oleamido peg-2 sulfosuccinate",
    "Dodecanoic acid",
    "Dodecoic acid",
    "Dodecylic acid",
    "Dunaliella salina extract",
    "Duodecylic acid",
    "Durvillaea antarctica extract",
    "Ecklonia cava",
    "Ecklonia cava extract",
    "Ecklonia radiata",
    "Enteromorpha compressa extract",
    "Ethoxylated Lanolin",
    "Ethylhexyl Palmitate",
    "Ethylhexyl Stearate",
    "Eucheuma spinosum extract",
    "Fucoxanthin",
    "Fucus serratus",
    "Fucus vesiculosus",
    "Gamtae extract",
    "Gelidiella acerosa extract",
    "Gelidium amansii extract",
    "Gigartina stellata extract",
    "Glyceryl monostearate",
    "Glyceryl Stearate SE",
    "Glyceryl-3 Diisostearate",
    "Glycine soja oil",
    "Glycine max",
    "Gracilariopsis chorda extract",
    "Haematococcus pluvialis extract",
    "Haematococcus pluvialis",
    "Haslea ostrearia extract",
    "Hexadecanol acetate",
    "Hexadecyl Acetate",
    "Hexadecyl Alcohol",
    "Himanthalia elongata extract",
    "Hizikia fusiforme extract",
    "Hydrogenated Vegetable Oil",
    "Hydrolyzed rhodophycea extract",
    "Hydrous magnesium silicate",
    "Hypnea musciformis extract",
    "Hypneaceae extract",
    "Irish Moss",
    "Isocetyl Alcohol",
    "Isocetyl Stearate",
    "Isodecyl Oleate",
    "Isohexadecanol",
    "Isohexadecyl alcohol",
    "Isohexadecyl stearate",
    "Isooctadecyl isooctadecanoate",
    "Isopalmitic alcohol",
    "Isopalmityl alcohol",
    "Isopropyl isodecanoate",
    "Isopropyl Isostearate",
    "Isopropyl Linolate",
    "Isopropyl Myristate",
    "Isopropyl Palmitate",
    "Isostearyl Isostearate",
    "Isostearyl Neopentanoate",
    "Jania rubens extract",
    "Jojoba wax",
    "Kappaphycus alvarezii extract",
    "Karite",
    "Kelp",
    "Kousou ekisu",
    "Laminaria",
    "Laminaria Digitata Extract",
    "Laminaria Saccharine",
    "Laminaria Saccharina Extract",
    "Lanolin acetate",
    "Lanolin alcohol acetate",
    "Lanolin polyoxyethylene ether",
    "Laureth-23",
    "Laureth-4",
    "Lauric Acid",
    "Laurostearic acid",
    "Lcd",
    "Linolate",
    "Liquor carbonis detergens",
    "Liquor picis carbonis",
    "Lithothamnium calcareum powder",
    "Lpc",
    "Macroalgae",
    "Macrocystis pyrifera extract",
    "Mangifera indica seed butter",
    "Mango Butter",
    "Marula",
    "Marula oil",
    "Methylsilanol mannuronate",
    "Mink Oil",
    "Moss",
    "Myristate",
    "Myristic Acid",
    "Myristyl",
    "Myristyl Lactate",
    "Myristyl Myristate",
    "Myristyl Propionate",
    "N-hexadecyl alcohol",
    "N-hexadecyl ethanoate",
    "Octadecanoic acid",
    "Octadecyl heptanoate",
    "Octyl Palmitate",
    "Octyl Stearate",
    "Oleth-3",
    "Oleth-3 phosphate",
    "Oleyl Alcohol",
    "Palmaria palmata extract",
    "Palmityl Acetate",
    "Palmityl Alcohol",
    "Parkii",
    "PEG 2 Sulfosuccinate",
    "PEG 2- Sulfosuccinate",
    "PEG 16 Lanolin",
    "PEG 200 Dilaurate",
    "PEG-75",
    "PEG 8 Stearate",
    "Pelvetia canaliculata extract",
    "PES",
    "Phaeodactylum tricornutum extract",
    "Phaeophyceae",
    "Pix carbonis",
    "PG Monostearate",
    "PGMS",
    "PPG-2 Myristyl",
    "PPG 2 Myristyl Propionate",
    "PPG 2 Myristyl Ether Propionate",
    "Plankton",
    "Polyethylene glycol 200",
    "Polyethylene glycol dodecyl ether",
    "Polyethylene glycol jojoba acid",
    "Polyethylene glycol lauryl ether",
    "Polyethylene glycol monododecyl ether",
    "Polyethylene glycol stearate",
    "Polyoxyethylene lauryl ether",
    "Polysiphonia elongata extract",
    "Polyglyceryl-3 Diisostearate",
    "Polyglyceryl-3-Disostearate",
    "Porphyra umbilicalis",
    "Porphyridium",
    "Porphyridium cruentum extract",
    "Porphyridium polysaccharide",
    "Potassium Chloride",
    "Potassium Salt",
    "Propanoic Acid",
    "Propylene Glycol Monostearate",
    "Pyrene coal tar pitch",
    "Red Algae",
    "Rhodophyta",
    "Rhodophyceae extract",
    "Sargassum filipendula extract",
    "Sargassum fusiforme extract",
    "Sclerocarya birrea",
    "Sclerocarya birrea seed oil",
    "Seaweed",
    "Sea fern",
    "Sesame",
    "Sesamum indicum",
    "Shark Liver Oil",
    "Shark Squalene",
    "Shea",
    "Shea Butter",
    "Sheep alcohol",
    "Simmondsia chinensis seed wax",
    "Sles",
    "Slo",
    "Sls",
    "Sodium Alginate",
    "Sodium Alkylethersulfate",
    "Sodium Docusate",
    "Sodium Dodecyl sulphate",
    "Sodium Laureth Sulfate",
    "Sodium Lauryl Ether sulfate",
    "Sodium Lauryl Sulfate",
    "Soja",
    "Solulan 16",
    "Sorbitan Monooleate",
    "Sorbitan Oleate",
    "Soy",
    "Soybean",
    "Soybean Oil",
    "Sphacelaria",
    "Spirulina",
    "Squalene",
    "Steareth 10",
    "Stearic Acid Tea",
    "Stearyl Heptanoate",
    "Starch",
    "Sulfated Castor Oil",
    "Sulfated Jojoba Oil",
    "Sulfosuccinate",
    "Sulphated castor oil",
    "Talc",
    "Talcum",
    "Tea stearate",
    "Tetradecanoic acid",
    "Tetradecyl lactate",
    "Tetradecyl myristate",
    "Tetradecyl propionate",
    "Theobroma butter",
    "Theobroma cocoa seed butter",
    "Theobroma oil",
    "Triticum aestivum",
    "Triticum vulgare",
    "Turkey red oil",
    "Undaria Pinnatifida",
    "Ulva lactuca",
    "Ulva fasciata",
    "Ulva rhacodes",
    "Vegetable gelatin",
    "Vitellaria paradoxa",
    "Vulvic acid",
    "Wakame",
    "Wheat",
    "Wheat Germ Glyceride",
    "Wheat Germ Oil",
    "Wool alcohol",
    "Wool fat",
    "Xanthophyta",
    "Xylene",
    "Xylitol",
    "Zea mays"
]

# Home route
@app.route('/')
def home():
    return "Welcome to the Skincare Platform API!"

def normalize_ingredient(ingredient):
    """ Normalize ingredients by converting to lowercase and splitting into words. """
    return set(re.sub(r'\W+', ' ', ingredient.lower()).split())

# Assuming your pore_clogging_ingredients list is already normalized
normalized_pore_clogging = [normalize_ingredient(ing) for ing in pore_clogging_ingredients]

def find_matching_pore_clogging_ingredients(product_ingredient, pore_clogging_list):
    """Return a list of pore-clogging ingredients found in the product ingredient, prioritizing longest match."""
    matches = []
    product_ingredient_lower = product_ingredient.lower()
    
    # Sort the pore-clogging list by length (longest first) to ensure specific matches first
    sorted_pore_clogging_list = sorted(pore_clogging_list, key=lambda x: len(x), reverse=True)
    
    for clogging_ingredient in sorted_pore_clogging_list:
        # Create a regex pattern to match the exact word boundaries for each ingredient
        pattern = r'\b' + re.escape(clogging_ingredient.lower()) + r'\b'
        if re.search(pattern, product_ingredient_lower):
            matches.append(clogging_ingredient)
    
    return matches

@app.route('/search-products', methods=['GET'])
def search_products():
    search_term = request.args.get('name')
    products = list(db.products.find({"name": {"$regex": search_term, "$options": 'i'}}))
    return jsonify([{
        "name": product["name"],
        "brand": product.get("brand", "Unknown brand"),
        "image_url": product.get("image_url", "default_image.jpg"),
        "ingredients": product.get("ingredients", [])
    } for product in products])

# Recommended products route
@app.route('/recommend-products', methods=['GET'])
def recommend_products():
    search_term = request.args.get('name', '')

    # Search both 'name' and 'brand' fields for the search term
    recommended_products = list(db.products.find(
        {'$or': [
            {'name': {'$regex': f'^{re.escape(search_term)}', '$options': 'i'}},  # Exact match at the start in name
            {'name': {'$regex': f'{re.escape(search_term)}', '$options': 'i'}},   # Containing the term anywhere in name
            {'brand': {'$regex': f'^{re.escape(search_term)}', '$options': 'i'}},  # Exact match at the start in brand
            {'brand': {'$regex': f'{re.escape(search_term)}', '$options': 'i'}}    # Containing the term anywhere in brand
        ]},
        {'name': 1, 'brand': 1, 'image_url': 1, 'ingredients': 1}  # Only fetch necessary fields
    ).limit(5))  # Limit to 5 products only

    # Format the response
    recommendations = [{
        'name': product['name'],
        'brand': product.get('brand', 'Unknown brand'),
        'image_url': product.get('image_url', 'default_image.jpg'),  # Fallback if no image URL
        'ingredients': product.get('ingredients', [])  # Ensure ingredients are included
    } for product in recommended_products]

    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)