import { useState, useEffect, useRef } from 'react'

const BASE_URL = 'https://expert-rotary-phone-9756jw66ww9v247r-5173.app.github.dev'

const NEON = {
  pink: '#ff00ff',
  aqua: '#00ffff',
  teal: '#00ffcc',
  purple: '#bc13fe',
  darkBlue: '#1b03a3'
}

function App() {
  const [products, setProducts] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [correction, setCorrection] = useState('')
  const [loading, setLoading] = useState(true)
  const inputRef = useRef(null)

  useEffect(() => {
    fetchProducts()
  }, [])

  useEffect(() => {
    if (inputRef.current) inputRef.current.focus()
  }, [currentIndex, loading])

  const fetchProducts = async () => {
    try {
      const response = await fetch(`${BASE_URL}/products`)
      const data = await response.json()
      setProducts(data)
      setLoading(false)
    } catch (error) {
      console.error(error)
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleFeedback(correction === '')
    }
  }

  const handleFeedback = async (isApproved) => {
    const product = products[currentIndex]
    try {
      await fetch(`${BASE_URL}/products/${product.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: isApproved ? 'approved' : 'corrected',
          text_content: isApproved ? product.text_content : correction
        }),
      })

      if (currentIndex < products.length - 1) {
        setCurrentIndex(prev => prev + 1)
        setCorrection('')
      } else {
        alert("🎯 Batch Complete!")
        fetchProducts()
      }
    } catch (error) { console.error(error) }
  }

  if (loading) return <div style={styles.loader}>INITIALIZING TECH-WHITE...</div>

  const current = products[currentIndex]

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.header}>
          <h2 style={styles.h2}>ITEM {currentIndex + 1} / {products.length}</h2>
          {currentIndex > 0 && <button onClick={() => setCurrentIndex(p => p - 1)} style={styles.backBtn}>← ESC PREV</button>}
        </div>

        <div style={styles.contentArea}>
          <h5 style={styles.h5}>RAW DATA INPUT</h5>
          <div style={styles.rawText}>{current.text_content}</div>
        </div>

        <div style={styles.inputSection}>
          <input
            ref={inputRef}
            type="text"
            value={correction}
            onChange={(e) => setCorrection(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type revised title & hit Enter..."
            style={styles.input}
          />
          <div style={styles.hint}>
            <strong>ENTER</strong> to Submit | <strong>EMPTY + ENTER</strong> to Approve
          </div>
        </div>
      </div>
    </div>
  )
}

const styles = {
  container: { 
    minHeight: '100vh', 
    backgroundColor: '#fdfdfd', // Tech-White background
    display: 'flex', 
    alignItems: 'center', 
    justifyContent: 'center', 
    fontFamily: '"Segoe UI", Roboto, sans-serif'
  },
  card: { 
    width: '90%', 
    maxWidth: '700px', 
    backgroundColor: '#ffffff', 
    borderRadius: '16px', 
    padding: '40px', 
    // Multi-layer Box Shadow
    boxShadow: `
      0 10px 15px -3px rgba(0, 0, 0, 0.1), 
      0 4px 6px -2px rgba(0, 0, 0, 0.05),
      0 0 20px rgba(0, 255, 255, 0.1)
    `,
    border: '4px solid',
    // Pink to Aqua Gradient Border
    borderImageSource: `linear-gradient(to right, ${NEON.pink}, ${NEON.aqua})`,
    borderImageSlice: 1,
  },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' },
  h2: { 
    color: 'white',
    fontSize: '24px',
    margin: 0,
    // Triple layer Purple Neon shadow
    textShadow: `2px 2px 0px ${NEON.purple}, 4px 4px 10px ${NEON.purple}, 0 0 15px ${NEON.purple}`
  },
  h5: {
    color: 'white',
    fontSize: '14px',
    letterSpacing: '2px',
    margin: '0 0 10px 0',
    // Triple layer Teal Neon shadow
    textShadow: `1px 1px 0px ${NEON.teal}, 2px 2px 5px ${NEON.teal}, 0 0 10px ${NEON.teal}`
  },
  backBtn: { background: 'none', border: `1px solid ${NEON.darkBlue}`, color: '#334155', cursor: 'pointer', padding: '5px 10px', borderRadius: '4px', fontSize: '10px', fontWeight: 'bold' },
  contentArea: { marginBottom: '40px' },
  rawText: { 
    fontSize: '18px', 
    lineHeight: '1.6', 
    color: '#1e293b', 
    backgroundColor: '#f8fafc',
    padding: '20px',
    borderRadius: '8px',
    border: '1px solid #e2e8f0'
  },
  inputSection: { paddingTop: '20px' },
  input: { 
    width: '100%', 
    backgroundColor: '#ffffff', 
    border: `2px solid ${NEON.aqua}`, 
    borderRadius: '8px', 
    padding: '15px', 
    color: '#0f172a', 
    fontSize: '18px', 
    boxSizing: 'border-box',
    boxShadow: `0 0 10px ${NEON.aqua}44`
  },
  hint: { marginTop: '15px', textAlign: 'center', fontSize: '12px', color: '#64748b' },
  loader: { height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', color: NEON.pink, fontWeight: 'bold' }
}

export default App