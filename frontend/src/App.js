import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import '@fortawesome/fontawesome-free/css/all.min.css';


function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [recommendedProducts, setRecommendedProducts] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [loadingIngredients, setLoadingIngredients] = useState(false);

  const [pastedIngredients, setPastedIngredients] = useState('');
  const [poreCloggingResults, setPoreCloggingResults] = useState([]);
  const [poreCloggingIngredients, setPoreCloggingIngredients] = useState([]);

  // Fetch the pore-clogging ingredients when the component mounts
  useEffect(() => {
    axios.get('http://skinform.vercel.app/pore-clogging-ingredients')
      .then(response => {
        setPoreCloggingIngredients(response.data); // Set the ingredients in state
      })
      .catch(error => {
        console.error('Error fetching pore-clogging ingredients:', error);
      });
  }, []);

  useEffect(() => {
    if (searchTerm) {
      axios.get(`http://skinform.vercel.app/recommend-products?name=${searchTerm}`)
        .then(response => {
          const results = response.data.slice(0, 5); // Limit to 5 products
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

  const handleProductSelect = (product) => {
    setSelectedProduct(product);
    setShowDropdown(false);
    fetchProductIngredients(product.name); // Fetch ingredients by product name
  };

  const fetchProductIngredients = (productName) => {
    setLoadingIngredients(true);
    axios.get(`http://skinform.vercel.app/product-ingredients/${encodeURIComponent(productName)}`)
      .then(response => {
        const updatedProduct = { ...selectedProduct, ...response.data };
        setSelectedProduct(updatedProduct);
        setLoadingIngredients(false);
      })
      .catch(error => {
        console.error('Error fetching product ingredients:', error);
        setLoadingIngredients(false);
      });
  };

  const checkPoreCloggingIngredients = () => {
    if (!pastedIngredients.trim()) return;

    axios.post('http://skinform.vercel.app/check-ingredients', { ingredients: pastedIngredients })
      .then(response => {
        setPoreCloggingResults(response.data);
      })
      .catch(error => {
        console.error('Error checking ingredients:', error);
      });
  };

  // Highlighting search term in product
  function highlightText(fullText, searchTerm) {
    if (!fullText || !searchTerm) return fullText;

    const escapedSearchTerm = searchTerm.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regexPattern = escapedSearchTerm.split(/\s+/).map(word => {
      return `(${word})`;
    }).join("|");

    const regex = new RegExp(regexPattern, 'gi');
    const parts = fullText.split(regex);

    return parts.map((part, index) => regex.test(part) ? <strong key={index}>{part}</strong> : part);
  }

  function highlightPoreCloggingIngredients(ingredientName, matchingPoreCloggingIngredients) {
    if (!matchingPoreCloggingIngredients || matchingPoreCloggingIngredients.length === 0) {
      return ingredientName;
    }

    const escapedIngredients = matchingPoreCloggingIngredients
      .map(ingredient => ingredient.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
      .sort((a, b) => b.length - a.length);

    const regexPattern = escapedIngredients.join('|');
    const regex = new RegExp(`(${regexPattern})`, 'gi');

    const parts = ingredientName.split(regex);

    return parts.map((part, index) => regex.test(part)
      ? <span key={index} style={{ color: 'red' }}>{part}</span>
      : part
    );
  }

  const handleImageError = (e) => {
    e.target.onerror = null;
    e.target.src = '/path_to_default_image.jpg'; // Default image path
  };

  return (
    <div className="App">
      {/* Add a header with a logo */}
      <header className="App-header">
        <img src="/logo.png" alt="Logo" className="App-logo" />
      </header>
      {/* Main Title and Description */}
      <h1>Pore-Clogging Product Search & Ingredient Checker</h1>
      <p>Search our database of products or paste any product’s ingredients to check for pore-clogging ingredients.</p>

      {/* Product Search Section */}
      <section className="product-search-section">
        <h2>Product Search</h2>
        <p>Search our Database of Products</p>
        <div className="search-container">
          <i className="fas fa-search search-icon"></i> 
          <input
            className="search-input"
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search Products..."
          />
          {showDropdown && (
            <div className="dropdown">
              {recommendedProducts.map((product, index) => (
                <div
                  key={index}
                  className="suggestion-item"
                  onClick={() => handleProductSelect(product)}
                >
                  <img
                    className="suggestion-image"
                    src={product.image_url}
                    alt={product.name}
                    onError={handleImageError}
                  />
                  <span>{highlightText(product.brand + ' - ' + (product.name || ''), searchTerm)}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {selectedProduct && (
        <div className="product-detail">
          <button className="close-button" onClick={() => setSelectedProduct(null)}>&times;</button>
          <img
            className="product-image"
            src={selectedProduct.image_url}
            alt={selectedProduct.name}
            onError={handleImageError}
          />
          <h2 className="product-title">{selectedProduct.brand} - {selectedProduct.name}</h2>
          {loadingIngredients ? (
            <p>Loading ingredients...</p>
          ) : (
            <>
              <p className="product-description">Ingredients:</p>
              {selectedProduct.ingredients && selectedProduct.ingredients.length > 0 ? (
                <ul className="ingredients-list">
                  {selectedProduct.ingredients.map((ingredient, index) => (
                    <li key={index}>
                      {highlightPoreCloggingIngredients(ingredient.name, ingredient.matching_pore_clogging_ingredients)}
                    </li>
                  ))}
                </ul>
              ) : (
                <p>No ingredients information available.</p>
              )}
            </>
          )}
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
