import { useState, useRef, useEffect, useCallback } from 'react'
import type { DatasetMetadata, ChatResponse } from './types'
import { uploadDataset, sendQuestion, connectURL, connectDB, connectKaggle } from './services/api'
import './App.css'

type TabMode = 'upload' | 'url' | 'db' | 'kaggle'

function App() {
  const [dataset, setDataset] = useState<DatasetMetadata | null>(null)
  const [question, setQuestion] = useState('')
  const [chatResult, setChatResult] = useState<ChatResponse | null>(null)
  const [typedAnswer, setTypedAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState<TabMode>('upload')
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [detailsOpen, setDetailsOpen] = useState(false)
  const [apiUrl, setApiUrl] = useState('')
  const [apiName, setApiName] = useState('')
  const [dbConnStr, setDbConnStr] = useState('')
  const [dbQuery, setDbQuery] = useState('')
  const [dbName, setDbName] = useState('')
  const [kaggleDataset, setKaggleDataset] = useState('')
  const [kaggleFile, setKaggleFile] = useState('')
  const [kaggleName, setKaggleName] = useState('')
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => { if (!dataset) setSettingsOpen(true) }, [dataset])

  useEffect(() => {
    if (chatResult?.answer) {
      let index = 0
      setTypedAnswer('')
      const words = chatResult.answer.split(' ')
      let currentText = ''
      const interval = setInterval(() => {
        if (index < words.length) {
          currentText += (index === 0 ? '' : ' ') + words[index]
          setTypedAnswer(currentText)
          index++
        } else clearInterval(interval)
      }, 35)
      return () => clearInterval(interval)
    } else setTypedAnswer('')
  }, [chatResult])

  const processFile = useCallback(async (file: File) => {
    setUploading(true); setError('')
    try {
      const meta = await uploadDataset(file)
      setDataset(meta); setChatResult(null); setQuestion(''); setSettingsOpen(false)
    } catch (err: any) { setError(err.message) }
    finally { setUploading(false); if (fileInputRef.current) fileInputRef.current.value = '' }
  }, [])

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault(); e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true)
    else if (e.type === 'dragleave') setDragActive(false)
  }, [])

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault(); e.stopPropagation(); setDragActive(false)
    const file = e.dataTransfer.files?.[0]
    if (file) await processFile(file)
  }, [processFile])

  const handleConnectURL = async () => {
    if (!apiUrl.trim()) return; setUploading(true); setError('')
    try {
      const meta = await connectURL(apiUrl.trim(), apiName.trim() || undefined)
      setDataset(meta); setChatResult(null); setQuestion(''); setSettingsOpen(false); setApiUrl(''); setApiName('')
    } catch (err: any) { setError(err.message) } finally { setUploading(false) }
  }

  const handleConnectDB = async () => {
    if (!dbConnStr.trim() || !dbQuery.trim()) return; setUploading(true); setError('')
    try {
      const meta = await connectDB(dbConnStr.trim(), dbQuery.trim(), dbName.trim() || undefined)
      setDataset(meta); setChatResult(null); setQuestion(''); setSettingsOpen(false); setDbConnStr(''); setDbQuery(''); setDbName('')
    } catch (err: any) { setError(err.message) } finally { setUploading(false) }
  }

  const handleConnectKaggle = async () => {
    if (!kaggleDataset.trim() || !kaggleFile.trim()) return; setUploading(true); setError('')
    try {
      const meta = await connectKaggle(kaggleDataset.trim(), kaggleFile.trim(), kaggleName.trim() || undefined)
      setDataset(meta); setChatResult(null); setQuestion(''); setSettingsOpen(false); setKaggleDataset(''); setKaggleFile(''); setKaggleName('')
    } catch (err: any) { setError(err.message) } finally { setUploading(false) }
  }

  const handleQuestion = async () => {
    if (!dataset || !question.trim()) return; setLoading(true); setError('')
    try {
      const result = await sendQuestion({ dataset_id: dataset.dataset_id, question: question.trim() })
      setChatResult(result)
    } catch (err: any) { setError(err.message) } finally { setLoading(false) }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); if (!loading && question.trim()) handleQuestion() }
  }

  const handleNewQuestion = () => { setChatResult(null); setQuestion('') }

  const closeAll = () => { setSettingsOpen(false); setDetailsOpen(false) }

  return (
    <div className="app">
      <div className="top-bar">
        <div className="top-bar-left">
          {dataset && (
            <button className={`icon-btn ${detailsOpen ? 'active' : ''}`} onClick={() => { setDetailsOpen(!detailsOpen); setSettingsOpen(false) }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="15" y2="12"/><line x1="3" y1="18" x2="18" y2="18"/></svg>
            </button>
          )}
        </div>
        <div className="top-bar-center">DataFriend</div>
        <div className="top-bar-right">
          <button className={`icon-btn ${settingsOpen ? 'active' : ''}`} onClick={() => { setSettingsOpen(!settingsOpen); setDetailsOpen(false) }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 112.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>
          </button>
        </div>
      </div>

      <div className="orb-area">
        <div className={`orb-wrapper ${loading ? 'state-loading' : chatResult ? 'state-answer' : 'state-input'}`}>
          <div className="orb-glow-layer" />
          <div className="orb-ring ring-outer" />
          <div className="orb-ring ring-middle" />
          <div className="orb-ring ring-inner" />
          <div className="orb-core">
            {!loading && !chatResult && (
              <div className="orb-content orb-content-input">
                <div className="orb-header-tiny">Ready to Analyze</div>
                <textarea className="orb-textarea" value={question} onChange={(e) => setQuestion(e.target.value)} onKeyDown={handleKeyDown} placeholder={dataset ? "Ask a question about your data..." : "Load a dataset first..."} rows={3} disabled={!dataset} />
                <button className="orb-action-btn" onClick={handleQuestion} disabled={!question.trim() || !dataset || loading}>
                  <span>Ask</span>
                  <svg className="btn-icon" viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                </button>
              </div>
            )}
            {loading && (
              <div className="orb-content orb-content-loading">
                <div className="orb-spinner"><div className="pulse-circle" /><div className="orbit-dot" /></div>
                <div className="loading-status"><span>Thinking</span><span className="dots" /></div>
                <p className="loading-sub">Running SQL &amp; analyzing</p>
              </div>
            )}
            {chatResult && !loading && (
              <div className="orb-content orb-content-answer">
                <div className="answer-scroll-container">
                  <div className="orb-answer-title">Answer</div>
                  <div className="orb-answer-text animate-fade-in">{typedAnswer}</div>
                </div>
                <button className="orb-new-question-btn" onClick={handleNewQuestion}>
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99"/></svg>
                  <span>New Question</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {(settingsOpen || detailsOpen) && <div className="slide-overlay open" onClick={closeAll} />}

      <div className={`slide-panel left ${detailsOpen ? 'open' : ''}`}>
        <div className="slide-header">
          <h2>Details</h2>
          <button className="slide-close" onClick={() => setDetailsOpen(false)}><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg></button>
        </div>
        <div className="slide-body">
          {error && <div className="error-msg">{error}</div>}
          {dataset && (
            <div className="dataset-info-mini">
              <h3>Dataset</h3>
              <p className="dataset-name">{dataset.filename}</p>
              <div className="dataset-meta"><span>{dataset.rows_count.toLocaleString()} rows</span><span>{dataset.columns_count} columns</span></div>
              <details className="schema-details"><summary>Schema</summary>
                <table className="schema-table"><thead><tr><th>Column</th><th>Type</th></tr></thead><tbody>{Object.entries(dataset.schema_info).map(([col, type]) => (<tr key={col}><td>{col}</td><td>{type}</td></tr>))}</tbody></table>
              </details>
            </div>
          )}
          {chatResult && (<>
            <div className="sql-box"><h3>SQL</h3><pre><code>{chatResult.sql}</code></pre></div>
            {chatResult.columns.length > 0 && (
              <div className="table-box"><h3>Results ({chatResult.rows.length} rows)</h3><div className="table-wrapper"><table><thead><tr>{chatResult.columns.map((col) => <th key={col}>{col}</th>)}</tr></thead><tbody>{chatResult.rows.map((row, i) => (<tr key={i}>{row.map((cell, j) => <td key={j}>{String(cell)}</td>)}</tr>))}</tbody></table></div></div>
            )}
          </>)}
          {!chatResult && <div className="empty-state"><p>Ask a question to see SQL and results here.</p></div>}
        </div>
      </div>

      <div className={`slide-panel right ${settingsOpen ? 'open' : ''}`}>
        <div className="slide-header">
          <h2>Data Source</h2>
          <button className="slide-close" onClick={() => setSettingsOpen(false)}><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg></button>
        </div>
        <div className="slide-body">
          <div className="source-tabs">
            <button className={`source-tab ${activeTab === 'upload' ? 'active' : ''}`} onClick={() => setActiveTab('upload')}><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/></svg>File</button>
            <button className={`source-tab ${activeTab === 'url' ? 'active' : ''}`} onClick={() => setActiveTab('url')}><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>API</button>
            <button className={`source-tab ${activeTab === 'db' ? 'active' : ''}`} onClick={() => setActiveTab('db')}><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4.03 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5"/></svg>DB</button>
            <button className={`source-tab ${activeTab === 'kaggle' ? 'active' : ''}`} onClick={() => setActiveTab('kaggle')}><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg>Kaggle</button>
          </div>

          {error && <div className="error-msg">{error}</div>}

          {activeTab === 'upload' && (
            <div className={`drop-zone ${dragActive ? 'drag-active' : ''}`} onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop} onClick={() => fileInputRef.current?.click()}>
              <input ref={fileInputRef} type="file" accept=".csv,.xlsx,.xls" onChange={(e) => { const f = e.target.files?.[0]; if (f) processFile(f) }} hidden />
              {uploading ? (<div className="drop-zone-loading"><div className="drop-spinner" /><span>Processing...</span></div>) : (<><div className="drop-icon"><svg viewBox="0 0 48 48" width="40" height="40" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="6" y="10" width="36" height="28" rx="3"/><path d="M6 18h36"/><path d="M24 26v8M20 30l4-4 4 4"/></svg></div><span className="drop-title">Drop your file here</span><span className="drop-sub">or click to browse</span><span className="drop-formats">CSV, XLSX, XLS</span></>)}
            </div>
          )}

          {activeTab === 'url' && (
            <div className="url-connect-panel">
              <div className="url-input-group"><label className="url-label">API Endpoint URL</label><input type="url" className="url-input" value={apiUrl} onChange={(e) => setApiUrl(e.target.value)} placeholder="https://api.example.com/data" onKeyDown={(e) => e.key === 'Enter' && handleConnectURL()} /></div>
              <div className="url-input-group"><label className="url-label">Name (optional)</label><input type="text" className="url-input" value={apiName} onChange={(e) => setApiName(e.target.value)} placeholder="My dataset" onKeyDown={(e) => e.key === 'Enter' && handleConnectURL()} /></div>
              <button className="url-connect-btn" onClick={handleConnectURL} disabled={!apiUrl.trim() || uploading}>{uploading ? <><div className="btn-spinner" />Connecting...</> : 'Connect to API'}</button>
              <p className="url-hint">Returns JSON array or object with <code>data</code>, <code>results</code>, or <code>items</code> key.</p>
            </div>
          )}

          {activeTab === 'db' && (
            <div className="url-connect-panel">
              <div className="url-input-group"><label className="url-label">PostgreSQL Connection String</label><input type="text" className="url-input" value={dbConnStr} onChange={(e) => setDbConnStr(e.target.value)} placeholder="postgresql://user:pass@host:5432/db" /></div>
              <div className="url-input-group"><label className="url-label">SQL Query</label><textarea className="url-input url-textarea" value={dbQuery} onChange={(e) => setDbQuery(e.target.value)} placeholder="SELECT * FROM sales" rows={3} /></div>
              <div className="url-input-group"><label className="url-label">Name (optional)</label><input type="text" className="url-input" value={dbName} onChange={(e) => setDbName(e.target.value)} placeholder="My dataset" onKeyDown={(e) => e.key === 'Enter' && handleConnectDB()} /></div>
              <button className="url-connect-btn" onClick={handleConnectDB} disabled={!dbConnStr.trim() || !dbQuery.trim() || uploading}>{uploading ? <><div className="btn-spinner" />Connecting...</> : 'Connect to Database'}</button>
            </div>
          )}

          {activeTab === 'kaggle' && (
            <div className="url-connect-panel">
              <div className="url-input-group"><label className="url-label">Dataset (owner/dataset-name)</label><input type="text" className="url-input" value={kaggleDataset} onChange={(e) => setKaggleDataset(e.target.value)} placeholder="karkavelrajaj/amazon-sales-dataset" /></div>
              <div className="url-input-group"><label className="url-label">File path</label><input type="text" className="url-input" value={kaggleFile} onChange={(e) => setKaggleFile(e.target.value)} placeholder="amazon.csv" onKeyDown={(e) => e.key === 'Enter' && handleConnectKaggle()} /></div>
              <div className="url-input-group"><label className="url-label">Name (optional)</label><input type="text" className="url-input" value={kaggleName} onChange={(e) => setKaggleName(e.target.value)} placeholder="My dataset" /></div>
              <button className="url-connect-btn" onClick={handleConnectKaggle} disabled={!kaggleDataset.trim() || !kaggleFile.trim() || uploading}>{uploading ? <><div className="btn-spinner" />Loading...</> : 'Load from Kaggle'}</button>
              <p className="url-hint">Find the file name on the Kaggle dataset page under the "Data" tab.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
