import React, { useState, useEffect } from 'react';
import api from '../api/client';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import {
  BarChart3,
  Users,
  Calendar,
  BookOpen,
  ShoppingBag,
  TrendingUp,
  Database,
  Layers,
} from 'lucide-react';

export const Analytics = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get('/analytics/overview')
      .then((res) => setData(res.data))
      .catch((err) => console.error('Failed to load analytics', err))
      .finally(() => setLoading(false));
  }, []);

  const PROGRAM_COLORS = ['#4F46E5', '#059669', '#DB2777'];
  const STATUS_COLORS = {
    COMPLETED: '#10B981',
    ACCEPTED: '#3B82F6',
    REQUESTED: '#F59E0B',
    CANCELLED: '#6B7280',
    REJECTED: '#EF4444',
  };

  if (loading) {
    return <div className="py-20 text-center text-xs text-academic-muted">Loading campus analytics...</div>;
  }

  if (!data) {
    return <div className="py-20 text-center text-xs text-academic-muted">Analytics data unavailable.</div>;
  }

  return (
    <div className="space-y-8 py-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-serif font-bold text-academic-primary">Campus Academic Analytics</h1>
        <p className="text-xs text-academic-muted mt-1">
          Live relational aggregation breakdown of student cohorts, learning sessions, and marketplace activity.
        </p>
      </div>

      {/* KPI Highlights */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Active Students', value: data.total_students, sub: 'BTECH / BBA / BDES', icon: Users },
          { label: 'Skills Catalog', value: data.total_skills, sub: 'Accredited Subjects', icon: BookOpen },
          { label: 'Mentoring Sessions', value: data.total_sessions, sub: 'All 5 Lifecycle States', icon: Calendar },
          {
            label: 'Marketplace Volume',
            value: `₹ ${data.marketplace.total_volume.toFixed(0)}`,
            sub: `${data.marketplace.sold_listings} Sold / ${data.marketplace.available_listings} Available`,
            icon: ShoppingBag,
          },
        ].map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div key={idx} className="bg-academic-card border border-academic-border rounded-xl p-5 shadow-xs">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-academic-muted uppercase tracking-wider">{kpi.label}</span>
                <Icon className="w-4 h-4 text-academic-burgundy" />
              </div>
              <p className="text-2xl font-serif font-bold text-academic-primary">{kpi.value}</p>
              <p className="text-[11px] text-academic-muted mt-0.5">{kpi.sub}</p>
            </div>
          );
        })}
      </div>

      {/* Charts Row 1: Program Distribution & Session Status Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Program Breakdown Donut */}
        <div className="bg-academic-card border border-academic-border rounded-2xl p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-academic-border pb-3">
            <div>
              <h3 className="font-serif font-bold text-base text-academic-primary">Cohort Enrollment by Program</h3>
              <p className="text-xs text-academic-muted">SQL Query 27: Program-wise student distribution</p>
            </div>
            <Database className="w-4 h-4 text-academic-muted" />
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.programs}
                  dataKey="student_count"
                  nameKey="program"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={5}
                >
                  {data.programs.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={PROGRAM_COLORS[index % PROGRAM_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value, name, item) => [
                    `${value} students (${item.payload.avg_reputation} avg rep)`,
                    name,
                  ]}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-3 gap-2 text-center text-xs pt-2 border-t border-academic-border/60">
            {data.programs.map((p, idx) => (
              <div key={p.program}>
                <p className="font-semibold text-academic-primary">{p.program}</p>
                <p className="text-academic-muted text-[11px]">{p.student_count} students</p>
                <p className="text-academic-accent text-[10px]">Avg Rep: {p.avg_reputation}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Session Status Distribution */}
        <div className="bg-academic-card border border-academic-border rounded-2xl p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-academic-border pb-3">
            <div>
              <h3 className="font-serif font-bold text-base text-academic-primary">Sessions by Lifecycle Status</h3>
              <p className="text-xs text-academic-muted">SQL Query 28: State machine percentage share</p>
            </div>
            <Calendar className="w-4 h-4 text-academic-muted" />
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.session_statuses}>
                <XAxis dataKey="status" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} />
                <Tooltip formatter={(value, name, item) => [`${value} sessions (${item.payload.percentage_share}%)`, 'Count']} />
                <Bar dataKey="session_count" fill="#7A1C28" radius={[4, 4, 0, 0]}>
                  {data.session_statuses.map((entry) => (
                    <Cell key={`cell-${entry.status}`} fill={STATUS_COLORS[entry.status] || '#7A1C28'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="flex flex-wrap justify-center gap-3 text-xs pt-2 border-t border-academic-border/60">
            {data.session_statuses.map((s) => (
              <span key={s.status} className="text-academic-muted text-[11px]">
                <strong className="text-academic-primary">{s.status}:</strong> {s.session_count} ({s.percentage_share}%)
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Row 2: Top Skills in Demand & Marketplace Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Top Skills */}
        <div className="bg-academic-card border border-academic-border rounded-2xl p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-academic-border pb-3">
            <div>
              <h3 className="font-serif font-bold text-base text-academic-primary">Top Academic Skills in Demand</h3>
              <p className="text-xs text-academic-muted">Ranked by registered student proficiency</p>
            </div>
            <Layers className="w-4 h-4 text-academic-muted" />
          </div>

          <div className="space-y-3">
            {data.top_skills.map((sk, idx) => (
              <div key={sk.skill_id} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="font-semibold text-academic-primary">
                    #{idx + 1} {sk.name}
                  </span>
                  <span className="text-academic-muted">{sk.student_count} students</span>
                </div>
                <div className="w-full bg-academic-secondary h-2.5 rounded-full overflow-hidden">
                  <div
                    className="bg-academic-burgundy h-full rounded-full transition-all duration-500"
                    style={{ width: `${Math.min(100, (sk.student_count / (data.total_students || 1)) * 100 * 2.5)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Marketplace Summary Box */}
        <div className="bg-academic-card border border-academic-border rounded-2xl p-6 shadow-xs space-y-4 flex flex-col justify-between">
          <div className="border-b border-academic-border pb-3">
            <h3 className="font-serif font-bold text-base text-academic-primary">Marketplace Relational Inventory</h3>
            <p className="text-xs text-academic-muted">Transaction integrity & student volume</p>
          </div>

          <div className="grid grid-cols-2 gap-4 text-center">
            <div className="bg-academic-secondary/60 rounded-xl p-4 border border-academic-border">
              <p className="text-2xl font-serif font-bold text-emerald-800">
                {data.marketplace.available_listings}
              </p>
              <p className="text-xs text-academic-muted uppercase tracking-wider mt-1">Available For Purchase</p>
            </div>

            <div className="bg-academic-secondary/60 rounded-xl p-4 border border-academic-border">
              <p className="text-2xl font-serif font-bold text-slate-800">
                {data.marketplace.sold_listings}
              </p>
              <p className="text-xs text-academic-muted uppercase tracking-wider mt-1">Sold Transactions</p>
            </div>

            <div className="col-span-2 bg-academic-burgundy/5 rounded-xl p-4 border border-academic-burgundy/20">
              <p className="text-xs text-academic-muted uppercase tracking-wider">Total Campus GMV Exchanged</p>
              <p className="text-3xl font-serif font-bold text-academic-burgundy mt-1">
                ₹ {data.marketplace.total_volume.toLocaleString()}
              </p>
            </div>
          </div>

          <div className="p-3 bg-academic-secondary/40 rounded-lg text-[11px] text-academic-muted leading-relaxed">
            All marketplace purchases follow atomic conditional updates with concurrency race-condition locks.
          </div>
        </div>
      </div>
    </div>
  );
};
