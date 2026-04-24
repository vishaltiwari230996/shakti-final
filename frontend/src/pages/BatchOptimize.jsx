import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Papa from 'papaparse';
import {
    Upload, Play, Download, CheckCircle, AlertCircle,
    FileSpreadsheet, Layers, Sparkles, Loader2, Check
} from 'lucide-react';
import JSZip from 'jszip';
import { saveAs } from 'file-saver';
import { DEFAULT_L2_PROMPT } from '../constants/prompts';
import { useAuth } from '../contexts/AuthContext';

const Section = ({ icon: Icon, title, subtitle, children, extra }) => (
    <section className="atl-card">
        <div className="atl-section-head">
            <div className="atl-section-icon"><Icon size={16} strokeWidth={1.8} /></div>
            <div style={{ flex: 1, minWidth: 0 }}>
                <h3 className="atl-section-title">{title}</h3>
                {subtitle && <p className="atl-section-sub">{subtitle}</p>}
            </div>
            {extra}
        </div>
        {children}
    </section>
);

const BatchOptimize = ({ config }) => {
    const { token } = useAuth();
    const [file, setFile] = useState(null);
    const [parsedData, setParsedData] = useState([]);
    const [l1Prompt, setL1Prompt] = useState('');
    const [l2Prompt] = useState(DEFAULT_L2_PROMPT);
    const [promptCategories, setPromptCategories] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState('');
    const [loadingCategory, setLoadingCategory] = useState(false);
    const [processing, setProcessing] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchCategories = async () => {
            try {
                const response = await axios.get('/api/prompt-templates');
                setPromptCategories(response.data.categories || []);
            } catch (err) {
                console.error('Failed to load prompt categories:', err);
            }
        };
        fetchCategories();
    }, []);

    const handleCategoryChange = async (categoryId) => {
        if (!categoryId) {
            setSelectedCategory('');
            setL1Prompt('');
            return;
        }
        setSelectedCategory(categoryId);
        setLoadingCategory(true);
        setError('');
        try {
            const response = await axios.get(`/api/prompt-templates/${categoryId}`);
            setL1Prompt(response.data.prompt);
        } catch (err) {
            setError(`Failed to load prompt: ${err.response?.data?.detail || err.message}`);
        } finally {
            setLoadingCategory(false);
        }
    };

    const handleFileChange = (e) => {
        const f = e.target.files[0];
        if (!f) return;
        setFile(f);
        Papa.parse(f, {
            header: true,
            skipEmptyLines: true,
            complete: (res) => {
                const fields = (res.meta.fields || []).map(f => f.toLowerCase().trim());
                const hasTitle = fields.some(f => f.includes('title'));
                const hasDesc = fields.some(f => f.includes('description'));
                if (!hasTitle || !hasDesc) {
                    setError('CSV must contain "Previous Title" and "Previous Description" columns.');
                    setParsedData([]);
                    return;
                }
                setError('');
                const normalized = res.data.slice(0, 10).map((row, idx) => {
                    const keys = Object.keys(row);
                    const titleKey = keys.find(k => k.toLowerCase().includes('title'));
                    const descKey = keys.find(k => k.toLowerCase().includes('description'));
                    const linkKey = keys.find(k => ['link', 'url'].some(x => k.toLowerCase().includes(x)));
                    return {
                        row_id: idx + 1,
                        prev_title: row[titleKey] || '',
                        prev_desc: row[descKey] || '',
                        product_link: linkKey ? row[linkKey] : ''
                    };
                });
                setParsedData(normalized);
            }
        });
    };

    const handleRun = async () => {
        if (!l1Prompt) {
            setError('Please select a prompt template before running a batch.');
            return;
        }
        if (parsedData.length === 0) {
            setError('Please upload a valid CSV.');
            return;
        }
        setProcessing(true);
        setError('');
        setResults(null);
        try {
            const response = await axios.post('/api/optimize/batch', {
                rows: parsedData,
                l1_prompt: l1Prompt,
                l2_prompt: l2Prompt,
                config
            }, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            setResults(response.data.results);
        } catch (err) {
            setError(err.response?.data?.detail || 'An error occurred during batch processing');
        } finally {
            setProcessing(false);
        }
    };

    const downloadZip = async () => {
        if (!results) return;
        const zip = new JSZip();
        results.forEach(res => {
            if (res.status === 'success') {
                zip.file(`report_${res.row_id}.html`, res.report_html);
            }
        });
        const content = await zip.generateAsync({ type: 'blob' });
        saveAs(content, 'shakti_batch_reports.zip');
    };

    const downloadCsv = () => {
        if (!results) return;
        const csvData = results.map(r => ({
            Row: r.row_id,
            Status: r.status,
            NewTitle: r.final?.new_title || '',
            NewDescription: r.final?.new_description || '',
            ShortTail: r.final?.keywords_short?.join(', ') || '',
            MidTail: r.final?.keywords_mid?.join(', ') || '',
            LongTail: r.final?.keywords_long?.join(', ') || '',
            Error: r.error || ''
        }));
        const csv = Papa.unparse(csvData);
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        saveAs(blob, 'shakti_batch_results.csv');
    };

    return (
        <div className="atl-page atl-page-narrow">
            <Section
                icon={Layers}
                title="Batch Optimize"
                subtitle="Upload a CSV and rewrite up to 10 product listings in a single run."
                extra={<span className="atl-chip">Max 10 rows</span>}
            />

            <Section
                icon={Upload}
                title="Upload CSV"
                subtitle="Requires columns containing 'Previous Title' and 'Previous Description'."
            >
                <div className="atl-dropzone">
                    <div className="atl-dropzone-icon"><Upload size={20} strokeWidth={1.8} /></div>
                    <p className="atl-dropzone-title">Drop or select a CSV</p>
                    <p className="atl-dropzone-sub">Optional 'Link'/'URL' column will be preserved per row.</p>
                    <input
                        type="file"
                        accept=".csv"
                        onChange={handleFileChange}
                        className="atl-hidden-input"
                        id="csv-upload"
                        style={{ display: 'none' }}
                    />
                    <label htmlFor="csv-upload" className="atl-btn-secondary" style={{ cursor: 'pointer' }}>
                        Select File
                    </label>
                    {file && <div className="atl-dropzone-filename">{file.name}</div>}
                </div>

                {parsedData.length > 0 && (
                    <div className="atl-alert atl-alert-success" style={{ marginTop: 14 }}>
                        <CheckCircle size={14} />
                        <span>Successfully loaded {parsedData.length} row{parsedData.length !== 1 ? 's' : ''}.</span>
                    </div>
                )}
            </Section>

            <Section
                icon={Sparkles}
                title="Prompt Template"
                subtitle="Prompts execute server-side and stay hidden from the UI."
            >
                <div className="atl-field">
                    <label className="atl-label">Category</label>
                    <select
                        className="atl-select"
                        value={selectedCategory}
                        onChange={(e) => handleCategoryChange(e.target.value)}
                        disabled={loadingCategory}
                    >
                        <option value="">— Choose an optimization template —</option>
                        {promptCategories.map(cat => (
                            <option key={cat.id} value={cat.id} disabled={!cat.available}>
                                {cat.name}{!cat.available ? ' (Not available)' : ''}
                            </option>
                        ))}
                    </select>
                    {loadingCategory && <p className="atl-muted-sm">Loading secure prompt…</p>}
                </div>
                {selectedCategory && !loadingCategory && (
                    <div className="atl-alert atl-alert-info">
                        <Check size={14} />
                        <span>Template loaded. L1 + L2 prompts are encrypted on the server.</span>
                    </div>
                )}
            </Section>

            <button
                onClick={handleRun}
                disabled={processing || parsedData.length === 0}
                className="atl-btn-primary atl-btn-primary-block"
            >
                {processing ? (
                    <><Loader2 size={15} className="atl-spin" /> Processing batch…</>
                ) : (
                    <><Play size={15} /> Start Batch Processing</>
                )}
            </button>

            {error && (
                <div className="atl-alert atl-alert-error">
                    <AlertCircle size={14} />
                    <span>{error}</span>
                </div>
            )}

            {results && (
                <Section
                    icon={FileSpreadsheet}
                    title="Processing Results"
                    subtitle={`${results.length} row${results.length !== 1 ? 's' : ''} processed.`}
                    extra={
                        <div style={{ display: 'flex', gap: 8 }}>
                            <button className="atl-btn-ghost-sm" onClick={downloadCsv}>
                                <FileSpreadsheet size={13} /> CSV
                            </button>
                            <button className="atl-btn-ghost-sm" onClick={downloadZip}>
                                <Download size={13} /> ZIP
                            </button>
                        </div>
                    }
                >
                    <div className="atl-table-wrap">
                        <table className="atl-table">
                            <thead>
                                <tr>
                                    <th>Row</th>
                                    <th>Status</th>
                                    <th>New Title</th>
                                    <th style={{ textAlign: 'right' }}>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {results.map((res) => (
                                    <tr key={res.row_id}>
                                        <td className="atl-table-row-id">#{res.row_id}</td>
                                        <td>
                                            {res.status === 'success' ? (
                                                <span className="atl-chip atl-chip-success">Success</span>
                                            ) : (
                                                <span className="atl-chip atl-chip-warn">Error</span>
                                            )}
                                        </td>
                                        <td style={{ maxWidth: 280, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                            {res.final?.new_title || (
                                                <span style={{ color: 'var(--ink-4)', fontStyle: 'italic' }}>{res.error}</span>
                                            )}
                                        </td>
                                        <td style={{ textAlign: 'right' }}>
                                            {res.status === 'success' && (
                                                <button
                                                    className="atl-link-btn"
                                                    onClick={() => {
                                                        const blob = new Blob([res.report_html], { type: 'text/html' });
                                                        saveAs(blob, `report_${res.row_id}.html`);
                                                    }}
                                                >
                                                    View report
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </Section>
            )}
        </div>
    );
};

export default BatchOptimize;
