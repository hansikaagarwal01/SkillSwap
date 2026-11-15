import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import api from '../api/client';
import { Mail, CheckCircle2, AlertCircle, RefreshCw, ArrowRight } from 'lucide-react';

export const VerifyEmail = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const tokenParam = searchParams.get('token') || '';
  const [token, setToken] = useState(tokenParam);
  const [resendEmail, setResendEmail] = useState('');

  const [loading, setLoading] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [resendMsg, setResendMsg] = useState('');

  const handleVerify = async (tokenToUse) => {
    const raw = (tokenToUse || token).trim();
    if (!raw) {
      setError('Please provide a valid verification token.');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const resp = await api.post('/auth/verify-email', { token: raw });
      setSuccess(resp.data?.message || 'Email verified successfully! You can now sign in to your account.');
    } catch (err) {
      const msg = err.response?.data?.error?.message || 'Failed to verify email. The token may be invalid or expired.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (tokenParam) {
      handleVerify(tokenParam);
    }
  }, [tokenParam]);

  const handleResend = async (e) => {
    e.preventDefault();
    if (!resendEmail.trim()) return;

    setResendLoading(true);
    setResendMsg('');
    setError('');

    try {
      const resp = await api.post('/auth/resend-verification', { email: resendEmail.trim().toLowerCase() });
      setResendMsg(resp.data?.message || 'If an unverified account exists for this email, a new verification link has been sent.');
    } catch (err) {
      const msg = err.response?.data?.error?.message || 'Failed to resend verification. Please try again later.';
      setError(msg);
    } finally {
      setResendLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto py-12 px-4">
      <div className="bg-academic-card border border-academic-border rounded-2xl shadow-xl p-8 space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-xl bg-academic-burgundy text-white flex items-center justify-center mx-auto shadow-md">
            <Mail className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-serif font-bold text-academic-primary">Email Verification</h2>
          <p className="text-xs text-academic-muted">
            Confirm your official JKLU student email to activate your account.
          </p>
        </div>

        {error && (
          <div className="flex items-start space-x-2 p-3.5 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs">
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0 text-rose-600" />
            <span className="font-medium">{error}</span>
          </div>
        )}

        {success && (
          <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs space-y-3">
            <div className="flex items-start space-x-2">
              <CheckCircle2 className="w-5 h-5 shrink-0 text-emerald-600 mt-0.5" />
              <div>
                <p className="font-semibold text-sm">Account Verified!</p>
                <p className="text-emerald-800">{success}</p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => navigate('/login')}
              className="w-full py-2.5 px-4 rounded-lg bg-emerald-700 text-white font-semibold hover:bg-emerald-800 transition-colors flex items-center justify-center space-x-1.5 shadow-xs"
            >
              <span>Proceed to Sign In</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {!success && (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleVerify(token);
            }}
            className="space-y-4"
          >
            <div>
              <label className="block text-xs font-semibold text-academic-primary mb-1 uppercase tracking-wider">
                Verification Token
              </label>
              <input
                type="text"
                required
                placeholder="Paste your 43-character verification token"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary text-xs font-mono placeholder:text-academic-muted/50 focus:outline-none focus:ring-2 focus:ring-academic-burgundy/40"
              />
              <p className="text-[11px] text-academic-muted mt-1">
                Found in the email sent upon registration or generated in your development server logs.
              </p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 rounded-lg bg-academic-burgundy text-white font-semibold text-xs hover:bg-academic-burgundy/90 transition-all shadow-xs disabled:opacity-50 flex items-center justify-center space-x-2"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>{loading ? 'Verifying Account...' : 'Verify & Activate Account'}</span>
            </button>
          </form>
        )}

        <div className="pt-4 border-t border-academic-border space-y-3 text-xs">
          <p className="font-semibold text-academic-primary">Did not receive or expired token?</p>

          {resendMsg && (
            <div className="p-3 rounded-lg bg-academic-secondary/60 border border-academic-border text-academic-primary text-xs">
              {resendMsg}
            </div>
          )}

          <form onSubmit={handleResend} className="flex gap-2">
            <input
              type="email"
              required
              placeholder="student@jklu.edu.in"
              value={resendEmail}
              onChange={(e) => setResendEmail(e.target.value)}
              className="flex-1 px-3 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary text-xs placeholder:text-academic-muted/50 focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
            />
            <button
              type="submit"
              disabled={resendLoading}
              className="px-3.5 py-2 rounded-lg border border-academic-border bg-academic-card text-academic-primary font-medium hover:bg-academic-secondary transition-colors shrink-0 disabled:opacity-50 flex items-center space-x-1"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${resendLoading ? 'animate-spin' : ''}`} />
              <span>Resend</span>
            </button>
          </form>
        </div>

        <div className="text-center pt-2">
          <Link to="/login" className="text-xs text-academic-burgundy hover:underline font-medium">
            Back to Sign In
          </Link>
        </div>
      </div>
    </div>
  );
};
