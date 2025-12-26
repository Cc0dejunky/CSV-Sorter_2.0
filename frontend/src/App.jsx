import { useState, useEffect } from 'react'
import './App.css'

// Use Vite env variable for codespace URL or fall back to localhost:8000
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => { fetchProducts() }, [])

  const normalizeProduct = (p) => ({
    id: p.id,
    text_content: p.text_content || p.text || p.normalized || '',
    category: p.category || p.taxonomy || p.category || null,
    type: p.type || p.product_type || null,
    price: p.variant_price || p.price || p.price || null,
    compare_price: p.variant_compare_at_price || p.compare_price || p.compare_price || null,
    taxable: typeof p.taxable === 'boolean' ? p.taxable : (p.taxable === 1 ? true : (p.taxable === 0 ? false : false)),
    status: p.status || 'Draft',
    variant_image: p.variant_image || p.image || p.image_src || null,
    ...p
  })

  const fetchProducts = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${BASE_URL}/products`)
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
      const data = await res.json()
      const mapped = data.map(normalizeProduct)
      setProducts(mapped)
    } catch (err) {
      setError(`Cannot reach backend at ${BASE_URL}. Verify the Codespace port 8000 forwarding and set VITE_API_URL if needed.`)
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
          <ProductCard key={p.id} product={p} onSaved={fetchProducts} />
        ))}
      </div>
      
      <button className="massive-submit-btn">PUBLISH ALL CHANGES</button>
    </div>
  )
}

function ProductCard({ product, onSaved }) {
  const [editing, setEditing] = useState(false)
  const [title, setTitle] = useState(product.text_content || '')
  const [category, setCategory] = useState(product.category || '')
  const [typeSel, setTypeSel] = useState(product.type || '')
  const [price, setPrice] = useState(product.price || '')
  const [comparePrice, setComparePrice] = useState(product.compare_price || '')
  const [taxable, setTaxable] = useState(Boolean(product.taxable))
  const [status, setStatus] = useState(product.status || 'Draft')
  const [imagePreview, setImagePreview] = useState(product.variant_image || '')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    setTitle(product.text_content || '')
    setCategory(product.category || '')
    setTypeSel(product.type || '')
    setPrice(product.price || '')
    setComparePrice(product.compare_price || '')
    setTaxable(Boolean(product.taxable))
    setStatus(product.status || 'Draft')
    setImagePreview(product.variant_image || '')
  }, [product])

  const handleSave = async () => {
    setSubmitting(true)
    try {
      const correction = JSON.stringify({
        variant_image: imagePreview,
        variant_price: price,
        variant_compare_at_price: comparePrice,
        category,
        type: typeSel,
        taxable,
        status,
        title
      })

      await fetch(`${BASE_URL}/submit-feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: product.id, is_approved: false, correction })
      })

      setEditing(false)
      if (onSaved) onSaved()
    } catch (e) {
      console.error('Save failed', e)
    } finally {
      setSubmitting(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSave()
    }
  }

  return (
    <div className={`manager-card ${editing ? 'editing' : ''}`}>
      <div className="card-header">
        <label className="switch">
          <input type="checkbox" checked={editing} onChange={() => setEditing(s => !s)} />
          <span className="slider"></span>
        </label>
        <h6 className="card-id">ID: {product.id}</h6>
      </div>

      <div className="card-image-container">
        <img src={imagePreview || 'https://via.placeholder.com/200'} alt="Product" className="product-img" />
      </div>

      {!editing ? (
        <div className="info-display">
          <h2>{title}</h2>
          <div className="raw-text-box mini"><strong>Category:</strong> {category || 'No Category'}</div>
          <div className="raw-text-box mini"><strong>Type:</strong> {typeSel || 'No Type'}</div>
          <div className="raw-text-box mini"><strong>Price:</strong> ${price || '0.00'} &nbsp; <strong>Compare:</strong> ${comparePrice || '0.00'}</div>
          <div className="raw-text-box mini"><strong>Taxable?</strong> {taxable ? 'True' : 'False'}</div>
          <div className="status-indicator"><strong>Status:</strong> {status}</div>
        </div>
      ) : (
        <div className="edit-form" onKeyDown={handleKeyDown}>
          <input autoFocus value={title} onChange={(e) => setTitle(e.target.value)} className="neon-input-small" />
          <input value={category} onChange={(e) => setCategory(e.target.value)} className="neon-input-small" placeholder="Category" />
          <input value={typeSel} onChange={(e) => setTypeSel(e.target.value)} className="neon-input-small" placeholder="Type" />
          <input value={price} onChange={(e) => setPrice(e.target.value)} className="neon-input-small" placeholder="Price" />
          <input value={comparePrice} onChange={(e) => setComparePrice(e.target.value)} className="neon-input-small" placeholder="Compare Price" />
          <label><input type="checkbox" checked={taxable} onChange={(e) => setTaxable(e.target.checked)} /> Taxable?</label>
          <select value={status} onChange={(e) => setStatus(e.target.value)} className="neon-select">
            <option>Active</option>
            <option>Draft</option>
          </select>
          <div className="card-actions">
            <button onClick={handleSave} disabled={submitting}>Save</button>
            <button onClick={() => setEditing(false)} disabled={submitting}>Cancel</button>
          </div>
        </div>
      )}
    </div>
  )
}

export default App