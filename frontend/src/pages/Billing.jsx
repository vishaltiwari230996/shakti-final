import React, { useState } from 'react';
import { CreditCard, Check, Zap, TrendingUp, Crown, Building2, Download, Calendar } from 'lucide-react';

const Billing = () => {
    const [currentPlan] = useState('starter'); // This will come from backend later

    const plans = [
        {
            id: 'starter',
            name: 'Starter',
            price: 0,
            skuLimit: 10,
            icon: Zap,
            color: 'bg-gray-500',
            features: [
                '10 SKU optimizations per month',
                'Basic SEO recommendations',
                'Email support',
                'Standard processing speed'
            ]
        },
        {
            id: 'plus',
            name: 'Plus',
            price: 999,
            skuLimit: 100,
            icon: TrendingUp,
            color: 'bg-blue-500',
            popular: true,
            features: [
                '100 SKU optimizations per month',
                'Advanced SEO analysis',
                'Priority email support',
                'Fast processing speed',
                'Keyword database access',
                'SKU grouping features'
            ]
        },
        {
            id: 'pro',
            name: 'Pro',
            price: 1999,
            skuLimit: 300,
            icon: Crown,
            color: 'bg-purple-500',
            features: [
                '300 SKU optimizations per month',
                'Premium SEO intelligence',
                'Priority support (24-48hr)',
                'Fastest processing speed',
                'Advanced keyword database',
                'Unlimited SKU groups',
                'Competitor analysis',
                'Custom reports'
            ]
        },
        {
            id: 'enterprise',
            name: 'Enterprise',
            price: 4999,
            skuLimit: -1, // Unlimited
            icon: Building2,
            color: 'bg-gradient-to-r from-orange-500 to-pink-500',
            features: [
                'Unlimited SKU optimizations',
                'Enterprise SEO suite',
                'Dedicated account manager',
                'Custom integrations',
                'API access',
                'White-label options',
                'Team collaboration tools',
                'Advanced analytics',
                'Multi-client management'
            ]
        }
    ];

    const mockInvoices = [
        { id: 'INV-2026-001', date: '2026-01-01', amount: 999, status: 'paid', plan: 'Plus' },
        { id: 'INV-2025-012', date: '2025-12-01', amount: 999, status: 'paid', plan: 'Plus' },
        { id: 'INV-2025-011', date: '2025-11-01', amount: 999, status: 'paid', plan: 'Plus' }
    ];

    const currentPlanData = plans.find(p => p.id === currentPlan);
    const currentUsage = 3; // This will come from backend
    const usagePercentage = currentPlanData.skuLimit > 0 
        ? (currentUsage / currentPlanData.skuLimit) * 100 
        : 0;

    return (
        <div className="max-w-7xl mx-auto space-y-8">
            {/* Current Plan Status */}
            <div className="card bg-gradient-blue text-white">
                <div className="flex items-start justify-between mb-6">
                    <div>
                        <h2 className="text-2xl font-semibold mb-2">Your Current Plan</h2>
                        <p className="text-white/80 text-sm">Manage your subscription and billing</p>
                    </div>
                    <div className="px-4 py-2 bg-white/20 rounded-lg backdrop-blur-sm">
                        <p className="text-xs opacity-80">Next billing</p>
                        <p className="text-sm font-semibold">Feb 1, 2026</p>
                    </div>
                </div>

                <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
                    <div className="flex items-center justify-between mb-4">
                        <div>
                            <h3 className="text-2xl font-bold">{currentPlanData.name}</h3>
                            <p className="text-white/80 text-sm">
                                {currentPlanData.price === 0 ? 'Free' : `₹${currentPlanData.price.toLocaleString()}/month`}
                            </p>
                        </div>
                        {currentPlanData.skuLimit > 0 && (
                            <div className="text-right">
                                <p className="text-3xl font-bold">{currentUsage}</p>
                                <p className="text-white/80 text-sm">of {currentPlanData.skuLimit} SKUs used</p>
                            </div>
                        )}
                    </div>

                    {currentPlanData.skuLimit > 0 && (
                        <div className="mt-4">
                            <div className="h-3 bg-white/20 rounded-full overflow-hidden">
                                <div 
                                    className="h-full bg-white rounded-full transition-all duration-300"
                                    style={{ width: `${usagePercentage}%` }}
                                />
                            </div>
                            <p className="text-xs text-white/70 mt-2">
                                {currentPlanData.skuLimit - currentUsage} SKUs remaining this month
                            </p>
                        </div>
                    )}
                </div>
            </div>

            {/* Plans Comparison */}
            <div>
                <h2 className="text-2xl font-semibold text-[var(--text-primary)] mb-4">
                    Subscription Plans
                </h2>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {plans.map((plan) => {
                        const Icon = plan.icon;
                        const isCurrentPlan = plan.id === currentPlan;

                        return (
                            <div
                                key={plan.id}
                                className={`card relative overflow-hidden transition-all duration-300 hover:shadow-xl ${
                                    isCurrentPlan ? 'ring-2 ring-[var(--accent)]' : ''
                                } ${plan.popular ? 'lg:scale-105 lg:z-10' : ''}`}
                            >
                                {plan.popular && (
                                    <div className="absolute top-0 right-0 bg-[var(--accent)] text-white text-xs px-3 py-1 rounded-bl-lg font-semibold">
                                        POPULAR
                                    </div>
                                )}

                                {isCurrentPlan && (
                                    <div className="absolute top-0 left-0 bg-green-500 text-white text-xs px-3 py-1 rounded-br-lg font-semibold">
                                        CURRENT
                                    </div>
                                )}

                                <div className={`w-12 h-12 ${plan.color} rounded-xl flex items-center justify-center text-white mb-4`}>
                                    <Icon size={24} />
                                </div>

                                <h3 className="text-xl font-bold text-[var(--text-primary)] mb-2">
                                    {plan.name}
                                </h3>

                                <div className="mb-6">
                                    <span className="text-3xl font-bold text-[var(--text-primary)]">
                                        ₹{plan.price.toLocaleString()}
                                    </span>
                                    <span className="text-[var(--text-secondary)] text-sm">/month</span>
                                </div>

                                <div className="mb-6">
                                    <p className="text-sm font-semibold text-[var(--text-secondary)] mb-4">
                                        {plan.skuLimit === -1 ? '∞ Unlimited SKUs' : `${plan.skuLimit} SKUs/month`}
                                    </p>
                                    <ul className="space-y-3">
                                        {plan.features.map((feature, idx) => (
                                            <li key={idx} className="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
                                                <Check size={16} className="text-green-500 mt-0.5 flex-shrink-0" />
                                                <span>{feature}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>

                                <button
                                    disabled={isCurrentPlan}
                                    className={`w-full btn ${
                                        isCurrentPlan
                                            ? 'bg-[var(--bg-element)] text-[var(--text-secondary)] cursor-not-allowed'
                                            : plan.popular
                                            ? 'btn-primary'
                                            : 'bg-[var(--bg-element)] text-[var(--text-primary)] hover:bg-[var(--border-medium)]'
                                    }`}
                                >
                                    {isCurrentPlan ? 'Current Plan' : plan.price === 0 ? 'Downgrade' : 'Upgrade'}
                                </button>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Billing History */}
            <div className="card">
                <div className="flex items-center gap-3 mb-6 pb-4 border-b border-[var(--border-subtle)]">
                    <div className="p-2 rounded-lg bg-[var(--bg-element)] text-[var(--text-primary)]">
                        <Calendar size={20} />
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold text-[var(--text-primary)]">Billing History</h3>
                        <p className="text-sm text-[var(--text-secondary)]">View and download your invoices</p>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-[var(--border-subtle)]">
                                <th className="text-left py-3 px-4 text-sm font-medium text-[var(--text-secondary)]">
                                    Invoice
                                </th>
                                <th className="text-left py-3 px-4 text-sm font-medium text-[var(--text-secondary)]">
                                    Date
                                </th>
                                <th className="text-left py-3 px-4 text-sm font-medium text-[var(--text-secondary)]">
                                    Plan
                                </th>
                                <th className="text-left py-3 px-4 text-sm font-medium text-[var(--text-secondary)]">
                                    Amount
                                </th>
                                <th className="text-left py-3 px-4 text-sm font-medium text-[var(--text-secondary)]">
                                    Status
                                </th>
                                <th className="text-right py-3 px-4 text-sm font-medium text-[var(--text-secondary)]">
                                    Action
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {mockInvoices.map((invoice) => (
                                <tr key={invoice.id} className="border-b border-[var(--border-subtle)] hover:bg-[var(--bg-element)] transition-colors">
                                    <td className="py-4 px-4">
                                        <span className="text-sm font-medium text-[var(--text-primary)] font-mono">
                                            {invoice.id}
                                        </span>
                                    </td>
                                    <td className="py-4 px-4">
                                        <span className="text-sm text-[var(--text-secondary)]">
                                            {new Date(invoice.date).toLocaleDateString('en-IN', { 
                                                year: 'numeric', 
                                                month: 'short', 
                                                day: 'numeric' 
                                            })}
                                        </span>
                                    </td>
                                    <td className="py-4 px-4">
                                        <span className="text-sm text-[var(--text-secondary)]">
                                            {invoice.plan}
                                        </span>
                                    </td>
                                    <td className="py-4 px-4">
                                        <span className="text-sm font-semibold text-[var(--text-primary)]">
                                            ₹{invoice.amount.toLocaleString()}
                                        </span>
                                    </td>
                                    <td className="py-4 px-4">
                                        <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300">
                                            {invoice.status}
                                        </span>
                                    </td>
                                    <td className="py-4 px-4 text-right">
                                        <button className="inline-flex items-center gap-2 text-sm text-[var(--accent)] hover:text-[var(--accent-hover)] transition-colors">
                                            <Download size={14} />
                                            Download
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Payment Method (Placeholder) */}
            <div className="card">
                <div className="flex items-center gap-3 mb-6 pb-4 border-b border-[var(--border-subtle)]">
                    <div className="p-2 rounded-lg bg-[var(--bg-element)] text-[var(--text-primary)]">
                        <CreditCard size={20} />
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold text-[var(--text-primary)]">Payment Method</h3>
                        <p className="text-sm text-[var(--text-secondary)]">Manage your payment information</p>
                    </div>
                </div>

                <div className="text-center py-8">
                    <p className="text-[var(--text-secondary)] mb-4">No payment method on file</p>
                    <button className="btn bg-[var(--bg-element)] text-[var(--text-primary)] hover:bg-[var(--border-medium)]">
                        Add Payment Method
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Billing;
