import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [recommendedProducts, setRecommendedProducts] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);

  function highlightText(fullText, searchTerm) {
    // Guard clauses for empty inputs
    if (!fullText || !searchTerm) return fullText;
  
    // Trim and escape special characters in searchTerm to safely use in regex
    const escapedSearchTerm = searchTerm.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    // Regex to match each word in the search term separately
    const regexPattern = escapedSearchTerm.split(/\s+/).map(word => {
      // Return pattern to match word at a word boundary or part of it
      return `(${word})`;
    }).join("|");
  
    const regex = new RegExp(regexPattern, 'gi');
    const parts = fullText.split(regex);
    
    // Reconstruct the string with highlighted matches
    return parts.map(part => regex.test(part) ? <strong>{part}</strong> : part);
  }
  
  
  
  useEffect(() => {
    if (searchTerm) {
      axios.get(`http://127.0.0.1:5000/recommend-products?name=${searchTerm}`)
        .then(response => {
          const results = response.data.slice(0, 5); // Limit to 5 products
          setRecommendedProducts(results);
          setShowDropdown(results.length > 0); // Only show dropdown if there are results
        })
        .catch(() => {
          setRecommendedProducts([]);
          setShowDropdown(false); // Ensure dropdown is not shown on error
        });
    } else {
      setRecommendedProducts([]);
      setShowDropdown(false);
    }
  }, [searchTerm]);

  const handleProductSelect = (product) => {
    console.log('Product selected:', product);  // Check the full product structure
    setSelectedProduct(product);
    setShowDropdown(false); // Hide dropdown after selection
  };
  
  useEffect(() => {
    if (searchTerm) {
      axios.get(`http://127.0.0.1:5000/recommend-products?name=${searchTerm}`)
        .then(response => {
          console.log('Fetched products:', response.data); // Log fetched data
          const results = response.data; 
          setRecommendedProducts(results);
          setShowDropdown(results.length > 0); // Only show dropdown if there are results
        })
        .catch(error => {
          console.error('Error fetching recommended products:', error);
          setRecommendedProducts([]);
          setShowDropdown(false); // Ensure dropdown is not shown on error
        });
    } else {
      setRecommendedProducts([]);
      setShowDropdown(false);
    }
  }, [searchTerm]);  

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
                  src={product.image_url} // Make sure this is the correct property
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
          <p className="product-description">Ingredients:</p>
          {selectedProduct && selectedProduct.ingredients && selectedProduct.ingredients.length > 0 ? (
            <ul className="ingredients-list">
              {selectedProduct.ingredients.map((ingredient, index) => (
                <li key={index} style={{ color: ingredient.is_pore_clogging ? 'red' : 'inherit' }}>
                  {ingredient.name}
                </li>
              ))}
            </ul>
          ) : (
            <p>No ingredients information available.</p>
          )}
        </div>
      )}
    </div>
  );
}

export default App;