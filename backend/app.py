from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import re

app = Flask(__name__)
CORS(app)

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
    "Chaetomorpha linum (aerea) cladophora radiosa",
    "Chlamydomonas reinhardtii extract",
    "Chlorella",
    "Chlorophyceae",
    "Chondrus Crispus (aka Irish Moss or Carageenan Moss)",
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
    "Laminaria Saccharina Extract (Laminaria Saccharine)",
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

# MongoDB setup
client = MongoClient("")
db = client.skincare

# Home route
@app.route('/')
def home():
    return "Welcome to the Skincare Platform API!"

def normalize_ingredient(ingredient):
    """ Normalize ingredients by converting to lowercase and splitting into words. """
    return set(re.sub(r'\W+', ' ', ingredient.lower()).split())

# Assuming your pore_clogging_ingredients list is already normalized
normalized_pore_clogging = [normalize_ingredient(ing) for ing in pore_clogging_ingredients]

def ingredient_matches(product_ingredient, pore_clogging_list):
    """ Check if any normalized pore clogging ingredient matches words in the product ingredient. """
    normalized_product_ingredient = normalize_ingredient(product_ingredient)
    return any(normalized_clog <= normalized_product_ingredient for normalized_clog in pore_clogging_list)

# Example of using this in your Flask route
@app.route('/search-products', methods=['GET'])
def search_products():
    search_term = request.args.get('name')
    products = list(db.products.find({
        "$or": [
            {'name': {'$regex': search_term, '$options': 'i'}},
            {'brand': {'$regex': search_term, '$options': 'i'}}
        ]
    }))

    if products:
        product_results = []
        for product in products:
            flagged_ingredients = [
                ingredient for ingredient in product['ingredients']
                if ingredient_matches(ingredient, normalized_pore_clogging)
            ]

            product_results.append({
                'name': product['name'],
                'brand': product['brand'],
                'product_category': product.get('product_category', ''),
                'image_url': product.get('image_url', ''),
                'ingredients': product['ingredients'],
                'pore_clogging': flagged_ingredients
            })

        return jsonify({'products': product_results})
    else:
        return jsonify({'products': []})

# Recommended products route (if needed)
@app.route('/recommend-products', methods=['GET'])
def recommend_products():
    search_term = request.args.get('name')

    # Find products with similar names or brands
    recommended_products = db.products.find({
        "$or": [
            {'name': {'$regex': search_term, '$options': 'i'}},
            {'brand': {'$regex': search_term, '$options': 'i'}}
        ]
    }).limit(4)  # Limit to 4 recommended products

    # Format recommended products
    recommendations = [{
        'name': product['name'],
        'brand': product['brand']
    } for product in recommended_products]

    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)
