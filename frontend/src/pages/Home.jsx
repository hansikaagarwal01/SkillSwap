import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';
import {
  GraduationCap,
  Users,
  BookOpen,
  Calendar,
  ShoppingBag,
  Award,
  ShieldCheck,
  ArrowRight,
  Sparkles,
  Lock,
} from 'lucide-react';

export const Home = () => {
  const [stats, setStats] = useState({
    total_students: 0,
    total_skills: 0,
    total_desired_skills: 0,
    total_sessions: 0,
    total_listings: 0,
  });

  useEffect(() => {
    api
      .get('/analytics/overview')
      .then((res) => {
        setStats({
          total_students: res.data.total_students ?? 0,
          total_skills: res.data.total_skills ?? 0,
          total_desired_skills: res.data.total_desired_skills ?? 0,
          total_sessions: res.data.total_sessions ?? 0,
          total_listings: res.data.total_listings ?? 0,
        });
      })
      .catch((err) => console.error('Failed to fetch analytics overview', err));
  }, []);

  return (
    <div className="space-y-16 py-8">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-2xl bg-academic-card border border-academic-border p-8 md:p-14 shadow-sm">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-96 h-96 bg-academic-burgundy/5 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 -mb-10 -ml-10 w-80 h-80 bg-academic-gold/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative max-w-3xl space-y-6">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-academic-secondary border border-academic-border text-xs font-semibold text-academic-primary">
            <Sparkles className="w-3.5 h-3.5 text-academic-gold" />
            <span>JK Lakshmipat University Academic Network</span>
          </div>

          <h1 className="text-4xl md:text-5xl font-serif font-bold text-academic-primary tracking-tight leading-tight">
            Elevate Your Learning with Peer Mentors & Campus Exchange
          </h1>

          <p className="text-base md:text-lg text-academic-muted leading-relaxed font-light">
            A trusted academic ecosystem for B.Tech, BBA, and B.Des students. Book free 1-on-1 mentorship sessions with verified seniors, build non-spendable academic reputation, and buy or sell course essentials securely.
          </p>

          <div className="flex flex-wrap items-center gap-4 pt-2">
            <Link
              to="/mentors"
              className="inline-flex items-center space-x-2 px-6 py-3 rounded-xl bg-academic-burgundy text-white font-semibold text-sm shadow-md hover:bg-academic-burgundy/90 transition-all card-hover"
            >
              <Users className="w-4 h-4" />
              <span>Explore Mentors</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              to="/marketplace"
              className="inline-flex items-center space-x-2 px-6 py-3 rounded-xl bg-academic-card border border-academic-border text-academic-primary font-semibold text-sm hover:bg-academic-secondary transition-all card-hover"
            >
              <ShoppingBag className="w-4 h-4 text-academic-accent" />
              <span>Campus Marketplace</span>
            </Link>
          </div>
        </div>
      </section>

      {/* Campus Stats Counter */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'JKLU Students', value: stats.total_students, icon: Users, sub: 'BTECH / BBA / BDES Programs' },
          { label: 'Catalog Skills', value: stats.total_skills, icon: BookOpen, sub: 'Distinct Academic & Extracurricular' },
          { label: 'Desired Skills', value: stats.total_desired_skills ?? 0, icon: Sparkles, sub: 'Peer Learning Goals' },
          { label: 'Marketplace Items', value: stats.total_listings, icon: ShoppingBag, sub: 'Authentic Campus Offerings' },
        ].map((item, idx) => {
          const Icon = item.icon;
          return (
            <div
              key={idx}
              className="bg-academic-card border border-academic-border rounded-xl p-5 shadow-xs card-hover flex flex-col justify-between"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold text-academic-muted uppercase tracking-wider">{item.label}</span>
                <div className="w-8 h-8 rounded-lg bg-academic-secondary flex items-center justify-center text-academic-burgundy">
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <div>
                <p className="text-3xl font-serif font-bold text-academic-primary">{item.value}</p>
                <p className="text-[11px] text-academic-muted mt-0.5">{item.sub}</p>
              </div>
            </div>
          );
        })}
      </section>

      {/* 3 Core Pillars */}
      <section className="space-y-6">
        <div className="text-center max-w-xl mx-auto space-y-2">
          <h2 className="text-2xl md:text-3xl font-serif font-bold text-academic-primary">
            Engineered for Academic Excellence
          </h2>
          <p className="text-sm text-academic-muted">
            Every feature is backed by strict relational integrity constraints and atomic business transactions.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Pillar 1 */}
          <div className="bg-academic-card border border-academic-border rounded-xl p-6 shadow-xs card-hover space-y-4">
            <div className="w-12 h-12 rounded-xl bg-indigo-50 border border-indigo-200 text-indigo-700 flex items-center justify-center">
              <Users className="w-6 h-6" />
            </div>
            <h3 className="font-serif font-bold text-lg text-academic-primary">1-on-1 Peer Mentorship</h3>
            <p className="text-xs text-academic-muted leading-relaxed">
              Connect directly with high-achieving seniors. Filter mentors by department, proficiency level, and verified peer ratings. Sessions follow an explicit state machine from Request to Completion.
            </p>
            <Link to="/mentors" className="inline-flex items-center text-xs font-semibold text-academic-burgundy hover:underline">
              Find a Mentor &rarr;
            </Link>
          </div>

          {/* Pillar 2 */}
          <div className="bg-academic-card border border-academic-border rounded-xl p-6 shadow-xs card-hover space-y-4">
            <div className="w-12 h-12 rounded-xl bg-amber-50 border border-amber-200 text-amber-700 flex items-center justify-center">
              <Award className="w-6 h-6" />
            </div>
            <h3 className="font-serif font-bold text-lg text-academic-primary">Non-Spendable Reputation</h3>
            <p className="text-xs text-academic-muted leading-relaxed">
              Reputation points represent genuine academic contribution and cannot be spent or transferred. Mentors earn exactly +10 points per completed session, safeguarded by row-level locking.
            </p>
            <Link to="/leaderboard" className="inline-flex items-center text-xs font-semibold text-academic-burgundy hover:underline">
              View Campus Leaderboard &rarr;
            </Link>
          </div>

          {/* Pillar 3 */}
          <div className="bg-academic-card border border-academic-border rounded-xl p-6 shadow-xs card-hover space-y-4">
            <div className="w-12 h-12 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 flex items-center justify-center">
              <ShoppingBag className="w-6 h-6" />
            </div>
            <h3 className="font-serif font-bold text-lg text-academic-primary">Campus Marketplace</h3>
            <p className="text-xs text-academic-muted leading-relaxed">
              Buy and sell engineering textbooks, Arduino kits, scientific calculators, and design tools within the student body. Multi-buyer purchases are atomically gated to prevent race conditions.
            </p>
            <Link to="/marketplace" className="inline-flex items-center text-xs font-semibold text-academic-burgundy hover:underline">
              Browse Listings &rarr;
            </Link>
          </div>
        </div>
      </section>

      {/* Relational Integrity Spotlight */}
      <section className="bg-academic-secondary/70 border border-academic-border rounded-2xl p-8 space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-academic-burgundy text-xs font-bold uppercase tracking-wider mb-1">
              <Lock className="w-4 h-4" />
              <span>DBMS Architecture & Normalization</span>
            </div>
            <h3 className="font-serif font-bold text-xl text-academic-primary">
              Academic Database Guarantees
            </h3>
          </div>
          <Link
            to="/analytics"
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-academic-card border border-academic-border text-xs font-semibold text-academic-primary hover:bg-academic-bg transition-colors"
          >
            <span>View Live Analytics Overview</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
          <div className="bg-academic-card border border-academic-border rounded-lg p-4 space-y-1.5">
            <p className="font-semibold text-academic-primary">Universal Roll_No PK</p>
            <p className="text-academic-muted">
              Matches regex <code className="font-mono bg-academic-secondary px-1 py-0.5 rounded">^(20[0-9]{2})(BTECH|BBA|BDES)[0-9]{3}$</code> across all foreign keys.
            </p>
          </div>

          <div className="bg-academic-card border border-academic-border rounded-lg p-4 space-y-1.5">
            <p className="font-semibold text-academic-primary">Strict Email Domain Validation</p>
            <p className="text-academic-muted">
              Strictly enforces <code className="font-mono bg-academic-secondary px-1 py-0.5 rounded">@jklu.edu.in</code> and rejects lookalike subdomains like <code className="font-mono text-rose-600">evil-jklu.edu.in</code>.
            </p>
          </div>

          <div className="bg-academic-card border border-academic-border rounded-lg p-4 space-y-1.5">
            <p className="font-semibold text-academic-primary">Safe Concurrency Control</p>
            <p className="text-academic-muted">
              Atomic conditional updates and <code className="font-mono bg-academic-secondary px-1 py-0.5 rounded">SELECT FOR UPDATE</code> with unique history constraints.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};
