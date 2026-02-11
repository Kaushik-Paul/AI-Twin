'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles } from 'lucide-react';
import MarkdownMessage from './MarkdownMessage';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

const SUGGESTIONS = [
    "Tell me about your experience",
    "What tech stack do you use?",
    "What projects have you worked on?",
];

export default function Twin() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState<string>('');
    const [warmupDone, setWarmupDone] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        // Warm up the lambda
        const warmUp = async () => {
            try {
                await fetch(
                    `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/health`, {
                    headers: {
                        'x-api-key': `${process.env.NEXT_PUBLIC_HEALTH_ENDPOINT_API_KEY}`
                    }
                });
            } catch (error) {
                console.error('Warm-up failed:', error);
            } finally {
                setWarmupDone(true);
            }
        };
        warmUp();
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async (overrideInput?: string) => {
        const messageText = overrideInput ?? input;
        if (!warmupDone || !messageText.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: messageText,
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-api-key': `${process.env.NEXT_PUBLIC_CHAT_ENDPOINT_API_KEY}`
                },
                body: JSON.stringify({
                    message: userMessage.content,
                    session_id: sessionId || undefined,
                }),
            });

            if (!response.ok) throw new Error('Failed to send message');

            const data = await response.json();

            if (!sessionId) {
                setSessionId(data.session_id);
            }

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: data.response,
                timestamp: new Date(),
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            console.error('Error:', error);
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again.',
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
            // Refocus the input after message is sent
            setTimeout(() => {
                inputRef.current?.focus();
            }, 100);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey && warmupDone) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className="flex flex-col h-full" style={{ background: 'var(--bg-primary)' }}>
            {/* Header */}
            <div
                className="glass-surface px-6 py-4 flex items-center gap-3"
                style={{ borderBottom: '1px solid var(--border-subtle)' }}
            >
                <div className="relative">
                    <div
                        className="w-9 h-9 rounded-xl flex items-center justify-center"
                        style={{ background: 'var(--accent-muted)' }}
                    >
                        <Bot className="w-5 h-5" style={{ color: 'var(--accent)' }} />
                    </div>
                    {/* Status dot */}
                    <div
                        className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2"
                        style={{
                            background: 'var(--accent)',
                            borderColor: 'var(--bg-primary)',
                            boxShadow: '0 0 6px var(--accent-glow)',
                        }}
                    />
                </div>
                <div>
                    <h2
                        className="text-base font-semibold"
                        style={{ color: 'var(--text-primary)' }}
                    >
                        Kaushik Paul
                    </h2>
                    <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                        AI Digital Twin • Career Conversation
                    </p>
                </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto px-4 py-6 space-y-5 sm:px-6">
                {/* Empty State */}
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full gap-6 select-none">
                        {/* Floating icon with glow ring */}
                        <div className="relative animate-float">
                            <div
                                className="absolute inset-0 rounded-full animate-glow-ring"
                                style={{
                                    background: 'radial-gradient(circle, var(--accent-glow) 0%, transparent 70%)',
                                    transform: 'scale(2)',
                                }}
                            />
                            <div
                                className="relative w-16 h-16 rounded-2xl flex items-center justify-center"
                                style={{ background: 'var(--accent-muted)', border: '1px solid var(--user-bubble-border)' }}
                            >
                                <Sparkles className="w-8 h-8" style={{ color: 'var(--accent)' }} />
                            </div>
                        </div>

                        <div className="text-center">
                            <p className="text-lg font-medium" style={{ color: 'var(--text-primary)' }}>
                                Hello! I&apos;m Kaushik&apos;s Digital Twin
                            </p>
                            <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
                                Ask me anything about my career, projects, or tech stack
                            </p>
                        </div>

                        {/* Suggestion Chips */}
                        <div className="flex flex-wrap justify-center gap-2 max-w-md">
                            {SUGGESTIONS.map((s) => (
                                <button
                                    key={s}
                                    className="suggestion-chip px-3.5 py-2 rounded-full text-sm"
                                    style={{ color: 'var(--text-secondary)' }}
                                    onClick={() => sendMessage(s)}
                                    disabled={!warmupDone || isLoading}
                                >
                                    {s}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* Message Bubbles */}
                {messages.map((message) => (
                    <div
                        key={message.id}
                        className={`flex gap-3 animate-fade-in-up ${message.role === 'user' ? 'justify-end' : 'justify-start'
                            }`}
                    >
                        {/* Bot avatar */}
                        {message.role === 'assistant' && (
                            <div className="flex-shrink-0 pt-1">
                                <div
                                    className="w-8 h-8 rounded-lg flex items-center justify-center"
                                    style={{ background: 'var(--accent-muted)' }}
                                >
                                    <Bot className="w-4 h-4" style={{ color: 'var(--accent)' }} />
                                </div>
                            </div>
                        )}

                        <div
                            className={`max-w-[75%] rounded-2xl px-4 py-3 ${message.role === 'user' ? 'message-user' : 'message-bot'
                                }`}
                        >
                            {message.role === 'assistant' ? (
                                <div className="prose-chat">
                                    <MarkdownMessage content={message.content} />
                                </div>
                            ) : (
                                <p
                                    className="whitespace-pre-wrap text-[0.9375rem] leading-relaxed"
                                    style={{ color: 'var(--text-primary)' }}
                                >
                                    {message.content}
                                </p>
                            )}
                            <p
                                className="text-[0.6875rem] mt-2 opacity-50"
                                style={{ color: message.role === 'user' ? 'var(--accent)' : 'var(--text-muted)' }}
                            >
                                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </p>
                        </div>

                        {/* User avatar */}
                        {message.role === 'user' && (
                            <div className="flex-shrink-0 pt-1">
                                <div
                                    className="w-8 h-8 rounded-lg flex items-center justify-center"
                                    style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border-default)' }}
                                >
                                    <User className="w-4 h-4" style={{ color: 'var(--text-secondary)' }} />
                                </div>
                            </div>
                        )}
                    </div>
                ))}

                {/* Typing Indicator */}
                {isLoading && (
                    <div className="flex gap-3 justify-start animate-fade-in-up">
                        <div className="flex-shrink-0 pt-1">
                            <div
                                className="w-8 h-8 rounded-lg flex items-center justify-center"
                                style={{ background: 'var(--accent-muted)' }}
                            >
                                <Bot className="w-4 h-4" style={{ color: 'var(--accent)' }} />
                            </div>
                        </div>
                        <div className="message-bot rounded-2xl px-5 py-4">
                            <div className="flex space-x-1.5">
                                <div
                                    className="w-2 h-2 rounded-full typing-dot"
                                    style={{ background: 'var(--accent)' }}
                                />
                                <div
                                    className="w-2 h-2 rounded-full typing-dot"
                                    style={{ background: 'var(--accent)' }}
                                />
                                <div
                                    className="w-2 h-2 rounded-full typing-dot"
                                    style={{ background: 'var(--accent)' }}
                                />
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input Bar */}
            <div
                className="px-4 py-4 sm:px-6"
                style={{ borderTop: '1px solid var(--border-subtle)' }}
            >
                <div
                    className="flex gap-3 items-center max-w-4xl mx-auto rounded-2xl px-4 py-2"
                    style={{
                        background: 'var(--input-wrapper-bg)',
                        border: '1px solid var(--border-default)',
                    }}
                >
                    <input
                        ref={inputRef}
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyPress}
                        placeholder={warmupDone ? "Ask me anything..." : "Warming up, please wait..."}
                        className="flex-1 bg-transparent outline-none text-[0.9375rem] placeholder:opacity-40"
                        style={{ color: 'var(--text-primary)' }}
                        disabled={isLoading}
                        autoFocus
                    />
                    <button
                        onClick={() => sendMessage()}
                        disabled={!warmupDone || !input.trim() || isLoading}
                        title={!warmupDone ? 'Please wait few seconds, chat warming up' : undefined}
                        className="send-btn w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
                    >
                        <Send className="w-4 h-4 text-white" />
                    </button>
                </div>
            </div>
        </div>
    );
}