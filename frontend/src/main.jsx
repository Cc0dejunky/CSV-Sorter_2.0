import { useState, useEffect } from 'react'
import './App.css'

// IMPORTANT: Double-check that this ID matches your browser URL bar!
const BASE_URL = 'https://expert-rotary-phone-9756jw66ww9v247r-8000.app.github.dev/'

function App() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchProducts()
  }, [])

  const fetchProducts = async () => {
    try {
      setLoading(true)
      const res = await fetch(`${BASE_URL}/products`)
      if (!res.ok) throw new Error("Backend not responding")
      const data = await res.json()
      setProducts(data)
      setError(null)
    } catch (err) {
      setError("Still in Demo Mode: Connection to Port 8000 Failed")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="gallery-container">
      <header className="sticky-header">
        <h1>PRODUCT COMMAND CENTER</h1>
        {error && <div className="connection-alert">{error}</div>}
      </header>

      <div className="product-grid">
        {products.map(p => (
          <div key={p.id} className="manager-card">
            <div className="card-image-container">
               <img src={p.variant_image || 'https://via.placeholder.com/200'} alt="Product" className="product-img" />
            </div>
            <h2>{p.text_content}</h2>
            <div className="price-row">
              <span className="price">${p.price}</span>
            </div>
            <input 
              type="text" 
              className="neon-input-small" 
              placeholder="Edit title and hit Enter..." 
              onKeyDown={(e) => {
                if(e.key === 'Enter') {
                   // Logic for your 160wpm fast-save goes here
                   console.log("Saving:", e.target.value)
                }
              }}
            />
          </div>
        ))}
      </div>
      
      <button className="massive-submit-btn">PUBLISH ALL CHANGES</button>
    </div>
  )
}

export default App