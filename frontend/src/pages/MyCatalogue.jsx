import React, { useEffect, useRef, useState } from 'react'
import { Upload, Download, FileSpreadsheet, Trash2, Hash, Package, ExternalLink, Sparkles, Loader2 } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { buildApiUrl } from '../utils/apiConfig'
import './TestUI.css'
import './MyCatalogue.css'

function authHeaders(token, extra = {}) {
  return { Authorization: `Bearer ${token}`, ...extra }
}

export default function MyCatalogue() {
  const { user, token } = useAuth()
  const [catalogue, setCatalogue] = useState(null)
  const [products, setProducts] = useState([])
  const [keywords, setKeywords] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [uploadResult, setUploadResult] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const fileInputRef = useRef(null)

  const [kwDraft, setKwDraft] = useState({ short_tail: '', mid_tail: '', long_tail: '', brand_keywords: '' })
  const [savingKw, setSavingKw] = useState(false)
  const [enrichingAll, setEnrichingAll] = useState(false)
  const [enrichingIds, setEnrichingIds] = useState(new Set())
  const [enrichBanner, setEnrichBanner] = useState(null)

  const load = async () => {
    setLoading(true); setError(null)
    try {
      const [c, p, k] = await Promise.all([
        fetch(buildApiUrl('/api/my/catalogue'), { headers: authHeaders(token) }).then((r) => r.json()),
        fetch(buildApiUrl('/api/my/products'), { headers: authHeaders(token) }).then((r) => r.json()),
        fetch(buildApiUrl('/api/my/keywords'), { headers: authHeaders(token) }).then((r) => r.json()),
      ])
      setCatalogue(c); setProducts(p); setKeywords(k)
      setKwDraft({
        short_tail: (k.short_tail || []).join(', '),
        mid_tail: (k.mid_tail || []).join(', '),
        long_tail: (k.long_tail || []).join(', '),
        brand_keywords: (k.brand_keywords || []).join(', '),
      })
    } catch (err) {
      setError('Failed to load catalogue')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { if (token) load() }, [token])

  const uploadCsv = async (file) => {
    if (!file) return
    setUploading(true); setError(null); setUploadResult(null)
    try {
      const fd = new FormData()
      fd.append('file', file)
      const res = await fetch(buildApiUrl('/api/my/products/upload-csv'), {
        method: 'POST',
        headers: authHeaders(token),
        body: fd,
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data.detail || 'Upload failed')
        return
      }
      setUploadResult(data)
      await load()
    } catch (err) {
      setError('Upload failed: ' + err.message)
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const downloadTemplate = () => {
    const csv = 'product_url,product_name,brand,category\nhttps://www.amazon.in/dp/B08N5WRWNW,Echo Dot (4th Gen),Amazon,Electronics\nhttps://www.amazon.in/dp/B0BDHWDR12,Fire TV Stick 4K,Amazon,Electronics\n'
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = 'catalogue_template.csv'; a.click()
    URL.revokeObjectURL(url)
  }

  const deleteProduct = async (id) => {
    if (!confirm('Delete this product?')) return
    await fetch(buildApiUrl(`/api/my/products/${id}`), { method: 'DELETE', headers: authHeaders(token) })
    await load()
  }

  const enrichOne = async (id) => {
    setEnrichingIds((s) => new Set(s).add(id))
    try {
      const res = await fetch(buildApiUrl(`/api/my/products/${id}/enrich`), {
        method: 'POST', headers: authHeaders(token),
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data.detail || 'Enrichment failed')
        return
      }
      setProducts((prev) => prev.map((p) => (p.id === id ? data.product : p)))
    } catch (err) {
      setError('Enrichment failed: ' + err.message)
    } finally {
      setEnrichingIds((s) => {
        const n = new Set(s); n.delete(id); return n
      })
    }
  }

  const enrichAllMissing = async () => {
    if (!confirm('Scrape Amazon for all products with missing brand/category? This may take a few minutes.')) return
    setEnrichingAll(true); setError(null); setEnrichBanner(null)
    try {
      const res = await fetch(buildApiUrl('/api/my/products/enrich-missing?limit=200'), {
        method: 'POST', headers: authHeaders(token),
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data.detail || 'Enrichment failed')
        return
      }
      setEnrichBanner(
        `Enriched ${data.enriched} of ${data.total_candidates} product(s)` +
        (data.failed ? ` · ${data.failed} failed` : '')
      )
      await load()
    } catch (err) {
      setError('Enrichment failed: ' + err.message)
    } finally {
      setEnrichingAll(false)
    }
  }

  const saveKeywords = async (e) => {
    e.preventDefault(); setSavingKw(true); setError(null)
    const toList = (s) => s.split(',').map((x) => x.trim()).filter(Boolean)
    try {
      const body = {
        short_tail: toList(kwDraft.short_tail),
        mid_tail: toList(kwDraft.mid_tail),
        long_tail: toList(kwDraft.long_tail),
        brand_keywords: toList(kwDraft.brand_keywords),
      }
      const res = await fetch(buildApiUrl('/api/my/keywords'), {
        method: 'PUT',
        headers: authHeaders(token, { 'Content-Type': 'application/json' }),
        body: JSON.stringify(body),
      })
      const data = await res.json()
      if (!res.ok) { setError(data.detail || 'Failed to save keywords'); return }
      setKeywords(data)
    } finally { setSavingKw(false) }
  }

  const onDrop = (e) => {
    e.preventDefault(); setDragOver(false)
    const f = e.dataTransfer.files?.[0]
    if (f) uploadCsv(f)
  }

  if (loading) return <div className="mc-loading">Loading catalogue…</div>

  return (
    <div className="mc-page">
      {/* Header */}
      <header className="mc-header">
        <div>
          <h1 className="mc-title">My Catalogue</h1>
          <p className="mc-subtitle">
            {user?.name} · {user?.email}{catalogue ? ` · ${catalogue.name}` : ''}
          </p>
        </div>
        <div className="mc-stats">
          <div className="mc-stat">
            <span className="mc-stat-label">Products</span>
            <span className="mc-stat-value">{products.length}</span>
          </div>
          <div className="mc-stat">
            <span className="mc-stat-label">Keywords</span>
            <span className="mc-stat-value">
              {((keywords?.short_tail?.length || 0) +
                (keywords?.mid_tail?.length || 0) +
                (keywords?.long_tail?.length || 0) +
                (keywords?.brand_keywords?.length || 0))}
            </span>
          </div>
        </div>
      </header>

      {error && <div className="mc-alert mc-alert-error">{error}</div>}

      {/* Upload */}
      <section className="atl-card mc-card">
        <div className="atl-card-head">
          <div>
            <div className="atl-card-title">Upload catalogue</div>
            <div className="atl-card-sub">
              CSV with <code className="mc-code">product_url</code>, <code className="mc-code">product_name</code>.
              Optional: <code className="mc-code">brand</code>, <code className="mc-code">category</code>, <code className="mc-code">asin</code>.
              ASIN is auto-extracted from Amazon URLs.
            </div>
          </div>
          <div className="atl-card-actions">
            <button onClick={downloadTemplate} className="atl-btn-ghost-sm">
              <Download size={13} /> Template
            </button>
          </div>
        </div>

        <label
          className={`mc-dropzone ${dragOver ? 'is-drag' : ''} ${uploading ? 'is-busy' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={onDrop}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            disabled={uploading}
            onChange={(e) => uploadCsv(e.target.files?.[0])}
            className="mc-file-input"
          />
          <div className="mc-dropzone-icon">
            {uploading ? <FileSpreadsheet size={22} /> : <Upload size={22} />}
          </div>
          <div className="mc-dropzone-title">
            {uploading ? 'Uploading…' : 'Drop CSV here or click to browse'}
          </div>
          <div className="mc-dropzone-hint">Up to a few thousand rows per file</div>
        </label>

        {uploadResult && (
          <div className="mc-upload-result">
            <div className="mc-result-summary">
              Added <strong>{uploadResult.created}</strong> product{uploadResult.created === 1 ? '' : 's'}
              {uploadResult.skipped > 0 && <span className="mc-muted"> · skipped {uploadResult.skipped} duplicate{uploadResult.skipped === 1 ? '' : 's'}</span>}
            </div>
            {uploadResult.errors?.length > 0 && (
              <details className="mc-warnings">
                <summary>{uploadResult.errors.length} warning{uploadResult.errors.length === 1 ? '' : 's'}</summary>
                <ul>
                  {uploadResult.errors.slice(0, 20).map((e, i) => <li key={i}>{e}</li>)}
                </ul>
              </details>
            )}
          </div>
        )}
      </section>

      {/* Products */}
      <section className="atl-card mc-card">
        <div className="atl-card-head">
          <div>
            <div className="atl-card-title">
              <Package size={15} style={{ verticalAlign: '-2px', marginRight: 6 }} />
              Products
              <span className="mc-count-chip">{products.length}</span>
            </div>
            <div className="atl-card-sub">Your uploaded Amazon catalogue</div>
          </div>
          {products.length > 0 && (
            <div className="atl-card-actions">
              <button
                onClick={enrichAllMissing}
                disabled={enrichingAll}
                className="atl-btn-ghost-sm"
                title="Scrape Amazon to fill missing brand/category"
              >
                {enrichingAll ? <Loader2 size={13} className="mc-spin" /> : <Sparkles size={13} />}
                {enrichingAll ? 'Auto-filling…' : 'Auto-fill missing'}
              </button>
            </div>
          )}
        </div>

        {enrichBanner && (
          <div className="mc-upload-result" style={{ marginBottom: 12 }}>
            <div className="mc-result-summary">{enrichBanner}</div>
          </div>
        )}

        {products.length === 0 ? (
          <div className="mc-empty">
            <Package size={28} />
            <div className="mc-empty-title">No products yet</div>
            <div className="mc-empty-sub">Upload a CSV above to populate your catalogue</div>
          </div>
        ) : (
          <div className="atl-table-wrap mc-table-wrap">
            <table className="atl-table">
              <thead>
                <tr>
                  <th style={{ width: 130 }}>ASIN</th>
                  <th>Name</th>
                  <th style={{ width: 130 }}>Brand</th>
                  <th style={{ width: 170 }}>Category</th>
                  <th style={{ width: 60 }}>Link</th>
                  <th style={{ width: 90 }}></th>
                </tr>
              </thead>
              <tbody>
                {products.map((p) => {
                  const missing = !(p.brand || '').trim() || !(p.category || '').trim()
                  const isEnriching = enrichingIds.has(p.id)
                  return (
                    <tr key={p.id}>
                      <td><span className="atl-table-row-id">{p.asin}</span></td>
                      <td>{p.product_name}</td>
                      <td>{p.brand || <span className="mc-muted">—</span>}</td>
                      <td>{p.category || <span className="mc-muted">—</span>}</td>
                      <td>
                        {p.product_url ? (
                          <a href={p.product_url} target="_blank" rel="noreferrer" className="mc-link">
                            <ExternalLink size={13} />
                          </a>
                        ) : (<span className="mc-muted">—</span>)}
                      </td>
                      <td>
                        <div className="mc-row-actions">
                          {missing && p.product_url && (
                            <button
                              onClick={() => enrichOne(p.id)}
                              disabled={isEnriching}
                              className="atl-btn-ghost-xs"
                              title="Auto-fill brand & category from Amazon"
                            >
                              {isEnriching ? <Loader2 size={12} className="mc-spin" /> : <Sparkles size={12} />}
                            </button>
                          )}
                          <button
                            onClick={() => deleteProduct(p.id)}
                            className="atl-btn-ghost-xs mc-delete-btn"
                            title="Delete product"
                          >
                            <Trash2 size={12} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Keywords */}
      <section className="atl-card mc-card">
        <div className="atl-card-head">
          <div>
            <div className="atl-card-title">
              <Hash size={15} style={{ verticalAlign: '-2px', marginRight: 6 }} />
              Keywords
            </div>
            <div className="atl-card-sub">Comma-separated. Used across all optimizations.</div>
          </div>
        </div>

        <form onSubmit={saveKeywords} className="mc-kw-form">
          {[
            ['short_tail', 'Short tail', 'headphones, earbuds'],
            ['mid_tail', 'Mid tail', 'wireless headphones, noise cancelling earbuds'],
            ['long_tail', 'Long tail', 'best wireless anc headphones under 10000'],
            ['brand_keywords', 'Brand keywords', 'Sony, boAt, JBL'],
          ].map(([k, label, placeholder]) => (
            <div key={k} className="mc-kw-field">
              <label className="atl-label">{label}</label>
              <input
                value={kwDraft[k]}
                onChange={(e) => setKwDraft({ ...kwDraft, [k]: e.target.value })}
                className="atl-input"
                placeholder={placeholder}
              />
            </div>
          ))}
          <div className="mc-kw-actions">
            <button type="submit" disabled={savingKw} className="atl-btn-primary">
              {savingKw ? 'Saving…' : 'Save keywords'}
            </button>
          </div>
        </form>
      </section>
    </div>
  )
}
