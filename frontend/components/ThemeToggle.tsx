'use client';

import { Sun, Moon, Monitor } from 'lucide-react';
import { useTheme } from './ThemeProvider';

const options = [
    { value: 'light' as const, icon: Sun, label: 'Light' },
    { value: 'dark' as const, icon: Moon, label: 'Dark' },
    { value: 'system' as const, icon: Monitor, label: 'System' },
];

export default function ThemeToggle() {
    const { theme, setTheme } = useTheme();

    return (
        <div
            className="inline-flex items-center rounded-xl p-1 gap-0.5"
            style={{
                background: 'var(--toggle-bg)',
                border: '1px solid var(--border-default)',
            }}
        >
            {options.map(({ value, icon: Icon, label }) => {
                const isActive = theme === value;
                return (
                    <button
                        key={value}
                        onClick={() => setTheme(value)}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200"
                        style={{
                            background: isActive ? 'var(--toggle-active-bg)' : 'transparent',
                            color: isActive ? 'var(--accent)' : 'var(--text-muted)',
                            boxShadow: isActive ? '0 1px 3px rgba(0,0,0,0.15)' : 'none',
                        }}
                        title={label}
                    >
                        <Icon className="w-3.5 h-3.5" />
                        <span className="hidden sm:inline">{label}</span>
                    </button>
                );
            })}
        </div>
    );
}
