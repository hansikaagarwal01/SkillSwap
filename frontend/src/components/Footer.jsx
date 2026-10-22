import React from 'react';
import { GraduationCap, Database, Code, CheckCircle } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="bg-academic-secondary border-t border-academic-border mt-20 text-academic-primary/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="md:col-span-2">
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

          <div>
            <h4 className="font-serif font-bold text-sm text-academic-primary mb-3">Relational Features</h4>
            <ul className="space-y-2 text-xs text-academic-muted">
              <li>• Universal Roll_No PK Regex</li>
              <li>• Strict @jklu.edu.in Emails</li>
              <li>• Zero-Credit Mentorship</li>
              <li>• Immutable Reputation Engine</li>
              <li>• Safe Concurrency Updates</li>
            </ul>
          </div>

          <div>
            <h4 className="font-serif font-bold text-sm text-academic-primary mb-3">DBMS Verification</h4>
            <div className="space-y-2 text-xs text-academic-muted">
              <div className="flex items-center space-x-1.5 text-emerald-800 font-medium">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                <span>34 Real SQL Queries Verified</span>
              </div>
              <div className="flex items-center space-x-1.5 text-emerald-800 font-medium">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                <span>BCNF / 3NF Normalized Schema</span>
              </div>
              <div className="flex items-center space-x-1.5 text-emerald-800 font-medium">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                <span>Automated Concurrency Gates</span>
              </div>
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
