import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, User, Bot, Sparkles } from 'lucide-react';

const Chat = ({ config }) => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const scrollRef = useRef(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim() || !config.openai_key) return;

        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const response = await axios.post('/api/chat', {
                messages: [...messages, userMsg],
                model: config.openai_model,
                api_key: config.openai_key
            });
            setMessages(prev => [...prev, response.data]);
        } catch (err) {
            setMessages(prev => [...prev, { role: 'assistant', content: 'Error: ' + (err.response?.data?.detail || err.message) }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto h-[calc(100vh-120px)] flex flex-col">
            <div className="card flex-1 flex flex-col overflow-hidden p-0 border-[var(--border-subtle)] bg-[var(--bg-panel)]">
                {/* Header */}
                <div className="px-6 py-4 border-b border-[var(--border-subtle)] flex items-center gap-3 bg-[var(--bg-element)]">
                    <div className="w-8 h-8 rounded-lg bg-[var(--accent)] flex items-center justify-center text-white">
                        <Sparkles size={16} />
                    </div>
                    <div>
                        <h2 className="text-sm font-medium text-[var(--text-primary)]">AI Assistant</h2>
                        <p className="text-xs text-[var(--text-secondary)]">Powered by {config.openai_model}</p>
                    </div>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6" ref={scrollRef}>
                    {messages.length === 0 && (
                        <div className="h-full flex flex-col items-center justify-center text-[var(--text-secondary)] opacity-60">
                            <div className="w-16 h-16 rounded-2xl bg-[var(--bg-element)] flex items-center justify-center mb-4 border border-[var(--border-subtle)]">
                                <Bot size={32} />
                            </div>
                            <p className="text-sm font-medium">How can I help you optimize today?</p>
                        </div>
                    )}

                    {messages.map((msg, i) => (
                        <div
                            key={i}
                            className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                        >
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 border ${msg.role === 'user'
                                    ? 'bg-[var(--bg-element)] border-[var(--border-subtle)] text-[var(--text-primary)]'
                                    : 'bg-[var(--accent)] border-transparent text-white'
                                }`}>
                                {msg.role === 'user' ? <User size={14} /> : <Bot size={14} />}
                            </div>
                            <div className={`max-w-[80%] space-y-1`}>
                                <div className={`text-xs ${msg.role === 'user' ? 'text-right text-[var(--text-secondary)]' : 'text-[var(--text-secondary)]'}`}>
                                    {msg.role === 'user' ? 'You' : 'Assistant'}
                                </div>
                                <div className={`p-4 rounded-2xl text-sm leading-relaxed ${msg.role === 'user'
                                        ? 'bg-[var(--bg-element)] text-[var(--text-primary)] border border-[var(--border-subtle)] rounded-tr-sm'
                                        : 'bg-transparent text-[var(--text-primary)] pl-0 pt-0'
                                    }`}>
                                    <p className="whitespace-pre-wrap">{msg.content}</p>
                                </div>
                            </div>
                        </div>
                    ))}

                    {loading && (
                        <div className="flex gap-4">
                            <div className="w-8 h-8 rounded-full bg-[var(--accent)] flex items-center justify-center flex-shrink-0">
                                <Bot size={14} className="text-white" />
                            </div>
                            <div className="space-y-1">
                                <div className="text-xs text-[var(--text-secondary)]">Assistant</div>
                                <div className="flex gap-1 pt-2">
                                    <div className="w-1.5 h-1.5 bg-[var(--text-tertiary)] rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                    <div className="w-1.5 h-1.5 bg-[var(--text-tertiary)] rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                    <div className="w-1.5 h-1.5 bg-[var(--text-tertiary)] rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Input */}
                <div className="p-4 border-t border-[var(--border-subtle)] bg-[var(--bg-panel)]">
                    <form onSubmit={handleSend} className="relative">
                        <input
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Type a message to chat with AI..."
                            className="w-full bg-[var(--bg-element)] border border-[var(--border-subtle)] rounded-xl py-4 pl-5 pr-14 text-sm text-[var(--text-primary)] focus:border-[var(--text-tertiary)] focus:ring-0 transition-colors"
                            disabled={loading}
                        />
                        <button
                            type="submit"
                            disabled={loading || !input.trim()}
                            className="absolute right-2 top-2 bottom-2 p-2 bg-[var(--text-primary)] text-[var(--bg-app)] rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
                        >
                            <Send size={16} />
                        </button>
                    </form>
                    <div className="text-center mt-2">
                        <p className="text-[10px] text-[var(--text-tertiary)]">AI can make mistakes. Review generated content.</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Chat;

