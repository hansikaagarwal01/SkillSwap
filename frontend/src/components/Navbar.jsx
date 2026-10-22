import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  GraduationCap,
  BookOpen,
  Users,
  Calendar,
  ShoppingBag,
  Award,
  BarChart3,
  ShieldCheck,
  LogOut,
  User,
  Star,
  ChevronDown,
  Sparkles,
} from 'lucide-react';

export const Navbar = () => {
  const { user, login, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [demoMenuOpen, setDemoMenuOpen] = useState(false);

  const navLinks = [
    { to: '/mentors', label: 'Mentors', icon: Users },
    { to: '/skills', label: 'Skills', icon: BookOpen },
    { to: '/sessions', label: 'Sessions', icon: Calendar, authRequired: true },
    { to: '/marketplace', label: 'Marketplace', icon: ShoppingBag },
    { to: '/leaderboard', label: 'Leaderboard', icon: Award },
    { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  ];

  if (user && user.role === 'ADMIN') {
    navLinks.push({ to: '/admin', label: 'Admin', icon: ShieldCheck, authRequired: true });
  }

  const handleQuickLogin = async (roll_no, password) => {
    try {
      await login(roll_no, password);
      setDemoMenuOpen(false);
      navigate('/mentors');
    } catch (err) {
      console.error('Demo login failed', err);
    }
  };

  const isActive = (path) => location.pathname === path;

  return (
    <header className="sticky top-0 z-40 bg-academic-card/95 backdrop-blur-md border-b border-academic-border shadow-sm">
      {/* Top Academic Ribbon */}
      <div className="bg-academic-burgundy text-white text-xs px-4 py-1 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <GraduationCap className="w-3.5 h-3.5 text-academic-gold" />
          <span className="font-medium tracking-wide">JK Lakshmipat University, Jaipur</span>
          <span className="text-white/60">|</span>
          <span className="text-white/80">DBMS Academic Project (Verified MySQL 8.0 & FastAPI)</span>
        </div>
        <div className="hidden sm:flex items-center space-x-3 text-white/90">
          <span>Universal Roll_No PK</span>
          <span>•</span>
          <span>Free Sessions (0 credits)</span>
          <span>•</span>
          <span>Non-Spendable Reputation</span>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 rounded-lg bg-academic-burgundy text-white flex items-center justify-center font-serif font-bold text-xl shadow-md group-hover:bg-academic-accent transition-colors">
              SK
            </div>
            <div>
              <span className="font-serif font-bold text-xl text-academic-primary tracking-tight block leading-tight">
                SkillSwap <span className="text-academic-burgundy font-sans text-sm font-semibold uppercase tracking-wider">JKLU</span>
              </span>
              <span className="text-xs text-academic-muted block leading-none">Peer Mentoring & Campus Exchange</span>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1">
            {navLinks.map(({ to, label, icon: Icon, authRequired }) => {
              if (authRequired && !user) return null;
              const active = isActive(to);
              return (
                <Link
                  key={to}
                  to={to}
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    active
                      ? 'bg-academic-secondary text-academic-burgundy font-semibold'
                      : 'text-academic-primary/80 hover:text-academic-primary hover:bg-academic-secondary/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${active ? 'text-academic-burgundy' : 'text-academic-muted'}`} />
                  <span>{label}</span>
                </Link>
              );
            })}
          </nav>

          {/* User Controls & Demo Switcher */}
          <div className="flex items-center space-x-3">
            {user ? (
              <div className="flex items-center space-x-3">
                {/* Reputation Badge */}
                <div className="hidden lg:flex items-center space-x-1 bg-amber-50 border border-amber-200 text-amber-900 px-2.5 py-1 rounded-full text-xs font-semibold shadow-xs">
                  <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-500" />
                  <span>{user.reputation_points} pts</span>
                </div>

                {/* Profile Pill */}
                <Link
                  to="/profile"
                  className="flex items-center space-x-2 pl-2 pr-3 py-1.5 rounded-lg border border-academic-border hover:bg-academic-secondary transition-colors"
                >
                  <div className="w-7 h-7 rounded-full bg-academic-burgundy text-white flex items-center justify-center text-xs font-bold">
                    {user.name.charAt(0)}
                  </div>
                  <div className="text-left hidden sm:block">
                    <p className="text-xs font-semibold text-academic-primary leading-tight">{user.name}</p>
                    <p className="text-[10px] text-academic-muted leading-tight font-mono">{user.roll_no}</p>
                  </div>
                </Link>

                {/* Logout Button */}
                <button
                  onClick={logout}
                  title="Logout"
                  className="p-2 text-academic-muted hover:text-academic-burgundy hover:bg-academic-secondary rounded-lg transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                {/* Quick Demo Switcher Dropdown */}
                <div className="relative">
                  <button
                    onClick={() => setDemoMenuOpen(!demoMenuOpen)}
                    className="flex items-center space-x-1.5 bg-academic-secondary border border-academic-border text-academic-primary px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-academic-border/60 transition-colors"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-academic-gold" />
                    <span className="hidden sm:inline">Quick Demo Login</span>
                    <ChevronDown className="w-3 h-3 text-academic-muted" />
                  </button>

                  {demoMenuOpen && (
                    <div className="absolute right-0 mt-2 w-64 bg-academic-card border border-academic-border rounded-xl shadow-xl py-2 z-50 animate-in fade-in zoom-in-95">
                      <div className="px-3 py-1 border-b border-academic-border mb-1">
                        <p className="text-xs font-semibold text-academic-muted">Select Academic Persona</p>
                      </div>
                      <button
                        onClick={() => handleQuickLogin('2024BTECH001', 'Admin@JKLU2026')}
                        className="w-full text-left px-3 py-2 text-xs hover:bg-academic-secondary flex flex-col"
                      >
                        <span className="font-semibold text-academic-primary">Aarav Sharma (Admin)</span>
                        <span className="text-[11px] text-academic-muted font-mono">2024BTECH001 • 40 pts</span>
                      </button>
                      <button
                        onClick={() => handleQuickLogin('2024BTECH002', 'Student@JKLU2026')}
                        className="w-full text-left px-3 py-2 text-xs hover:bg-academic-secondary flex flex-col"
                      >
                        <span className="font-semibold text-academic-primary">Bhavya Patel (Student)</span>
                        <span className="text-[11px] text-academic-muted font-mono">2024BTECH002 • 50 pts</span>
                      </button>
                      <button
                        onClick={() => handleQuickLogin('2024BBA001', 'Student@JKLU2026')}
                        className="w-full text-left px-3 py-2 text-xs hover:bg-academic-secondary flex flex-col"
                      >
                        <span className="font-semibold text-academic-primary">Sneha Agarwal (BBA Mentor)</span>
                        <span className="text-[11px] text-academic-muted font-mono">2024BBA001 • 30 pts</span>
                      </button>
                    </div>
                  )}
                </div>

                <Link
                  to="/login"
                  className="px-3.5 py-1.5 text-xs font-medium text-academic-primary hover:text-academic-burgundy transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="px-3.5 py-1.5 text-xs font-semibold bg-academic-burgundy text-white rounded-lg hover:bg-academic-burgundy/90 transition-colors shadow-xs"
                >
                  Register
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
