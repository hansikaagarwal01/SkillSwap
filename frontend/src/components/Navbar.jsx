import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
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
  const { user, logout } = useAuth();
  const location = useLocation();

  const navLinks = [
    { to: '/mentors', label: 'Students & Mentors', icon: Users },
    { to: '/skills', label: 'Skills', icon: BookOpen },
    { to: '/sessions', label: 'Sessions', icon: Calendar, authRequired: true },
    { to: '/marketplace', label: 'Marketplace', icon: ShoppingBag },
    { to: '/leaderboard', label: 'Leaderboard', icon: Award },
    { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  ];

  if (user && user.role === 'ADMIN') {
    navLinks.push({ to: '/admin', label: 'Admin', icon: ShieldCheck, authRequired: true });
  }

  const isActive = (path) => location.pathname === path;

  return (
    <header className="sticky top-0 z-40 bg-academic-card/95 backdrop-blur-md border-b border-academic-border shadow-sm">
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
