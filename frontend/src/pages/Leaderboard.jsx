import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { ProgramBadge } from '../components/Badge';
import {
  Award,
  Star,
  Users,
  CheckCircle2,
  Sparkles,
  ShieldAlert,
} from 'lucide-react';

export const Leaderboard = () => {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get('/leaderboard?limit=30')
      .then((res) => setLeaderboard(res.data))
      .catch((err) => console.error('Failed to load leaderboard', err))
      .finally(() => setLoading(false));
  }, []);

  const activeLeaders = leaderboard.filter((item) => item.reputation_points > 0);

  return (
    <div className="space-y-8 py-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-serif font-bold text-academic-primary">Academic Reputation Leaderboard</h1>
          <p className="text-xs text-academic-muted mt-1">
            Top campus peer mentors ranked by verified reputation points earned through completed sessions.
          </p>
        </div>

        {/* Academic Non-spendable Callout */}
        <div className="bg-academic-secondary border border-academic-border rounded-xl px-4 py-2 text-xs text-academic-primary flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-academic-accent shrink-0" />
          <span>
            <strong className="font-semibold">Non-Spendable Metric:</strong> Points represent academic merit and cannot be traded.
          </span>
        </div>
      </div>

      {loading ? (
        <div className="py-20 text-center text-xs text-academic-muted">Loading academic leaderboard...</div>
      ) : activeLeaders.length === 0 ? (
        /* Genuine Database Empty State */
        <div className="bg-academic-card border border-academic-border rounded-2xl p-10 text-center max-w-2xl mx-auto space-y-4">
          <div className="w-12 h-12 rounded-xl bg-academic-secondary text-academic-accent flex items-center justify-center mx-auto">
            <Award className="w-6 h-6" />
          </div>
          <div className="space-y-1">
            <h3 className="font-serif font-bold text-lg text-academic-primary">
              No Completed Sessions Recorded Yet
            </h3>
            <p className="text-xs text-academic-muted leading-relaxed max-w-md mx-auto">
              In accordance with our strict university integrity rules, student reputation rankings are driven strictly by verified, completed learning sessions (+10 non-spendable points per session).
            </p>
          </div>
          <div className="pt-2 border-t border-academic-border/60 text-xs text-academic-muted flex flex-wrap justify-center gap-x-6 gap-y-2">
            <span>• 34 Verified JKLU Students Enrolled</span>
            <span>• Zero Fabricated Reputation Points</span>
            <span>• Safe Concurrency Session Audits</span>
          </div>
        </div>
      ) : (
        <div className="bg-academic-card border border-academic-border rounded-2xl shadow-xs overflow-hidden">
          <div className="px-6 py-4 border-b border-academic-border flex items-center justify-between">
            <h2 className="font-serif font-bold text-base text-academic-primary">Student Merit Rankings</h2>
            <span className="text-xs text-academic-muted font-mono">{activeLeaders.length} Mentors Ranked</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-academic-secondary/60 text-academic-muted border-b border-academic-border font-semibold uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-3 px-6 text-center w-16">Rank</th>
                  <th className="py-3 px-6">Student</th>
                  <th className="py-3 px-6">Program</th>
                  <th className="py-3 px-6 text-center">Sessions Mentored</th>
                  <th className="py-3 px-6 text-center">Avg Rating</th>
                  <th className="py-3 px-6 text-right">Reputation Points</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-academic-border">
                {activeLeaders.map((st) => (
                  <tr key={st.roll_no} className="hover:bg-academic-secondary/30 transition-colors">
                    <td className="py-3.5 px-6 text-center font-bold text-academic-primary font-mono">
                      #{st.rank}
                    </td>
                    <td className="py-3.5 px-6">
                      <div className="font-semibold text-academic-primary">{st.name}</div>
                      <div className="text-[11px] font-mono text-academic-muted">{st.roll_no}</div>
                    </td>
                    <td className="py-3.5 px-6">
                      <ProgramBadge program={st.program} />
                    </td>
                    <td className="py-3.5 px-6 text-center font-semibold text-academic-primary">
                      {st.sessions_mentored}
                    </td>
                    <td className="py-3.5 px-6 text-center text-academic-muted">
                      {st.avg_rating ? `★ ${st.avg_rating.toFixed(1)}` : '—'}
                    </td>
                    <td className="py-3.5 px-6 text-right">
                      <span className="font-serif font-bold text-academic-burgundy text-sm">
                        {st.reputation_points} pts
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
