import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
    Play, Download, Link as LinkIcon, Loader2, Check, FileText,
    Sparkles, Wand2, Zap, AlertCircle, CircleDot
} from 'lucide-react';
import { DEFAULT_L2_PROMPT } from '../constants/prompts';
import { useAuth } from '../contexts/AuthContext';
import { sanitizeRichHtml } from '../utils/sanitizeHtml';

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

const SingleOptimize = ({ config }) => {
    const { token, userStats, fetchUserStats } = useAuth();
    const [inputs, setInputs] = useState({
        prev_title: '',
        prev_desc: '',
        product_link: '',
        l1_prompt: '',
        l2_prompt: DEFAULT_L2_PROMPT,
    });
    const [promptCategories, setPromptCategories] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState('');
    const [loadingCategory, setLoadingCategory] = useState(false);
    const [extractUrl, setExtractUrl] = useState('');
    const [extracting, setExtracting] = useState(false);
    const [extractedFrom, setExtractedFrom] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
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
            setInputs(prev => ({ ...prev, l1_prompt: '' }));
            return;
        }
        setSelectedCategory(categoryId);
        setLoadingCategory(true);
        setError('');
        try {
            const response = await axios.get(`/api/prompt-templates/${categoryId}`);
            setInputs(prev => ({ ...prev, l1_prompt: response.data.prompt }));
        } catch (err) {
            setError(`Failed to load prompt: ${err.response?.data?.detail || err.message}`);
        } finally {
            setLoadingCategory(false);
        }
    };

    const handleExtractFromUrl = async () => {
        if (!extractUrl.trim()) {
            setError('Please enter a URL to extract.');
            return;
        }
        setExtracting(true);
        setError('');
        setExtractedFrom('');
        try {
            const response = await axios.post('/api/extract-url', { url: extractUrl.trim() }, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.data?.success) {
                setInputs(prev => ({
                    ...prev,
                    prev_title: response.data.title || prev.prev_title,
                    prev_desc: response.data.description || prev.prev_desc,
                    product_link: extractUrl.trim(),
                }));
                setExtractedFrom(response.data.platform || 'URL');
            } else {
                setError(response.data?.error || 'Could not extract from URL.');
            }
        } catch (err) {
            setError(err.response?.data?.detail || err.message || 'URL extraction failed.');
        } finally {
            setExtracting(false);
        }
    };

    const handleChange = (field, value) => {
        setInputs(prev => ({ ...prev, [field]: value }));
    };

    const handleRun = async () => {
        if (!inputs.prev_title.trim() || !inputs.prev_desc.trim()) {
            setError('Please provide a previous title and description.');
            return;
        }
        if (!inputs.l1_prompt) {
            setError('Please select a prompt template before running.');
            return;
        }
        setLoading(true);
        setError('');
        setResult(null);
        try {
            const response = await axios.post('/api/optimize/single', {
                ...inputs,
                config,
            }, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            setResult(response.data);
            if (fetchUserStats && token) fetchUserStats(token);
        } catch (err) {
            setError(err.response?.data?.detail || err.message || 'Optimization failed.');
        } finally {
            setLoading(false);
        }
    };

    const downloadReport = () => {
        if (!result?.report_html) return;
        const blob = new Blob([result.report_html], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `single_optimize_report.html`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    const usage = userStats?.usage?.single_optimize;

    return (
        <div className="atl-page atl-page-wide">
            <Section
                icon={Wand2}
                title="Single Optimize"
                subtitle="Rewrite one product listing end to end — title, description, and keyword ladders."
            />

            <div className="atl-split">
                {/* LEFT — Inputs */}
                <div className="atl-col">
                    {usage && (
                        <section className="atl-card">
                            <div className="atl-usage">
                                <div className="atl-usage-head">
                                    <span><strong>Single Optimizations</strong></span>
                                    <span>{usage.used}/{usage.limit} used</span>
                                </div>
                                <div className="atl-usage-bar">
                                    <div
                                        className={`atl-usage-fill ${usage.used / usage.limit > 0.8 ? 'warn' : ''}`}
                                        style={{ width: `${Math.min((usage.used / usage.limit) * 100, 100)}%` }}
                                    />
                                </div>
                                <p className="atl-muted">{usage.remaining} remaining this period</p>
                            </div>
                        </section>
                    )}

                    <Section
                        icon={LinkIcon}
                        title="Quick Extract"
                        subtitle="Paste an Amazon or Flipkart URL to auto-fill the fields."
                    >
                        <div className="atl-input-row">
                            <input
                                type="url"
                                className="atl-input"
                                placeholder="https://www.amazon.in/dp/..."
                                value={extractUrl}
                                onChange={(e) => setExtractUrl(e.target.value)}
                                disabled={extracting}
                            />
                            <button
                                className="atl-btn-secondary"
                                onClick={handleExtractFromUrl}
                                disabled={extracting || !extractUrl.trim()}
                            >
                                {extracting ? (
                                    <><Loader2 size={14} className="atl-spin" /> Extracting</>
                                ) : (
                                    <><Sparkles size={14} /> Extract</>
                                )}
                            </button>
                        </div>
                        {extractedFrom && (
                            <div className="atl-alert atl-alert-success" style={{ marginTop: 10 }}>
                                <Check size={14} />
                                <span>Extracted from {extractedFrom}. Fields below were pre-filled.</span>
                            </div>
                        )}
                    </Section>

                    <Section
                        icon={FileText}
                        title="Input Details"
                        subtitle="Paste the current listing content below."
                    >
                        <div className="atl-field">
                            <label className="atl-label">Previous Title</label>
                            <input
                                type="text"
                                className="atl-input"
                                value={inputs.prev_title}
                                onChange={(e) => handleChange('prev_title', e.target.value)}
                                placeholder="Current product title..."
                            />
                        </div>
                        <div className="atl-field">
                            <label className="atl-label">Previous Description</label>
                            <textarea
                                className="atl-textarea atl-textarea-lg"
                                value={inputs.prev_desc}
                                onChange={(e) => handleChange('prev_desc', e.target.value)}
                                placeholder="Current product description..."
                                rows={6}
                            />
                        </div>
                        <div className="atl-field">
                            <label className="atl-label">Product Link <span style={{ color: 'var(--ink-4)', fontWeight: 400 }}>(optional)</span></label>
                            <input
                                type="url"
                                className="atl-input"
                                value={inputs.product_link}
                                onChange={(e) => handleChange('product_link', e.target.value)}
                                placeholder="https://..."
                            />
                        </div>
                    </Section>

                    <Section
                        icon={Sparkles}
                        title="Prompt Template"
                        subtitle="Select a server-side optimization recipe."
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
                            {loadingCategory && (
                                <p className="atl-muted-sm">Loading secure prompt…</p>
                            )}
                            {selectedCategory && !loadingCategory && (
                                <div className="atl-alert atl-alert-info" style={{ marginTop: 10 }}>
                                    <Check size={14} />
                                    <span>Template loaded. Prompts execute server-side and stay hidden from the UI.</span>
                                </div>
                            )}
                        </div>
                    </Section>

                    <button
                        className="atl-btn-primary atl-btn-primary-block"
                        onClick={handleRun}
                        disabled={loading}
                    >
                        {loading ? (
                            <><Loader2 size={15} className="atl-spin" /> Optimizing…</>
                        ) : (
                            <><Play size={15} /> Run Optimization</>
                        )}
                    </button>

                    {error && (
                        <div className="atl-alert atl-alert-error">
                            <AlertCircle size={14} />
                            <span>{error}</span>
                        </div>
                    )}
                </div>

                {/* RIGHT — Result */}
                <div className="atl-col">
                    {result?.final ? (
                        <>
                            <Section
                                icon={Zap}
                                title="Optimized Listing"
                                subtitle="Generated by the model using your selected template."
                                extra={
                                    result.report_html && (
                                        <button className="atl-btn-ghost-sm" onClick={downloadReport}>
                                            <Download size={13} /> Report
                                        </button>
                                    )
                                }
                            >
                                <div className="atl-field">
                                    <p className="atl-label-caps">New Title</p>
                                    <div className="atl-result-box">{result.final.new_title}</div>
                                </div>
                                <div className="atl-field">
                                    <p className="atl-label-caps">New Description</p>
                                    <div
                                        className="atl-result-box atl-result-box-scroll"
                                        dangerouslySetInnerHTML={{
                                            __html: sanitizeRichHtml(result.final.new_description || '')
                                        }}
                                    />
                                </div>
                            </Section>

                            <Section
                                icon={CircleDot}
                                title="Keyword Ladder"
                                subtitle="Short-, mid-, and long-tail keywords extracted for SEO."
                            >
                                {result.final.keywords_short?.length > 0 && (
                                    <div className="atl-field">
                                        <p className="atl-label-caps">Short-Tail</p>
                                        <div className="atl-chip-group">
                                            {result.final.keywords_short.map((kw, i) => (
                                                <span key={i} className="atl-chip atl-chip-accent">{kw}</span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                                {result.final.keywords_mid?.length > 0 && (
                                    <div className="atl-field">
                                        <p className="atl-label-caps">Mid-Tail</p>
                                        <div className="atl-chip-group">
                                            {result.final.keywords_mid.map((kw, i) => (
                                                <span key={i} className="atl-chip">{kw}</span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                                {result.final.keywords_long?.length > 0 && (
                                    <div className="atl-field">
                                        <p className="atl-label-caps">Long-Tail</p>
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                                            {result.final.keywords_long.map((kw, i) => (
                                                <div key={i} className="atl-result-box" style={{ padding: '8px 12px', fontSize: 12.5 }}>
                                                    {kw}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </Section>
                        </>
                    ) : (
                        <section className="atl-card">
                            <div className="atl-empty">
                                <div className="atl-empty-icon"><Play size={26} strokeWidth={1.5} /></div>
                                <h3 className="atl-empty-title">Ready when you are</h3>
                                <p className="atl-empty-desc">
                                    Fill in the previous title and description on the left, pick a prompt template,
                                    and hit <strong>Run Optimization</strong>. Your rewritten listing and keyword
                                    ladder will appear here.
                                </p>
                            </div>
                        </section>
                    )}
                </div>
            </div>
        </div>
    );
};

export default SingleOptimize;
