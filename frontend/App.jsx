import { useMemo, useState } from 'react'
import './App.css'

const mockEmotionResult = {
  label: 'Calm',
  confidence: 0.86,
  cues: ['Soft wording', 'Neutral sentiment', 'Steady pacing'],
}

function App() {
  const [textInput, setTextInput] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState(null)

  const isReadyToAnalyze = useMemo(() => {
    return textInput.trim().length > 0
  }, [textInput])

  const handleAnalyze = async () => {
    if (!isReadyToAnalyze) return
    setIsAnalyzing(true)
    
    try {
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: textInput,
        }),
      })
      
      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }
      
      const data = await response.json()
      
      // Transform API response to match frontend format
      const emotionLabels = {
        'anger': 'Angry',
        'fear': 'Fearful',
        'joy': 'Joyful',
        'love': 'Loving',
        'sadness': 'Sad',
        'surprise': 'Surprised',
        'neutral': 'Neutral'
      }
      
      // Generate cues from probabilities
      const cues = Object.entries(data.probabilities)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 3)
        .map(([emotion, prob]) => {
          const label = emotionLabels[emotion] || emotion
          return `${label}: ${(prob * 100).toFixed(1)}%`
        })
      
      setResult({
        label: emotionLabels[data.emotion] || data.emotion,
        confidence: data.confidence,
        cues: cues,
        probabilities: data.probabilities
      })
    } catch (error) {
      console.error('Error analyzing emotion:', error)
      // Fallback to mock result if API fails
      setResult({
        ...mockEmotionResult,
        label: 'Error',
        confidence: 0,
        cues: [`Failed to analyze: ${error.message}`],
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <main className="page">
      <header className="hero">
        <div>
          <p className="eyebrow">Truetone AI</p>
          <h1>Express yourself through text</h1>
          <p className="sub">
            Share your thoughts to detect emotion.
          </p>
        </div>
      </header>

      <section className="panel highlight">
        <div className="panel-body">
            <div className="panel-graphic">
            <div className="badge">Live</div>
            <div className="masks">
              <span aria-hidden>🎭</span>
            </div>
            <p>Type to detect emotion</p>
          </div>
          <div className="panel-card">
            <label className="input-stack">
              <span className="label">Input text to analyze?</span>
              <textarea
                placeholder="Input a thought or short message..."
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                rows={6}
              />
            </label>

            <button
              className="analyze"
              disabled={!isReadyToAnalyze || isAnalyzing}
              onClick={handleAnalyze}
            >
              {isAnalyzing ? 'Analyzing…' : 'Analyze'}
            </button>

            <div className="divider" />

            <div className="result">
              <div className="result-header">
                <span className="result-title">Emotion</span>
                <span className="pill">Model active</span>
              </div>
              {result ? (
                <>
                  <p className="emotion-label">{result.label}</p>
                  <p className="confidence">
                    Confidence: {(result.confidence * 100).toFixed(1)}%
                  </p>
                  <ul className="cues">
                    {result.cues.map((cue, index) => (
                      <li key={index}>{cue}</li>
                    ))}
                  </ul>
                  {result.probabilities && (
                    <div style={{ marginTop: '1rem', fontSize: '0.875rem', opacity: 0.8 }}>
                      <details>
                        <summary style={{ cursor: 'pointer', marginBottom: '0.5rem' }}>
                          View all probabilities
                        </summary>
                        <ul style={{ listStyle: 'none', padding: 0 }}>
                          {Object.entries(result.probabilities)
                            .sort(([, a], [, b]) => b - a)
                            .map(([emotion, prob]) => (
                              <li key={emotion} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                                <span>{emotion}:</span>
                                <span>{(prob * 100).toFixed(2)}%</span>
                              </li>
                            ))}
                        </ul>
                      </details>
                    </div>
                  )}
                </>
              ) : (
                <p className="placeholder">
                  Results will appear here once you analyze some text.
                </p>
              )}
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}

export default App
