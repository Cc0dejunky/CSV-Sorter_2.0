import React, { useState, useEffect } from 'react';
import './App.css';

// Update this with your actual Port 8000 URL from the Ports tab
const BASE_URL = 'https://expert-rotary-phone-9756jw66ww9v247r-8000.app.github.dev';

export default function App() {
  const [products, setProducts] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [feedback, setFeedback] = useState('');

  useEffect(() => {
    fetch(`${BASE_URL}/products`)
      .then(res => res.json())
      .then(data => setProducts(data))
      .catch(err => console.error("Fog Alert: Backend not found", err));
  }, []);

  const handleNext = () => {
    // Logic to save feedback would go here
    setFeedback('');
    setCurrentIndex(prev => prev + 1);
  };

  // THE ENTER KEY LISTENER
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleNext();
    }
  };

  if (products.length === 0) return <div className="loading">INITIALIZING NEON CORE...</div>;

  const currentProduct = products[currentIndex];

  return (
    <div className="app-container">
      <h1 className="neon-title-purple">NEON COMMAND CENTER</h1>
      
      <div className="neon-card">
        <h5 className="neon-teal-label">CURRENT PRODUCT</h5>
        <h2 className="product-text">{currentProduct.text_content}</h2>
        
        <div className="input-wrapper">
          <input 
            autoFocus
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type correction and hit ENTER..."
            className="neon-input"
          />
        </div>
      </div>
    </div>
  );
}



