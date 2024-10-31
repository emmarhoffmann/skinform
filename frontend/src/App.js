import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

function App() {
  // Search and Product States
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [recommendedProducts, setRecommendedProducts] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [loadingIngredients, setLoadingIngredients] = useState(false);

  // Ingredient Checker States
  const [pastedIngredients, setPastedIngredients] = useState('');
  const [poreCloggingResults, setPoreCloggingResults] = useState([]);
  const [poreCloggingIngredients, setPoreCloggingIngredients] = useState([]);

  // Category Navigation States
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [safeProducts, setSafeProducts] = useState([]);
  const [unsafeProducts, setUnsafeProducts] = useState([]);
  const [showCategoryPage, setShowCategoryPage] = useState(false);

  // Fetch pore-clogging ingredients on mount
  useEffect(() => {
    axios.get('https://skinform.onrender.com/pore-clogging-ingredients')
      .then(response => setPoreCloggingIngredients(response.data))
      .catch(error => console.error('Error fetching pore-clogging ingredients:', error));
  }, []);

  // Fetch product recommendations when search term changes
  useEffect(() => {
    if (searchTerm) {
      axios.get(`https://skinform.onrender.com/recommend-products?name=${searchTerm}`)
        .then(response => {
          const results = response.data.slice(0, 5);
          setRecommendedProducts(results);
          setShowDropdown(results.length > 0);
        })
        .catch(() => {
          setRecommendedProducts([]);
          setShowDropdown(false);
        });
    } else {
      setRecommendedProducts([]);
      setShowDropdown(false);
    }
  }, [searchTerm]);

  // Fetch categories on mount
  useEffect(() => {
    axios.get('https://skinform.onrender.com/categories')
      .then(response => setCategories(response.data))
      .catch(error => console.error("Error fetching categories:", error));
  }, []);

  // Product Selection Handler
  const handleProductSelect = (product) => {
    setSelectedProduct(product);
    setShowDropdown(false);
    fetchProductIngredients(product.name);
  };

  // Fetch Product Ingredients
  const fetchProductIngredients = (productName) => {
    setLoadingIngredients(true);
    axios.get(`https://skinform.onrender.com/product-ingredients/${encodeURIComponent(productName)}`)
      .then(response => {
        setSelectedProduct(prev => ({ ...prev, ...response.data }));
        setLoadingIngredients(false);
      })
      .catch(error => {
        console.error('Error fetching product ingredients:', error);
        setLoadingIngredients(false);
      });
  };

  // Ingredient Checker Handler
  const checkPoreCloggingIngredients = () => {
    if (!pastedIngredients.trim()) return;
    
    axios.post('https://skinform.onrender.com/check-ingredients', { ingredients: pastedIngredients })
      .then(response => setPoreCloggingResults(response.data))
      .catch(error => console.error('Error checking ingredients:', error));
  };

  // Category Selection Handler
  const handleCategoryClick = (category) => {
    setSelectedCategory(category);
    axios.get(`https://skinform.onrender.com/products-by-category`, {
      params: { category }
    })
      .then(response => {
        setSafeProducts(response.data.products_without_pore_clogging);
        setUnsafeProducts(response.data.products_with_pore_clogging);
      })
      .catch(error => console.error("Error fetching products by category:", error));
  };

  // Text Highlighting Functions
  const highlightText = (fullText, searchTerm) => {
    if (!fullText || !searchTerm) return fullText;

    const escapedSearchTerm = searchTerm.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regexPattern = escapedSearchTerm.split(/\s+/).map(word => `(${word})`).join("|");
    const regex = new RegExp(regexPattern, 'gi');
    const parts = fullText.split(regex);

    return parts.map((part, index) => regex.test(part) ? <strong key={index}>{part}</strong> : part);
  };

  const highlightPoreCloggingIngredients = (ingredientName, matchingPoreCloggingIngredients) => {
    if (!matchingPoreCloggingIngredients?.length) return ingredientName;

    const escapedIngredients = matchingPoreCloggingIngredients
      .map(ingredient => ingredient.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
      .sort((a, b) => b.length - a.length);
    
    const regex = new RegExp(`(${escapedIngredients.join('|')})`, 'gi');
    const parts = ingredientName.split(regex);

    return parts.map((part, index) => 
      regex.test(part) ? <span key={index} className="text-red-600">{part}</span> : part
    );
  };

  const handleImageError = (e) => {
    e.target.onerror = null;
    e.target.src = '/api/placeholder/200/200';
  };

  return (
    <div className="App">
      {/* Header */}
      <header className="App-header">
        <img src="/logo.png" alt="Logo" className="App-logo" />
      </header>

      {/* Main Title */}
      <h1 className="text-3xl font-bold mb-4">Pore-Clogging Product Search & Ingredient Checker</h1>
      <p className="mb-8">Search our database of products or paste any product's ingredients to check for pore-clogging ingredients.</p>

      {/* Browse Categories Section */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">Find Products by Category</h2>
        <div className="flex flex-col items-center">
          {!showCategoryPage ? (
            <button 
              onClick={() => setShowCategoryPage(true)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Browse Categories
            </button>
          ) : (
            <div className="w-full max-w-6xl">
              {!selectedCategory ? (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {categories.map((category, index) => (
                    <Card 
                      key={index}
                      className="hover:shadow-lg cursor-pointer transition-shadow"
                      onClick={() => handleCategoryClick(category)}
                    >
                      <CardHeader>
                        <CardTitle className="text-center">{category}</CardTitle>
                      </CardHeader>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="space-y-8">
                  <div className="flex justify-between items-center">
                    <h3 className="text-xl font-semibold">{selectedCategory}</h3>
                    <button 
                      onClick={() => setSelectedCategory(null)}
                      className="px-4 py-2 bg-gray-200 rounded-md hover:bg-gray-300"
                    >
                      Back to Categories
                    </button>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Safe Products */}
                    <div>
                      <h4 className="text-lg font-semibold text-green-600 mb-4">Pore-Safe Products</h4>
                      <div className="space-y-4">
                        {safeProducts.map((product, index) => (
                          <Card 
                            key={index}
                            className="hover:shadow-lg cursor-pointer transition-shadow"
                            onClick={() => handleProductSelect(product)}
                          >
                            <CardContent className="flex items-center gap-4 p-4">
                              <img 
                                src={product.image_url} 
                                alt={product.name}
                                className="w-20 h-20 object-cover"
                                onError={handleImageError}
                              />
                              <div>
                                <h3 className="font-semibold">{product.brand}</h3>
                                <p>{product.name}</p>
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                        {safeProducts.length === 0 && (
                          <p className="text-gray-500">No pore-safe products found in this category.</p>
                        )}
                      </div>
                    </div>

                    {/* Unsafe Products */}
                    <div>
                      <h4 className="text-lg font-semibold text-red-600 mb-4">Products with Pore-Clogging Ingredients</h4>
                      <div className="space-y-4">
                        {unsafeProducts.map((product, index) => (
                          <Card 
                            key={index}
                            className="hover:shadow-lg cursor-pointer transition-shadow"
                            onClick={() => handleProductSelect(product)}
                          >
                            <CardContent className="flex items-center gap-4 p-4">
                              <img 
                                src={product.image_url} 
                                alt={product.name}
                                className="w-20 h-20 object-cover"
                                onError={handleImageError}
                              />
                              <div>
                                <h3 className="font-semibold">{product.brand}</h3>
                                <p>{product.name}</p>
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                        {unsafeProducts.length === 0 && (
                          <p className="text-gray-500">No pore-clogging products found in this category.</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </section>

      {/* Product Search Section */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">Product Search</h2>
        <div className="relative max-w-xl mx-auto">
          <div className="flex items-center border rounded-lg overflow-hidden shadow-sm">
            <i className="fas fa-search text-gray-400 px-4"></i>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search Products..."
              className="w-full py-3 px-2 outline-none"
            />
          </div>
          {showDropdown && (
            <div className="absolute w-full mt-2 bg-white rounded-lg shadow-lg z-10">
              {recommendedProducts.map((product, index) => (
                <div
                  key={index}
                  className="flex items-center gap-4 p-4 hover:bg-gray-50 cursor-pointer"
                  onClick={() => handleProductSelect(product)}
                >
                  <img
                    src={product.image_url}
                    alt={product.name}
                    className="w-12 h-12 object-cover"
                    onError={handleImageError}
                  />
                  <span>
                    {highlightText(product.brand + ' - ' + (product.name || ''), searchTerm)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Selected Product Modal */}
      {selectedProduct && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <CardHeader className="flex flex-row justify-between items-start">
              <CardTitle>{selectedProduct.brand} - {selectedProduct.name}</CardTitle>
              <button 
                onClick={() => setSelectedProduct(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ×
              </button>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col md:flex-row gap-8">
                <img
                  src={selectedProduct.image_url}
                  alt={selectedProduct.name}
                  className="w-64 h-64 object-cover"
                  onError={handleImageError}
                />
                <div className="flex-1">
                  <h3 className="font-semibold mb-2">Ingredients:</h3>
                  {loadingIngredients ? (
                    <p>Loading ingredients...</p>
                  ) : selectedProduct.ingredients?.length > 0 ? (
                    <ul className="list-disc pl-5 space-y-1">
                      {selectedProduct.ingredients.map((ingredient, index) => (
                        <li key={index}>
                          {highlightPoreCloggingIngredients(
                            ingredient.name,
                            ingredient.matching_pore_clogging_ingredients
                          )}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p>No ingredients information available.</p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Ingredient Checker Section */}
      <section className="ingredient-checker-section">
        <h2>Ingredient Checker</h2>
        <p>Check Any Product’s Ingredient List</p>
        <div className="ingredient-checker">
          <div className="textarea-container">
            <i className={`fa-regular fa-paste paste-icon ${pastedIngredients ? 'hidden' : ''}`}></i>
            <textarea
              value={pastedIngredients}
              onChange={(e) => setPastedIngredients(e.target.value)}
              onFocus={(e) => {
                e.target.placeholder = ''; // Remove placeholder on focus
                document.querySelector('.paste-icon').classList.add('hidden'); // Hide icon
              }}
              onBlur={(e) => {
                if (!e.target.value) {
                  e.target.placeholder = '     Paste Ingredients'; // Restore placeholder if no content
                  document.querySelector('.paste-icon').classList.remove('hidden'); // Show icon
                }
              }}
              placeholder="     Paste Ingredients"
              className="pasted-ingredients"
            />
          </div>
          
          {/* Buttons section */}
          <div className="button-container">
            <button onClick={checkPoreCloggingIngredients}>Check</button>
            <button onClick={() => {
              setPastedIngredients(''); // Clear the textarea content
              document.querySelector('.pasted-ingredients').placeholder = '     Paste Ingredients'; // Restore placeholder
              document.querySelector('.paste-icon').classList.remove('hidden'); // Show the icon
            }}>
              Clear
            </button>
          </div>

          {poreCloggingResults.length > 0 && (
            <div className="pore-clogging-results">
              <button className="close-checker-button" onClick={() => setPoreCloggingResults([])}>&times;</button>
              <ul className="ingredients-list">
                {poreCloggingResults.map((ingredient, index) => (
                  <li key={index}>
                    {highlightPoreCloggingIngredients(ingredient.name, ingredient.matching_pore_clogging_ingredients)}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </section>

      {/* Informational Section */}
      <section className="info-section">
        <h2>Identify Pore-Clogging Ingredients in Everyday Products</h2>
        <p>Take control of your skincare with our tool, designed to identify pore-clogging ingredients in your favorite products. From skincare and makeup to haircare and body washes, our extensive database covers a wide variety of products, each carefully analyzed for potential breakout-causing ingredients. You can easily search for products or paste any ingredient list for instant analysis. Even products labeled as "non-comedogenic" or "oil-free" may contain problematic ingredients, as these claims aren't always regulated. With our tool, you can reduce irritants and refine your product selection for healthier results.</p>
        <p>Our database was last updated on 9/19/2024. Please note that product formulations may change over time, and it's always a good idea to verify the ingredient list directly from the product packaging to ensure it hasn't been reformulated since our last update.</p>
        <p>The impact of a pore-clogging ingredient on skin varies between individuals. Ingredients that cause issues for some may not affect others in the same way.</p>
      </section>

      {/* Pore-Clogging Ingredients List Section */}
      <section className="pore-clogging-list-section">
        <h2>Pore-Clogging Ingredients List</h2>
        <div className="pore-clogging-list">
          <ul className="ingredients-list">
            {poreCloggingIngredients.map((ingredient, index) => (
              <li key={index}>{ingredient}</li>  // Display each ingredient
            ))}
          </ul>
        </div>
        <p>Courtesy of acneclinicnyc.com</p>
      </section>
    </div>
  );
}

export default App;
