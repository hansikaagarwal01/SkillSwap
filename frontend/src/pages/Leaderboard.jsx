import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { ProgramBadge } from '../components/Badge';
import {
  Award,
  Star,
  Trophy,
  Medal,
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

  const getRankBadge = (rank) => {
    if (rank === 1) {
      return (
        <div className="w-8 h-8 rounded-full bg-amber-100 border border-amber-300 text-amber-800 flex items-center justify-center font-bold text-sm shadow-xs">
          🥇
        </div>
      );
    }
    if (rank === 2) {
      return (
        <div className="w-8 h-8 rounded-full bg-slate-100 border border-slate-300 text-slate-800 flex items-center justify-center font-bold text-sm shadow-xs">
          🥈
        </div>
      );
    }
    if (rank === 3) {
      return (
        <div className="w-8 h-8 rounded-full bg-orange-100 border border-orange-300 text-orange-800 flex items-center justify-center font-bold text-sm shadow-xs">
          🥉
        </div>
      );
    }
    return (
      <span className="font-serif font-bold text-academic-muted text-sm w-8 text-center">
        #{rank}
      </span>
    );
  };

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
        <div className="bg-amber-50 border border-amber-200 rounded-xl px-4 py-2 text-xs text-amber-900 flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-amber-600 shrink-0" />
          <span>
            <strong className="font-semibold">Non-Spendable Metric:</strong> Points represent academic merit and cannot be traded.
          </span>
        </div>
      </div>

      {/* Top 3 Podium Highlights */}
      {!loading && leaderboard.length >= 3 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
          {/* Silver - 2nd */}
          <div className="order-2 md:order-1 bg-academic-card border border-academic-border rounded-2xl p-6 shadow-xs card-hover flex flex-col items-center text-center space-y-3 relative">
            <div className="text-2xl">🥈</div>
            <div className="w-14 h-14 rounded-full bg-slate-200 text-slate-800 flex items-center justify-center font-serif font-bold text-lg">
              {leaderboard[1].name.charAt(0)}
            </div>
            <div>
              <h3 className="font-serif font-bold text-base text-academic-primary">{leaderboard[1].name}</h3>
              <p className="text-xs font-mono text-academic-muted">{leaderboard[1].roll_no}</p>
            </div>
            <ProgramBadge program={leaderboard[1].program} />
            <div className="pt-2 border-t border-academic-border w-full flex justify-around text-xs">
              <div>
                <p className="font-bold text-academic-burgundy font-serif text-lg">{leaderboard[1].reputation_points}</p>
                <p className="text-[10px] text-academic-muted uppercase">Reputation</p>
              </div>
              <div>
                <p className="font-bold text-academic-primary font-serif text-lg">{leaderboard[1].sessions_mentored}</p>
                <p className="text-[10px] text-academic-muted uppercase">Mentored</p>
              </div>
            </div>
          </div>

          {/* Gold - 1st */}
          <div className="order-1 md:order-2 bg-gradient-to-b from-amber-50/80 to-academic-card border-2 border-amber-300 rounded-2xl p-7 shadow-md card-hover flex flex-col items-center text-center space-y-3 relative -translate-y-2">
            <div className="text-3xl">🥇</div>
            <div className="w-16 h-16 rounded-full bg-amber-400 text-amber-950 flex items-center justify-center font-serif font-bold text-2xl shadow-sm">
              {leaderboard[0].name.charAt(0)}
            </div>
            <div>
              <span className="text-[10px] font-bold text-amber-800 uppercase tracking-wider bg-amber-100 px-2 py-0.5 rounded-full">
                Grand Mentor
              </span>
              <h3 className="font-serif font-bold text-lg text-academic-primary mt-1">{leaderboard[0].name}</h3>
              <p className="text-xs font-mono text-academic-muted">{leaderboard[0].roll_no}</p>
            </div>
            <ProgramBadge program={leaderboard[0].program} />
            <div className="pt-2 border-t border-amber-200 w-full flex justify-around text-xs">
              <div>
                <p className="font-bold text-amber-700 font-serif text-2xl">{leaderboard[0].reputation_points}</p>
                <p className="text-[10px] text-academic-muted uppercase">Reputation</p>
              </div>
              <div>
                <p className="font-bold text-academic-primary font-serif text-2xl">{leaderboard[0].sessions_mentored}</p>
                <p className="text-[10px] text-academic-muted uppercase">Mentored</p>
              </div>
            </div>
          </div>

          {/* Bronze - 3rd */}
          <div className="order-3 bg-academic-card border border-academic-border rounded-2xl p-6 shadow-xs card-hover flex flex-col items-center text-center space-y-3 relative">
            <div className="text-2xl">🥉</div>
            <div className="w-14 h-14 rounded-full bg-orange-100 text-orange-900 flex items-center justify-center font-serif font-bold text-lg">
              {leaderboard[2].name.charAt(0)}
            </div>
            <div>
              <h3 className="font-serif font-bold text-base text-academic-primary">{leaderboard[2].name}</h3>
              <p className="text-xs font-mono text-academic-muted">{leaderboard[2].roll_no}</p>
            </div>
            <ProgramBadge program={leaderboard[2].program} />
            <div className="pt-2 border-t border-academic-border w-full flex justify-around text-xs">
              <div>
                <p className="font-bold text-academic-burgundy font-serif text-lg">{leaderboard[2].reputation_points}</p>
                <p className="text-[10px] text-academic-muted uppercase">Reputation</p>
              </div>
              <div>
                <p className="font-bold text-academic-primary font-serif text-lg">{leaderboard[2].sessions_mentored}</p>
                <p className="text-[10px] text-academic-muted uppercase">Mentored</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Leaderboard Table */}
      <div className="bg-academic-card border border-academic-border rounded-2xl shadow-xs overflow-hidden">
        <div className="px-6 py-4 border-b border-academic-border bg-academic-secondary/30 flex justify-between items-center">
          <h3 className="font-serif font-bold text-sm text-academic-primary">Comprehensive Standings (MySQL DENSE_RANK)</h3>
          <span className="text-xs text-academic-muted">Top 30 Mentors</span>
        </div>

        {loading ? (
          <div className="py-20 text-center text-xs text-academic-muted">Loading leaderboard standings...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-academic-secondary/60 text-academic-muted font-semibold uppercase tracking-wider border-b border-academic-border">
                <tr>
                  <th className="px-6 py-3">Rank</th>
                  <th className="px-6 py-3">Student Name</th>
                  <th className="px-6 py-3">Roll Number</th>
                  <th className="px-6 py-3">Program</th>
                  <th className="px-6 py-3 text-right">Reputation</th>
                  <th className="px-6 py-3 text-center">Sessions Mentored</th>
                  <th className="px-6 py-3 text-right">Avg Rating</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-academic-border/60">
                {leaderboard.map((student) => (
                  <tr key={student.roll_no} className="hover:bg-academic-secondary/40 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">{getRankBadge(student.rank)}</td>
                    <td className="px-6 py-4 font-semibold text-academic-primary whitespace-nowrap">
                      {student.name}
                    </td>
                    <td className="px-6 py-4 font-mono text-academic-muted whitespace-nowrap">
                      {student.roll_no}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <ProgramBadge program={student.program} />
                    </td>
                    <td className="px-6 py-4 text-right whitespace-nowrap">
                      <span className="font-bold text-amber-700 font-serif text-sm">
                        ⭐ {student.reputation_points}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center text-academic-primary whitespace-nowrap">
                      {student.sessions_mentored}
                    </td>
                    <td className="px-6 py-4 text-right text-academic-muted whitespace-nowrap">
                      {student.avg_rating ? `★ ${student.avg_rating.toFixed(1)}` : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
