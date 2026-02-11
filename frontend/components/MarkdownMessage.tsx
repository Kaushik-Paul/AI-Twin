'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { HTMLAttributes } from 'react';

interface MarkdownMessageProps {
    content: string;
}

type MarkdownCodeProps = HTMLAttributes<HTMLElement> & {
    inline?: boolean;
};

export default function MarkdownMessage({ content }: MarkdownMessageProps) {
    return (
        <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
                code({ inline, className, children, ...rest }: MarkdownCodeProps) {
                    if (inline) {
                        return (
                            <code
                                className="px-1.5 py-0.5 rounded-md text-sm font-[family-name:var(--font-mono)]"
                                style={{
                                    background: 'var(--code-inline-bg)',
                                    color: 'var(--accent-hover)',
                                    border: '1px solid var(--code-inline-border)',
                                }}
                                {...rest}
                            >
                                {children}
                            </code>
                        );
                    }
                    return (
                        <div className="rounded-lg overflow-hidden my-2" style={{ border: '1px solid var(--border-subtle)' }}>
                            <div
                                className="h-0.5"
                                style={{ background: 'linear-gradient(90deg, var(--accent), transparent)' }}
                            />
                            <pre
                                className="p-4 overflow-x-auto text-sm font-[family-name:var(--font-mono)]"
                                style={{ background: 'var(--code-block-bg)', color: 'var(--code-block-text)' }}
                            >
                                <code className={className} {...rest}>
                                    {children}
                                </code>
                            </pre>
                        </div>
                    );
                },
            }}
        >
            {content}
        </ReactMarkdown>
    );
}
