'use client';

import { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'light' | 'dark' | 'system';

interface ThemeContextType {
    theme: Theme;
    setTheme: (theme: Theme) => void;
    resolvedTheme: 'light' | 'dark';
}

const defaultContext: ThemeContextType = {
    theme: 'system',
    setTheme: () => { },
    resolvedTheme: 'dark',
};

const ThemeContext = createContext<ThemeContextType>(defaultContext);

export function useTheme() {
    return useContext(ThemeContext);
}

function getSystemTheme(): 'light' | 'dark' {
    if (typeof window === 'undefined') return 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

export default function ThemeProvider({ children }: { children: React.ReactNode }) {
    const [theme, setThemeState] = useState<Theme>('system');
    const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('dark');
    const [mounted, setMounted] = useState(false);

    // Load saved theme from localStorage on mount
    useEffect(() => {
        const saved = localStorage.getItem('theme') as Theme | null;
        if (saved && ['light', 'dark', 'system'].includes(saved)) {
            setThemeState(saved);
        }
        setMounted(true);
    }, []);

    // Resolve the actual theme and apply data-theme attribute
    useEffect(() => {
        if (!mounted) return;

        const resolved = theme === 'system' ? getSystemTheme() : theme;
        setResolvedTheme(resolved);
        document.documentElement.setAttribute('data-theme', resolved);

        // Listen for system theme changes when in 'system' mode
        if (theme === 'system') {
            const mq = window.matchMedia('(prefers-color-scheme: dark)');
            const handler = (e: MediaQueryListEvent) => {
                const newResolved = e.matches ? 'dark' : 'light';
                setResolvedTheme(newResolved);
                document.documentElement.setAttribute('data-theme', newResolved);
            };
            mq.addEventListener('change', handler);
            return () => mq.removeEventListener('change', handler);
        }
    }, [theme, mounted]);

    const setTheme = (t: Theme) => {
        setThemeState(t);
        localStorage.setItem('theme', t);
    };

    // Prevent flash of wrong theme
    if (!mounted) {
        return <div style={{ visibility: 'hidden' }}>{children}</div>;
    }

    return (
        <ThemeContext.Provider value={{ theme, setTheme, resolvedTheme }}>
            {children}
        </ThemeContext.Provider>
    );
}
