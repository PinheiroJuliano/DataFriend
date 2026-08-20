import { useState, useRef } from 'react'
import type { DatasetMetadata, ChatResponse } from './types'
import { uploadDataset, sendQuestion } from './services/api'
import './App.css'

function App() {
  const [dataset, setDataset] = useState<DatasetMetadata | null>(null)
  const [question, setQuestion] = useState('')
  const [chatResult, setChatResult] = useState<ChatResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    setError('')
    try {
      const meta = await uploadDataset(file)
      setDataset(meta)
      setChatResult(null)
      setQuestion('')
    } catch (err: any) {
      setError(err.message)
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const handleQuestion = async () => {
    if (!dataset || !question.trim()) return

    setLoading(true)
    setError('')
    try {
      const result = await sendQuestion({
        dataset_id: dataset.dataset_id,
        question: question.trim(),
      })
      setChatResult(result)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !loading) handleQuestion()
  }

  return (
    <div className="app">
      <header className="header">
        <h1>DataFriend</h1>
        <p>Upload a dataset and ask questions in natural language</p>
      </header>

      <section className="upload-section">
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.xlsx,.xls"
          onChange={handleUpload}
          id="file-upload"
          hidden
        />
        <label htmlFor="file-upload" className="upload-btn">
          {uploading ? 'Uploading...' : 'Upload CSV or XLSX'}
        </label>
      </section>

      {error && <div className="error">{error}</div>}

      {dataset && (
        <section className="dataset-info">
          <h2>Dataset: {dataset.filename}</h2>
          <div className="meta-grid">
            <div className="meta-item">
              <span className="meta-label">Rows</span>
              <span className="meta-value">{dataset.rows_count}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Columns</span>
              <span className="meta-value">{dataset.columns_count}</span>
            </div>
          </div>
          <details className="schema-details">
            <summary>Schema</summary>
            <table className="schema-table">
              <thead>
                <tr><th>Column</th><th>Type</th></tr>
              </thead>
              <tbody>
                {Object.entries(dataset.schema_info).map(([col, type]) => (
                  <tr key={col}><td>{col}</td><td>{type}</td></tr>
                ))}
              </tbody>
            </table>
          </details>
        </section>
      )}

      {dataset && (
        <section className="chat-section">
          <div className="question-row">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question about your data..."
              disabled={loading}
            />
            <button onClick={handleQuestion} disabled={loading || !question.trim()}>
              {loading ? 'Thinking...' : 'Ask'}
            </button>
          </div>
        </section>
      )}

      {chatResult && (
        <section className="results-section">
          <div className="answer-box">
            <h3>Answer</h3>
            <p>{chatResult.answer}</p>
          </div>

          <div className="sql-box">
            <h3>SQL</h3>
            <pre><code>{chatResult.sql}</code></pre>
          </div>

          {chatResult.columns.length > 0 && (
            <div className="table-box">
              <h3>Results</h3>
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>{chatResult.columns.map((col) => <th key={col}>{col}</th>)}</tr>
                  </thead>
                  <tbody>
                    {chatResult.rows.map((row, i) => (
                      <tr key={i}>{row.map((cell, j) => <td key={j}>{String(cell)}</td>)}</tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </section>
      )}
    </div>
  )
}

export default App
