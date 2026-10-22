import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { GraduationCap, Lock, User, AlertCircle, ArrowRight, Sparkles, CheckCircle2 } from 'lucide-react';

export const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [rollNo, setRollNo] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(rollNo.trim().toUpperCase(), password);
      navigate('/mentors');
    } catch (err) {
      const msg = err.response?.data?.error?.message || 'Invalid credentials or account unverified.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleInstantVerify = async () => {
    if (!rollNo.trim()) return;
    setVerifying(true);
    try {
      await api.post(`/auth/verify-account/${rollNo.trim().toUpperCase()}`);
      setError('');
      if (password) {
        await login(rollNo.trim().toUpperCase(), password);
        navigate('/mentors');
      } else {
        alert(`Account ${rollNo.toUpperCase()} verified! Please enter your password to sign in.`);
      }
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to auto-verify account.');
    } finally {
      setVerifying(false);
    }
  };

  const handleQuickFill = (r, p) => {
    setRollNo(r);
    setPassword(p);
    setError('');
  };

  return (
    <div className="max-w-md mx-auto py-12 px-4">
      <div className="bg-academic-card border border-academic-border rounded-2xl shadow-xl p-8 space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-xl bg-academic-burgundy text-white flex items-center justify-center mx-auto shadow-md">
            <GraduationCap className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-serif font-bold text-academic-primary">JKLU Student Sign In</h2>
          <p className="text-xs text-academic-muted">
            Enter your university roll number and credentials to access your academic portal.
          </p>
        </div>

        {error && (
          <div className="p-3.5 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs space-y-2">
            <div className="flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 mt-0.5 shrink-0 text-rose-600" />
              <span className="font-medium">{error}</span>
            </div>

            {error.toLowerCase().includes('verify') && (
              <button
                type="button"
                onClick={handleInstantVerify}
                disabled={verifying}
                className="w-full py-2 px-3 rounded-lg bg-emerald-700 text-white font-semibold text-xs hover:bg-emerald-800 transition-colors flex items-center justify-center space-x-1.5 shadow-xs"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>{verifying ? 'Activating...' : `Click to Activate & Log In as ${rollNo || 'Student'}`}</span>
              </button>
            )}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-academic-primary mb-1 uppercase tracking-wider">
              University Roll Number
            </label>
            <div className="relative">
              <input
                type="text"
                required
                placeholder="e.g. 2025BTECH027"
                value={rollNo}
                onChange={(e) => {
                  setRollNo(e.target.value.toUpperCase());
                  setError('');
                }}
                className="w-full px-3.5 py-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary text-sm font-mono placeholder:text-academic-muted/50 focus:outline-none focus:ring-2 focus:ring-academic-burgundy/40 focus:border-academic-burgundy"
              />
              <User className="absolute right-3 top-3 w-4 h-4 text-academic-muted" />
            </div>
            <p className="text-[10px] text-academic-muted mt-1 font-mono">Format: 20YY[BTECH|BBA|BDES]NNN</p>
          </div>

          <div>
            <label className="block text-xs font-semibold text-academic-primary mb-1 uppercase tracking-wider">
              Password
            </label>
            <div className="relative">
              <input
                type="password"
                required
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  setError('');
                }}
                className="w-full px-3.5 py-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary text-sm placeholder:text-academic-muted/50 focus:outline-none focus:ring-2 focus:ring-academic-burgundy/40 focus:border-academic-burgundy"
              />
              <Lock className="absolute right-3 top-3 w-4 h-4 text-academic-muted" />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-academic-burgundy text-white font-semibold text-sm shadow-md hover:bg-academic-burgundy/90 transition-all disabled:opacity-50"
          >
            {loading ? 'Authenticating...' : 'Sign In to Portal'}
          </button>
        </form>

        {/* Demo Quick Fills */}
        <div className="pt-4 border-t border-academic-border space-y-2">
          <div className="flex items-center space-x-1 text-xs font-semibold text-academic-muted">
            <Sparkles className="w-3.5 h-3.5 text-academic-gold" />
            <span>Academic Demonstration Credentials:</span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs">
            <button
              type="button"
              onClick={() => handleQuickFill('2024BTECH001', 'Admin@JKLU2026')}
              className="p-2 rounded-lg border border-academic-border bg-academic-secondary/60 hover:bg-academic-secondary text-left transition-colors"
            >
              <p className="font-semibold text-academic-primary">Aarav (Admin)</p>
              <p className="text-[10px] text-academic-muted font-mono">2024BTECH001</p>
            </button>

            <button
              type="button"
              onClick={() => handleQuickFill('2024BTECH002', 'Student@JKLU2026')}
              className="p-2 rounded-lg border border-academic-border bg-academic-secondary/60 hover:bg-academic-secondary text-left transition-colors"
            >
              <p className="font-semibold text-academic-primary">Bhavya (Student)</p>
              <p className="text-[10px] text-academic-muted font-mono">2024BTECH002</p>
            </button>
          </div>
        </div>

        <div className="text-center text-xs text-academic-muted pt-2">
          New to SkillSwap JKLU?{' '}
          <Link to="/register" className="font-semibold text-academic-burgundy hover:underline">
            Register your roll number
          </Link>
        </div>
      </div>
    </div>
  );
};
