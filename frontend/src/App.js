import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [recommendedProducts, setRecommendedProducts] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    if (searchTerm) {
      setShowDropdown(true);
      axios.get(`http://127.0.0.1:5000/recommend-products?name=${searchTerm}`)
        .then(response => {
          setRecommendedProducts(response.data.slice(0, 5));
        })
        .catch(() => {
          setRecommendedProducts([]);
        });
    } else {
      setShowDropdown(false);
    }
  }, [searchTerm]);

  const handleProductSelect = (product) => {
    setSelectedProduct(product); // Set the selected product
    console.log('Selected product ingredients:', product.ingredients); // Inspect ingredients
    setShowDropdown(false); // Hide dropdown after selection
};

  const handleImageError = (e) => {
    console.error('Image failed to load:', e.target.src);
    e.target.onerror = null;
    e.target.src = '/path_to_default_image.jpg'; // Make sure this path is correct
  };

  return (
    <div className="App">
      <div className="header">
        <img src="/path_to_your_logo.jpg" alt="Skinform logo" style={{ height: '50px' }} />
        <h1>Pore-Clogging Product Search & Ingredient Checker</h1>
        <p>Search our analyzed products or paste any product's ingredients to check for pore-clogging ingredients.</p>
      </div>
    <div className="App">
      <h1>Skincare Product Search</h1>
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Search Products..."
      />

      {showDropdown && (
        <div className="dropdown">
          {recommendedProducts.map((product, index) => (
            <div key={index} className="suggestion-item" onClick={() => handleProductSelect(product)}>
              <img 
                src={product.image_url} 
                alt={product.name} 
                className="suggestion-image" 
                onError={handleImageError}
              />
              <p className="suggestion-title">{product.brand} - {product.name}</p>
            </div>
          ))}
        </div>
      )}

      {selectedProduct && (
        <div className="product-detail">
          <img 
            src={selectedProduct.image_url} 
            alt={selectedProduct.name} 
            className="product-image" 
            onError={handleImageError}
          />
          <div>
            <h2 className="product-title">{selectedProduct.brand} - {selectedProduct.name}</h2>
            <h3>Ingredients:</h3>
            {selectedProduct.ingredients && selectedProduct.ingredients.length > 0 ? (
              <ul className="ingredients-list">
                {selectedProduct.ingredients.map((ingredient, index) => (
                  <li key={index}>{ingredient}</li>
                ))}
              </ul>
            ) : (
              <p>No ingredients information available.</p>
            )}
          </div>
        </div>
      )}
    </div>
  </div>
  );
}

export default App;