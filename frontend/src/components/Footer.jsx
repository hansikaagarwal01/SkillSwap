import React from 'react';

export const Footer = () => {
  return (
    <footer className="bg-academic-secondary border-t border-academic-border mt-20 text-academic-primary/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-8">
          <div>
            <div className="flex items-center space-x-2 mb-3">
              <div className="w-8 h-8 rounded-lg bg-academic-burgundy text-white flex items-center justify-center font-serif font-bold text-sm">
                SK
              </div>
              <span className="font-serif font-bold text-lg text-academic-primary">SkillSwap JKLU</span>
            </div>
            <p className="text-xs text-academic-muted leading-relaxed max-w-md">
              A university peer-mentoring, skill-sharing, and student marketplace platform engineered specifically for JK Lakshmipat University, Jaipur. Built with strict relational integrity, ACID transactions, and zero-trust academic validation.
            </p>
            <div className="mt-4 flex items-center space-x-4 text-xs font-mono text-academic-muted">
              <span>MySQL 8.0+ InnoDB</span>
              <span>•</span>
              <span>FastAPI 0.115+</span>
              <span>•</span>
              <span>React 18+ / Vite</span>
            </div>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-academic-border flex flex-col sm:flex-row items-center justify-between text-xs text-academic-muted">
          <p>© 2026 JK Lakshmipat University, Jaipur. DBMS Academic Capstone Project.</p>
          <div className="flex items-center space-x-4 mt-2 sm:mt-0 font-mono">
            <span>BTECH / BBA / BDES</span>
            <span>•</span>
            <span>Jaipur, Rajasthan</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
