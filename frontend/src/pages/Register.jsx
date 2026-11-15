import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { GraduationCap, AlertCircle, CheckCircle2, UserPlus, Sparkles } from 'lucide-react';

export const Register = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [formData, setFormData] = useState({
    roll_no: '',
    name: '',
    email: '',
    phone: '',
    program: 'BTECH',
    d_id: 1,
    password: '',
    confirm_password: '',
  });

  const [detectedYear, setDetectedYear] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const [departments, setDepartments] = useState([]);

  useEffect(() => {
    api
      .get('/departments')
      .then((res) => {
        if (res.data && res.data.length > 0) {
          setDepartments(res.data);
        }
      })
      .catch((err) => console.error('Failed to fetch departments', err));
  }, []);

  // Auto-detect Admission Year and Program directly from Roll Number string!
  useEffect(() => {
    const clean = formData.roll_no.trim().toUpperCase();
    if (clean.length >= 4) {
      const yr = parseInt(clean.slice(0, 4), 10);
      if (yr >= 2000 && yr <= 2099) {
        setDetectedYear(yr);
      }
    } else {
      setDetectedYear(null);
    }

    if (clean.includes('BTECH') && formData.program !== 'BTECH') {
      const firstBtech = departments.find((d) => d.program === 'BTECH');
      setFormData((prev) => ({ ...prev, program: 'BTECH', d_id: firstBtech ? firstBtech.d_id : 1 }));
    } else if (clean.includes('BBA') && formData.program !== 'BBA') {
      const firstBba = departments.find((d) => d.program === 'BBA');
      setFormData((prev) => ({ ...prev, program: 'BBA', d_id: firstBba ? firstBba.d_id : 4 }));
    } else if (clean.includes('BDES') && formData.program !== 'BDES') {
      const firstBdes = departments.find((d) => d.program === 'BDES');
      setFormData((prev) => ({ ...prev, program: 'BDES', d_id: firstBdes ? firstBdes.d_id : 5 }));
    }
  }, [formData.roll_no, departments]);

  const handleProgramChange = (prog) => {
    const matched = departments.find((d) => d.program === prog);
    const defaultDid = matched ? matched.d_id : prog === 'BBA' ? 4 : prog === 'BDES' ? 5 : 1;

    setFormData({
      ...formData,
      program: prog,
      d_id: defaultDid,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (formData.password !== formData.confirm_password) {
      setError('Passwords do not match.');
      return;
    }

    if (!formData.email.endsWith('@jklu.edu.in')) {
      setError('Email must strictly end with @jklu.edu.in');
      return;
    }

    const roll = formData.roll_no.trim().toUpperCase();
    const admissionYear = detectedYear || parseInt(roll.slice(0, 4), 10) || 2026;

    setLoading(true);

    try {
      const payload = {
        roll_no: roll,
        name: formData.name.trim(),
        email: formData.email.trim().toLowerCase(),
        phone: formData.phone.trim() || null,
        d_id: parseInt(formData.d_id, 10),
        program: formData.program,
        admission_year: admissionYear,
        password: formData.password,
      };

      // 1. Register student account
      const resp = await api.post('/auth/register', payload);

      setSuccess(
        resp.data?.message ||
        `Registration submitted for ${roll}! A single-use verification link has been sent to ${payload.email}. Please verify your email to activate your account.`
      );
    } catch (err) {
      const msg = err.response?.data?.error?.message || 'Registration failed. Check roll number and email format.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto py-10 px-4">
      <div className="bg-academic-card border border-academic-border rounded-2xl shadow-xl p-8 space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-xl bg-academic-burgundy text-white flex items-center justify-center mx-auto shadow-md">
            <UserPlus className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-serif font-bold text-academic-primary">JKLU Student Registration</h2>
          <p className="text-xs text-academic-muted">
            Create your academic account. Roll number automatically identifies your cohort year and program.
          </p>
        </div>

        {error && (
          <div className="flex items-start space-x-2 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs">
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0 text-rose-600" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs space-y-3">
            <div className="flex items-start space-x-2">
              <CheckCircle2 className="w-5 h-5 shrink-0 text-emerald-600 mt-0.5" />
              <div className="space-y-1">
                <p className="font-semibold text-sm">Account Registration Successful!</p>
                <p className="text-emerald-800">{success}</p>
                <p className="text-[11px] text-emerald-700">
                  Check your university inbox for the verification token, or proceed to the verification screen.
                </p>
              </div>
            </div>
            <div className="flex space-x-2 pt-1">
              <button
                type="button"
                onClick={() => navigate('/verify-email')}
                className="py-2 px-4 rounded-lg bg-emerald-700 text-white font-semibold hover:bg-emerald-800 transition-colors shadow-xs"
              >
                Go to Email Verification
              </button>
              <button
                type="button"
                onClick={() => navigate('/login')}
                className="py-2 px-4 rounded-lg border border-emerald-300 bg-white text-emerald-800 font-medium hover:bg-emerald-50 transition-colors"
              >
                Sign In
              </button>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-academic-primary mb-1 uppercase tracking-wider">
                Roll Number *
              </label>
              <input
                type="text"
                required
                placeholder="e.g. XXXX"
                value={formData.roll_no}
                onChange={(e) => setFormData({ ...formData, roll_no: e.target.value.toUpperCase() })}
                className="w-full px-3 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary text-sm font-mono placeholder:text-academic-muted/50 focus:outline-none focus:ring-2 focus:ring-academic-burgundy/40"
              />
              {detectedYear ? (
                <div className="mt-1 flex items-center space-x-1.5 text-[11px] text-emerald-700 font-medium">
                  <Sparkles className="w-3 h-3 text-emerald-600" />
                  <span>Cohort Year: {detectedYear} (Auto-detected)</span>
                </div>
              ) : (
                <p className="text-[10px] text-academic-muted mt-1 font-mono">Format: 20YY[BTECH|BBA|BDES]NNN</p>
              )}
            </div>

            <div>
              <label className="block text-xs font-semibold text-academic-primary mb-1 uppercase tracking-wider">
                Full Name *
              </label>
              <input
                type="text"
                required
                placeholder="e.g. John Doe"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary text-sm placeholder:text-academic-muted/50 focus:outline-none focus:ring-2 focus:ring-academic-burgundy/40"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-academic-primary mb-1 uppercase tracking-wider">
                University Email *
              </label>
              <input
                type="email"
                required
                placeholder="e.g. student@example.com"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary text-sm placeholder:text-academic-muted/50 focus:outline-none focus:ring-2 focus:ring-academic-burgundy/40"
              />
              <p className="text-[10px] text-academic-muted mt-1">Must end with @jklu.edu.in</p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-academic-primary mb-1 uppercase tracking-wider">
                Phone Number (Optional)
              </label>
              <input
                type="tel"
                placeholder="e.g. 9876543210"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary text-sm placeholder:text-academic-muted/50 focus:outline-none focus:ring-2 focus:ring-academic-burgundy/40"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-academic-primary mb-1 uppercase tracking-wider">
                Academic Program *
              </label>
              <select
                value={formData.program}
                onChange={(e) => handleProgramChange(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary text-sm focus:outline-none focus:ring-2 focus:ring-academic-burgundy/40"
              >
                <option value="BTECH">B.Tech</option>
                <option value="BBA">BBA</option>
                <option value="BDES">B.Des</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-academic-primary mb-1 uppercase tracking-wider">
                Department *
              </label>
              <select
                value={formData.d_id}
                onChange={(e) => setFormData({ ...formData, d_id: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary text-sm focus:outline-none focus:ring-2 focus:ring-academic-burgundy/40"
              >
                {departments
                  .filter((d) => d.program === formData.program)
                  .map((dept) => (
                    <option key={dept.d_id} value={dept.d_id}>
                      {dept.name}
                    </option>
                  ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-academic-primary mb-1 uppercase tracking-wider">
                Password *
              </label>
              <input
                type="password"
                required
                placeholder="Enter your password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary text-sm focus:outline-none focus:ring-2 focus:ring-academic-burgundy/40"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-academic-primary mb-1 uppercase tracking-wider">
                Confirm Password *
              </label>
              <input
                type="password"
                required
                placeholder="Re-enter your password"
                value={formData.confirm_password}
                onChange={(e) => setFormData({ ...formData, confirm_password: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary text-sm focus:outline-none focus:ring-2 focus:ring-academic-burgundy/40"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-academic-burgundy text-white font-semibold text-sm shadow-md hover:bg-academic-burgundy/90 transition-all disabled:opacity-50"
          >
            {loading ? 'Creating & Activating Account...' : 'Complete Registration & Sign In'}
          </button>
        </form>

        <div className="text-center text-xs text-academic-muted pt-2">
          Already registered?{' '}
          <Link to="/login" className="font-semibold text-academic-burgundy hover:underline">
            Sign in with roll number
          </Link>
        </div>
      </div>
    </div>
  );
};
