import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [recommendedProducts, setRecommendedProducts] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [loadingIngredients, setLoadingIngredients] = useState(false);

  const [pastedIngredients, setPastedIngredients] = useState('');
  const [poreCloggingResults, setPoreCloggingResults] = useState([]);

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

  useEffect(() => {
    if (searchTerm) {
      axios.get(`http://127.0.0.1:5000/recommend-products?name=${searchTerm}`)
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
    console.log('Product selected:', product);  // This should show the full product structure
    if (!product.name) {
      console.error('Product name is undefined:', product);
      return; // Stop further execution if no product name is available
    }
  
    setSelectedProduct(product);
    setShowDropdown(false);
    fetchProductIngredients(product.name); // Fetch ingredients by product name
  };  

  const fetchProductIngredients = (productName) => {
    setLoadingIngredients(true);  // Set loading state
    axios.get(`http://127.0.0.1:5000/product-ingredients/${encodeURIComponent(productName)}`)
      .then(response => {
        console.log("API Response:", response.data);  // Log the full API response
        const updatedProduct = { ...selectedProduct, ...response.data };
        setSelectedProduct(updatedProduct); // Update product with all data
        setLoadingIngredients(false);  // Turn off loading
      })
      .catch(error => {
        console.error('Error fetching product ingredients:', error);
        setLoadingIngredients(false);  // Turn off loading even on error
      });
  };

  const checkPoreCloggingIngredients = () => {
    if (!pastedIngredients.trim()) {
      return;
    }
  
    axios.post('http://127.0.0.1:5000/check-ingredients', { ingredients: pastedIngredients })
      .then(response => {
        setPoreCloggingResults(response.data);
      })
      .catch(error => {
        console.error('Error checking ingredients:', error);
      });
  };
  

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
    console.error('Image failed to load:', e.target.src);
    e.target.onerror = null;
    e.target.src = '/path_to_default_image.jpg'; // Default image path
  };

  return (
    <div className="App">
      <h1>Pore-Clogging Product Search & Ingredient Checker</h1>
      <p>Search our analyzed products or paste any product's ingredients to check for pore-clogging ingredients.</p>
      <div className="search-container">
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

      {selectedProduct && (
      <div className="product-detail">
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
      <div className="ingredient-checker">
        <h2>Ingredient Checker</h2>
        <textarea
          value={pastedIngredients}
          onChange={(e) => setPastedIngredients(e.target.value)}
          placeholder="Paste Ingredients"
          className="pasted-ingredients"
        />
        <div>
          <button onClick={checkPoreCloggingIngredients}>Check</button>
          <button onClick={() => setPastedIngredients('')}>Clear</button>
        </div>
        {poreCloggingResults.length > 0 && (
            <div className="pore-clogging-results">
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
    </div>
  );
}

export default App;
