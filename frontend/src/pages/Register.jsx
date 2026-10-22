import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api/client';
import { GraduationCap, AlertCircle, CheckCircle2, UserPlus, ArrowRight } from 'lucide-react';

export const Register = () => {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    roll_no: '',
    name: '',
    email: '',
    phone: '',
    program: 'BTECH',
    d_id: 1,
    admission_year: 2026,
    password: '',
    confirm_password: '',
  });

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const departments = [
    { d_id: 1, name: 'Computer Science and Engineering', program: 'BTECH' },
    { d_id: 2, name: 'Artificial Intelligence and Data Science', program: 'BTECH' },
    { d_id: 3, name: 'Electronics and Communication Engineering', program: 'BTECH' },
    { d_id: 4, name: 'Institute of Management', program: 'BBA' },
    { d_id: 5, name: 'Institute of Design', program: 'BDES' },
  ];

  const handleProgramChange = (prog) => {
    let defaultDid = 1;
    if (prog === 'BBA') defaultDid = 4;
    else if (prog === 'BDES') defaultDid = 5;

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

    setLoading(true);

    try {
      const payload = {
        roll_no: formData.roll_no.trim().toUpperCase(),
        name: formData.name.trim(),
        email: formData.email.trim().toLowerCase(),
        phone: formData.phone.trim() || null,
        d_id: parseInt(formData.d_id, 10),
        program: formData.program,
        admission_year: parseInt(formData.admission_year, 10),
        password: formData.password,
      };

      const resp = await api.post('/auth/register', payload);
      setSuccess('Registration successful! Please check your JKLU email inbox or log in after verification.');
      setTimeout(() => {
        navigate('/login');
      }, 2500);
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
            Create your academic account. Only JK Lakshmipat University students with valid credentials may register.
          </p>
        </div>

        {error && (
          <div className="flex items-start space-x-2 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs">
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0 text-rose-600" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="flex items-start space-x-2 p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs">
            <CheckCircle2 className="w-4 h-4 mt-0.5 shrink-0 text-emerald-600" />
            <span>{success}</span>
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
                placeholder="2026BTECH099"
                value={formData.roll_no}
                onChange={(e) => setFormData({ ...formData, roll_no: e.target.value.toUpperCase() })}
                className="w-full px-3 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary text-sm font-mono placeholder:text-academic-muted/50 focus:outline-none focus:ring-2 focus:ring-academic-burgundy/40"
              />
              <p className="text-[10px] text-academic-muted mt-1 font-mono">Regex: ^(20[0-9]{'{2}'})(BTECH|BBA|BDES)[0-9]{'{3}'}$</p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-academic-primary mb-1 uppercase tracking-wider">
                Full Name *
              </label>
              <input
                type="text"
                required
                placeholder="e.g. Ananya Sharma"
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
                placeholder="ananya.sharma@jklu.edu.in"
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
                placeholder="9829012345"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary text-sm placeholder:text-academic-muted/50 focus:outline-none focus:ring-2 focus:ring-academic-burgundy/40"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-academic-primary mb-1 uppercase tracking-wider">
                Program *
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

            <div>
              <label className="block text-xs font-semibold text-academic-primary mb-1 uppercase tracking-wider">
                Admission Year *
              </label>
              <select
                value={formData.admission_year}
                onChange={(e) => setFormData({ ...formData, admission_year: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary text-sm focus:outline-none focus:ring-2 focus:ring-academic-burgundy/40"
              >
                <option value="2024">2024 (Senior)</option>
                <option value="2025">2025 (Junior)</option>
                <option value="2026">2026 (Freshman)</option>
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
                placeholder="Min 8 characters"
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
                placeholder="Re-enter password"
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
            {loading ? 'Submitting Registration...' : 'Register Academic Account'}
          </button>
        </form>

        <div className="text-center text-xs text-academic-muted pt-2">
          Already registered?{' '}
          <Link to="/login" className="font-semibold text-academic-burgundy hover:underline">
            Sign in to existing account
          </Link>
        </div>
      </div>
    </div>
  );
};
