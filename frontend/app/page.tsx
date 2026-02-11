'use client';

import Twin from '@/components/twin';
import ThemeToggle from '@/components/ThemeToggle';

export default function Home() {
  return (
    <main className="h-screen flex flex-col" style={{ background: 'var(--bg-page)' }}>
      {/* Top bar with theme toggle */}
      <div className="flex items-center justify-end px-4 py-3 sm:px-6">
        <ThemeToggle />
      </div>

      {/* Chat container — centered on desktop, full-width on mobile */}
      <div className="flex-1 min-h-0 px-0 md:px-6 md:pb-6">
        <div className="chat-container">
          <Twin />
        </div>
      </div>

      {/* Minimal footer */}
      <footer className="py-2 text-center text-xs" style={{ color: 'var(--text-muted)' }}>
        <p>All rights reserved &copy; {new Date().getFullYear()}</p>
      </footer>
    </main>
  );
}