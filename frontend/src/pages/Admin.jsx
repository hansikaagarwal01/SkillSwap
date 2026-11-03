import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import {
  ShieldCheck,
  Activity,
  UserCheck,
  CheckCircle2,
  AlertCircle,
  Database,
  Cpu,
  RefreshCw,
} from 'lucide-react';

export const Admin = () => {
  const { user } = useAuth();
  const [health, setHealth] = useState(null);
  const [healthLoading, setHealthLoading] = useState(true);

  // Approval input
  const [targetRoll, setTargetRoll] = useState('');
  const [approveLoading, setApproveLoading] = useState(false);
  const [approveMsg, setApproveMsg] = useState('');
  const [approveErr, setApproveErr] = useState('');

  const fetchHealth = async () => {
    setHealthLoading(true);
    try {
      const resp = await api.get('/health', { baseURL: '' });
      setHealth(resp.data);
    } catch (err) {
      console.error('Failed to fetch health', err);
    } finally {
      setHealthLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const handleApprove = async (e) => {
    e.preventDefault();
    setApproveLoading(true);
    setApproveMsg('');
    setApproveErr('');

    try {
      const resp = await api.post(`/admin/approve/${targetRoll.trim().toUpperCase()}`);
      setApproveMsg(resp.data.message || `Account for ${targetRoll} has been approved and activated.`);
      setTargetRoll('');
    } catch (err) {
      setApproveErr(err.response?.data?.error?.message || 'Failed to approve account.');
    } finally {
      setApproveLoading(false);
    }
  };

  if (!user || user.role !== 'ADMIN') {
    return (
      <div className="py-20 text-center space-y-2">
        <p className="font-serif font-bold text-lg text-academic-primary">Access Restricted</p>
        <p className="text-xs text-academic-muted">This portal requires academic administrator privileges.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 py-6">
      {/* Header */}
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-academic-burgundy text-white flex items-center justify-center shadow-xs">
          <ShieldCheck className="w-5 h-5" />
        </div>
        <div>
          <h1 className="text-3xl font-serif font-bold text-academic-primary">Academic Administration Portal</h1>
          <p className="text-xs text-academic-muted mt-0.5">
            System diagnostics, student registration verification, and database state oversight.
          </p>
        </div>
      </div>

      {/* System Health Card */}
      <div className="bg-academic-card border border-academic-border rounded-2xl p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-academic-border pb-3">
          <div className="flex items-center space-x-2">
            <Activity className="w-4 h-4 text-emerald-600" />
            <h3 className="font-serif font-bold text-base text-academic-primary">System & Database Health</h3>
          </div>
          <button
            onClick={fetchHealth}
            disabled={healthLoading}
            className="p-1.5 rounded-lg border border-academic-border bg-academic-secondary hover:bg-academic-border/60 text-academic-muted hover:text-academic-primary transition-colors text-xs flex items-center space-x-1"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${healthLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>

        {healthLoading ? (
          <p className="text-xs text-academic-muted py-4">Checking server diagnostics...</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-academic-secondary/60 border border-academic-border space-y-1">
              <span className="text-[10px] font-semibold text-academic-muted uppercase tracking-wider">
                Database Engine
              </span>
              <p className="font-serif font-bold text-base text-academic-primary flex items-center space-x-1.5">
                <Database className="w-4 h-4 text-emerald-600" />
                <span className="capitalize">{health?.database}</span>
              </p>
              <p className="text-[10px] text-academic-muted font-mono">MySQL 8.0.46 InnoDB</p>
            </div>

            <div className="p-4 rounded-xl bg-academic-secondary/60 border border-academic-border space-y-1">
              <span className="text-[10px] font-semibold text-academic-muted uppercase tracking-wider">
                API Environment
              </span>
              <p className="font-serif font-bold text-base text-academic-primary flex items-center space-x-1.5">
                <Cpu className="w-4 h-4 text-indigo-600" />
                <span className="capitalize">{health?.app_env}</span>
              </p>
              <p className="text-[10px] text-academic-muted font-mono">FastAPI 0.115.14</p>
            </div>

            <div className="p-4 rounded-xl bg-academic-secondary/60 border border-academic-border space-y-1">
              <span className="text-[10px] font-semibold text-academic-muted uppercase tracking-wider">
                Platform Status
              </span>
              <p className="font-serif font-bold text-base text-emerald-700 flex items-center space-x-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span className="uppercase">{health?.status}</span>
              </p>
              <p className="text-[10px] text-academic-muted font-mono">{health?.project}</p>
            </div>
          </div>
        )}
      </div>

      {/* Manual Student Approval Card */}
      <div className="bg-academic-card border border-academic-border rounded-2xl p-6 shadow-xs space-y-4">
        <div className="border-b border-academic-border pb-3">
          <div className="flex items-center space-x-2">
            <UserCheck className="w-4 h-4 text-academic-burgundy" />
            <h3 className="font-serif font-bold text-base text-academic-primary">
              Manual Student Account Approval
            </h3>
          </div>
          <p className="text-xs text-academic-muted mt-0.5">
            Approve students with status PENDING_APPROVAL to ACTIVE (Endpoint: POST /api/v1/admin/approve/:roll_no)
          </p>
        </div>

        {approveMsg && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>{approveMsg}</span>
          </div>
        )}

        {approveErr && (
          <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-rose-600" />
            <span>{approveErr}</span>
          </div>
        )}

        <form onSubmit={handleApprove} className="space-y-3 max-w-md text-xs">
          <div>
            <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
              Student Roll Number *
            </label>
            <input
              type="text"
              required
              placeholder="e.g. XXXX"
              value={targetRoll}
              onChange={(e) => setTargetRoll(e.target.value.toUpperCase())}
              className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary font-mono focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
            />
          </div>

          <button
            type="submit"
            disabled={approveLoading}
            className="px-5 py-2.5 rounded-lg bg-academic-burgundy text-white font-semibold shadow-xs hover:bg-academic-burgundy/90 transition-all disabled:opacity-50"
          >
            {approveLoading ? 'Approving...' : 'Approve & Activate Account'}
          </button>
        </form>
      </div>
    </div>
  );
};
