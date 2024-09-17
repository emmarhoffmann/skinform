import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const [product, setProduct] = useState(null);
  const [error, setError] = useState(null);
  const [recommendedProducts, setRecommendedProducts] = useState([]);

  // Debounce timer to delay searching until the user stops typing
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchTerm) {
        axios.get(`http://127.0.0.1:5000/search-products?name=${searchTerm}`)
          .then(response => {
            if (response.data.products && response.data.products.length > 0) {
              setProduct(response.data.products[0]);
              setError(null);
              setRecommendedProducts([]); // Clear recommendations when exact product is found
            } else {
              setProduct(null);
              setRecommendedProducts([]); // Clear recommendations
            }
          })
          .catch(() => {
            setError('Product not found');
            setProduct(null);
            setRecommendedProducts([]); // Clear recommendations if search fails
          });

        // Fetch recommended products
        axios.get(`http://127.0.0.1:5000/recommend-products?name=${searchTerm}`)
          .then(response => {
            if (response.data.length > 0) {
              setRecommendedProducts(response.data);
            } else {
              setRecommendedProducts([]);
            }
          })
          .catch(() => {
            setRecommendedProducts([]); // Clear recommendations if recommendation API fails
          });
      } else {
        setProduct(null);
        setRecommendedProducts([]);
      }
    }, 500); // Delay the search by 500ms

    return () => clearTimeout(timer);
  }, [searchTerm]);

  return (
    <div className="App">
      <h1>Skincare Product Search</h1>
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Enter product name or brand"
      />

      {error && <p>{error}</p>}

      {product && (
        <div>
          <h2>{product.name}</h2>
          <p>Brand: {product.brand}</p>
          <img src={product.image_url} alt={product.name} style={{ width: '150px', height: '150px' }} />
          <h4>Ingredients:</h4>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {product.ingredients.map((ingredient, index) => (
              <li
                key={index}
                style={{ display: 'inline', color: product.pore_clogging && product.pore_clogging.includes(ingredient) ? 'red' : 'black' }}
              >
                {ingredient}
                {index !== product.ingredients.length - 1 && ', '}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommended products */}
      {recommendedProducts.length > 0 && (
        <div>
          <h3>Recommended Products:</h3>
          <ul>
            {recommendedProducts.map((recProduct, index) => (
              <li key={index}>
                <h4>{recProduct.name}</h4>
                <p>Brand: {recProduct.brand}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;