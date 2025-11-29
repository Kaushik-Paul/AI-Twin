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
                                className="px-1 py-0.5 rounded bg-slate-100 font-mono text-sm"
                                {...rest}
                            >
                                {children}
                            </code>
                        );
                    }
                    return (
                        <pre className="bg-slate-900 text-slate-100 p-3 rounded-md overflow-x-auto text-sm">
                            <code className={className} {...rest}>
                                {children}
                            </code>
                        </pre>
                    );
                },
            }}
        >
            {content}
        </ReactMarkdown>
    );
}
