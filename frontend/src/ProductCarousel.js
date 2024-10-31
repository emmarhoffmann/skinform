import React, { useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

const ProductCarousel = ({ products, title, isLoading }) => {
  const [flippedCard, setFlippedCard] = useState(null);

  const scroll = (direction) => {
    const container = document.getElementById(`carousel-${title.replace(/\s+/g, '-')}`);
    if (container) {
      container.scrollBy({
        left: direction === 'left' ? -300 : 300,
        behavior: 'smooth'
      });
    }
  };

  if (isLoading) {
    return (
      <div className="w-full">
        <h4 className="text-xl font-bold mb-4">{title}</h4>
        <div className="flex gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="w-48 h-48 bg-gray-200 rounded-lg"></div>
              <div className="h-4 bg-gray-200 rounded mt-2 w-32"></div>
              <div className="h-4 bg-gray-200 rounded mt-2 w-24"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="w-full">
      <h4 className="text-xl font-bold mb-4">{title}</h4>
      <div className="relative group">
        <button 
          onClick={() => scroll('left')} 
          className="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-white/80 rounded-full p-2 shadow-md hover:bg-gray-100"
          aria-label="Scroll left"
        >
          <ChevronLeft size={24} />
        </button>

        <div 
          id={`carousel-${title.replace(/\s+/g, '-')}`}
          className="flex gap-4 overflow-x-auto scroll-smooth hide-scrollbar"
          style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
        >
          {products.map((product) => (
            <div 
              key={product._id || product.id} 
              className="min-w-[200px] relative cursor-pointer"
              onClick={() => setFlippedCard(flippedCard === product._id ? null : product._id)}
            >
              <div 
                className={`relative transform transition-transform duration-500 ${
                  flippedCard === product._id ? 'rotate-y-180' : ''
                }`}
                style={{ transformStyle: 'preserve-3d' }}
              >
                {/* Front of card */}
                <div className="bg-white rounded-lg p-4 shadow">
                  <img 
                    src={product.image_url} 
                    alt={product.name}
                    className="w-48 h-48 object-cover rounded-lg mb-2"
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.src = "/api/placeholder/192/192";
                    }}
                  />
                  <h3 className="font-semibold truncate">{product.brand}</h3>
                  <p className="text-sm text-gray-600 truncate">{product.name}</p>
                </div>

                {/* Back of card - Ingredients */}
                {flippedCard === product._id && (
                  <div 
                    className="absolute inset-0 bg-white rounded-lg p-4 shadow overflow-y-auto"
                    style={{ transform: 'rotateY(180deg)', backfaceVisibility: 'hidden' }}
                  >
                    <h3 className="font-semibold mb-2">Ingredients:</h3>
                    <ul className="text-sm space-y-1">
                      {product.ingredients?.map((ingredient, idx) => (
                        <li 
                          key={idx}
                          className={ingredient.matching_pore_clogging_ingredients?.length ? 'text-red-600' : ''}
                        >
                          {ingredient.name}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <button 
          onClick={() => scroll('right')} 
          className="absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-white/80 rounded-full p-2 shadow-md hover:bg-gray-100"
          aria-label="Scroll right"
        >
          <ChevronRight size={24} />
        </button>
      </div>
    </div>
  );
};

export default ProductCarousel;