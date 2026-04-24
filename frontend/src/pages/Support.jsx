import React, { useState } from 'react';
import axios from 'axios';
import { HelpCircle, Send, CheckCircle, AlertCircle } from 'lucide-react';

const Support = () => {
    const [formData, setFormData] = useState({
        issueType: '',
        subject: '',
        description: '',
        email: ''
    });
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState(null); // 'success' | 'error' | null

    const issueTypes = [
        { value: 'bug', label: 'Bug Report' },
        { value: 'feature', label: 'Feature Request' },
        { value: 'billing', label: 'Billing Issue' },
        { value: 'technical', label: 'Technical Support' },
        { value: 'other', label: 'Other' }
    ];

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!formData.issueType || !formData.subject || !formData.description) {
            setStatus('error');
            setTimeout(() => setStatus(null), 3000);
            return;
        }

        setLoading(true);
        setStatus(null);

        try {
            // For now, just simulate sending (will add backend endpoint later)
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // TODO: Replace with actual API call
            // await axios.post('/api/support/ticket', formData);
            
            setStatus('success');
            setFormData({ issueType: '', subject: '', description: '', email: '' });
            setTimeout(() => setStatus(null), 5000);
        } catch (err) {
            console.error('Error submitting support ticket:', err);
            setStatus('error');
            setTimeout(() => setStatus(null), 5000);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-3xl mx-auto">
            <div className="card">
                {/* Header */}
                <div className="flex items-center gap-3 mb-6 pb-6 border-b border-[var(--border-subtle)]">
                    <div className="w-10 h-10 rounded-lg bg-[var(--accent)] flex items-center justify-center text-white">
                        <HelpCircle size={20} />
                    </div>
                    <div>
                        <h2 className="text-xl font-semibold text-[var(--text-primary)]">Customer Support</h2>
                        <p className="text-sm text-[var(--text-secondary)]">
                            Get help with issues, request features, or ask questions
                        </p>
                    </div>
                </div>

                {/* Status Messages */}
                {status === 'success' && (
                    <div className="mb-6 p-4 rounded-xl bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 flex items-center gap-3 animate-fade-in">
                        <CheckCircle size={20} className="text-green-600 dark:text-green-400" />
                        <div>
                            <p className="text-sm font-medium text-green-800 dark:text-green-200">
                                Support ticket submitted successfully!
                            </p>
                            <p className="text-xs text-green-700 dark:text-green-300 mt-1">
                                We'll get back to you within 24-48 hours.
                            </p>
                        </div>
                    </div>
                )}

                {status === 'error' && (
                    <div className="mb-6 p-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 flex items-center gap-3 animate-fade-in">
                        <AlertCircle size={20} className="text-red-600 dark:text-red-400" />
                        <p className="text-sm font-medium text-red-800 dark:text-red-200">
                            Please fill in all required fields
                        </p>
                    </div>
                )}

                {/* Support Form */}
                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Issue Type */}
                    <div className="input-group">
                        <label className="label">
                            Issue Type <span className="text-red-500">*</span>
                        </label>
                        <select
                            name="issueType"
                            value={formData.issueType}
                            onChange={handleChange}
                            className="select"
                            required
                        >
                            <option value="">Select an issue type</option>
                            {issueTypes.map(type => (
                                <option key={type.value} value={type.value}>
                                    {type.label}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Email */}
                    <div className="input-group">
                        <label className="label">
                            Your Email <span className="text-red-500">*</span>
                        </label>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            className="input"
                            placeholder="your.email@example.com"
                            required
                        />
                        <p className="text-xs text-[var(--text-secondary)] mt-1">
                            We'll use this to respond to your inquiry
                        </p>
                    </div>

                    {/* Subject */}
                    <div className="input-group">
                        <label className="label">
                            Subject <span className="text-red-500">*</span>
                        </label>
                        <input
                            type="text"
                            name="subject"
                            value={formData.subject}
                            onChange={handleChange}
                            className="input"
                            placeholder="Brief summary of your issue"
                            required
                        />
                    </div>

                    {/* Description */}
                    <div className="input-group">
                        <label className="label">
                            Description <span className="text-red-500">*</span>
                        </label>
                        <textarea
                            name="description"
                            value={formData.description}
                            onChange={handleChange}
                            className="input min-h-[200px] resize-y"
                            placeholder="Please provide as much detail as possible about your issue or request..."
                            required
                        />
                        <p className="text-xs text-[var(--text-secondary)] mt-1">
                            Include any error messages, steps to reproduce, or specific requirements
                        </p>
                    </div>

                    {/* Submit Button */}
                    <button
                        type="submit"
                        disabled={loading}
                        className="btn btn-primary w-full flex items-center justify-center gap-2"
                    >
                        {loading ? (
                            <>
                                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                Submitting...
                            </>
                        ) : (
                            <>
                                <Send size={16} />
                                Submit Support Ticket
                            </>
                        )}
                    </button>
                </form>

                {/* Help Text */}
                <div className="mt-8 pt-6 border-t border-[var(--border-subtle)]">
                    <h3 className="text-sm font-medium text-[var(--text-primary)] mb-3">
                        Common Questions
                    </h3>
                    <div className="space-y-2 text-sm text-[var(--text-secondary)]">
                        <p>• <strong>Response Time:</strong> We typically respond within 24-48 hours</p>
                        <p>• <strong>Billing Issues:</strong> Include your subscription plan and invoice details</p>
                        <p>• <strong>Technical Problems:</strong> Describe the steps that led to the issue</p>
                        <p>• <strong>Feature Requests:</strong> Explain the use case and expected benefit</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Support;
