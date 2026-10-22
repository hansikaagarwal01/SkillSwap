import React, { useEffect } from 'react';
import { X } from 'lucide-react';

export const Modal = ({ isOpen, onClose, title, children, maxWidth = 'max-w-lg' }) => {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.body.style.overflow = 'unset';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="fixed inset-0 bg-academic-primary/40 backdrop-blur-sm transition-opacity" onClick={onClose} />
      <div className="flex min-h-full items-center justify-center p-4">
        <div className={`relative w-full ${maxWidth} bg-academic-card border border-academic-border rounded-xl shadow-2xl p-6 z-10 animate-in fade-in zoom-in-95 duration-150`}>
          <div className="flex items-center justify-between pb-3 border-b border-academic-border mb-4">
            <h3 className="text-lg font-serif font-bold text-academic-primary">{title}</h3>
            <button
              onClick={onClose}
              className="text-academic-muted hover:text-academic-primary transition-colors p-1 rounded-lg hover:bg-academic-secondary"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          {children}
        </div>
      </div>
    </div>
  );
};
