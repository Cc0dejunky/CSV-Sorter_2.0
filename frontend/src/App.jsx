import React, { useState, useEffect, useRef } from 'react';

// BRAND COLORS: Neon Accents
const NEON = { pink: '#ff00ff', aqua: '#00ffff', teal: '#00ffcc', purple: '#bc13fe', darkBlue: '#1b03a3' };

// FIXED: Now points to the BACKEND port (8000)
const BASE_URL = 'https://expert-rotary-phone-9756jw66ww9v247r-8000.app.github.dev';

export default function App() {
  const [products, setProducts] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [correction, setCorrection] = useState('');
  const [loading, setLoading] = useState(true);
  const inputRef = useRef(null);

  useEffect(() => {
    fetch(`${BASE_URL}/products`)
      .then(res => res.json())
      .then(data => {
        // Handle both "all" and "pending" results
        const items = Array.isArray(data) ? data : [];
        setProducts(items);
        setLoading(false);
      })
      .catch(err => {
        console.error("Backend unreachable on port 8000:", err);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (inputRef.current) inputRef.current.focus();
  }, [currentIndex, loading]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      const isApproved = correction.trim() === '';
      handleFeedback(isApproved);
    }
  };

  const handleFeedback = async (isApproved) => {
    if (products.length === 0) return;
    const product = products[currentIndex];
    
    try {
      await fetch(`${BASE_URL}/submit-feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: product.id,
          is_approved: isApproved,
          correction: isApproved ? product.text_content : correction
        }),
      });

      if (currentIndex < products.length - 1) {
        setCurrentIndex(prev => prev + 1);
        setCorrection('');
      } else {
        alert("🎯 Batch Complete!");
        setLoading(true);
        window.location.reload(); 
      }
    } catch (error) { console.error("Submit error:", error); }
  };

  if (loading) return <div style={styles.loader}>INITIALIZING NEON...</div>;
  if (products.length === 0) return <div style={styles.loader}>NO PRODUCTS FOUND - CHECK DEV.DB</div>;

  const current = products[currentIndex];

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.header}>
          <h2 style={styles.h2}>ITEM {currentIndex + 1} / {products.length}</h2>
        </div>

        <div style={styles.contentArea}>
          <h5 style={styles.h5}>RAW DATA INPUT</h5>
          <div style={styles.rawText}>{current.text_content || current.text}</div>
        </div>

        <div style={styles.inputSection}>
          <input
            ref={inputRef}
            type="text"
            value={correction}
            onChange={(e) => setCorrection(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type revision & hit Enter..."
            style={styles.input}
          />
          <div style={styles.hint}>
            <strong>ENTER</strong> to Submit | <strong>EMPTY + ENTER</strong> to Approve
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: { minHeight: '100vh', backgroundColor: '#fdfdfd', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'sans-serif' },
  card: { width: '90%', maxWidth: '600px', backgroundColor: 'white', borderRadius: '16px', padding: '40px', boxShadow: '0 20px 40px rgba(0,0,0,0.1)', border: '4px solid transparent', borderImageSource: `linear-gradient(to right, ${NEON.pink}, ${NEON.aqua})`, borderImageSlice: 1 },
  header: { marginBottom: '30px' },
  h2: { color: 'white', textShadow: `2px 2px 0px ${NEON.purple}, 4px 4px 10px ${NEON.purple}` },
  h5: { color: 'white', textShadow: `1px 1px 0px ${NEON.teal}, 2px 2px 5px ${NEON.teal}`, letterSpacing: '1px' },
  contentArea: { marginBottom: '30px' },
  rawText: { fontSize: '20px', color: '#1e293b', backgroundColor: '#f8fafc', padding: '20px', borderRadius: '8px', border: '1px solid #e2e8f0' },
  input: { width: '100%', border: `2px solid ${NEON.aqua}`, borderRadius: '8px', padding: '15px', fontSize: '18px', outline: 'none' },
  hint: { marginTop: '15px', textAlign: 'center', fontSize: '12px', color: '#64748b' },
  loader: { height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', color: NEON.pink, fontWeight: 'bold', fontSize: '24px' }
};