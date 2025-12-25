import { useState, useEffect } from 'react'

function App() {
  const [products, setProducts] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [correction, setCorrection] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProducts()
  }, [])

  const fetchProducts = async () => {
    try {
      const response = await fetch('http://localhost:8000/products-for-review')
      const data = await response.json()
      setProducts(data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching products:', error)
      setLoading(false)
    }
  }

  const handleFeedback = async (isApproved) => {
    const product = products[currentIndex]
    
    try {
      await fetch('http://localhost:8000/submit-feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          product_id: product.id,
          is_approved: isApproved,
          correction: isApproved ? null : correction
        }),
      })

      // Move to next product
      if (currentIndex < products.length - 1) {
        setCurrentIndex(prev => prev + 1)
        setCorrection('')
      } else {
        // Refresh list if we're done
        setLoading(true)
        setCurrentIndex(0)
        setCorrection('')
        fetchProducts()
      }
    } catch (error) {
      console.error('Error submitting feedback:', error)
    }
  }

  if (loading) return <div className="p-8 text-center text-gray-600">Loading...</div>
  if (products.length === 0) return <div className="p-8 text-center text-gray-600">No products to review! Upload a CSV to get started.</div>

  const currentProduct = products[currentIndex]

  return (
    <div className="min-h-screen bg-gray-100 p-8 flex items-center justify-center">
      <div className="w-full max-w-2xl bg-white rounded-xl shadow-lg overflow-hidden p-8">
        <h1 className="text-2xl font-bold mb-6 text-gray-800">Product Review ({currentIndex + 1}/{products.length})</h1>
        
        <div className="mb-8">
          <h2 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Original Text</h2>
          <p className="text-xl text-gray-900 bg-gray-50 p-4 rounded-lg border border-gray-200">{currentProduct.text}</p>
        </div>

        <div className="flex flex-col gap-4">
          <button 
            onClick={() => handleFeedback(true)}
            className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded-lg transition duration-200"
          >
            Approve
          </button>

          <div className="relative my-2">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">Or Correct</span>
            </div>
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              value={correction}
              onChange={(e) => setCorrection(e.target.value)}
              placeholder="Type correct product name..."
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button 
              onClick={() => handleFeedback(false)}
              disabled={!correction}
              className="bg-red-500 hover:bg-red-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-bold py-2 px-6 rounded-lg transition duration-200"
            >
              Submit
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App