import React from 'react';

export const ProgramBadge = ({ program }) => {
  const styles = {
    BTECH: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    BBA: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    BDES: 'bg-pink-50 text-pink-700 border-pink-200',
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${styles[program] || 'bg-gray-100 text-gray-700 border-gray-200'}`}>
      {program}
    </span>
  );
};

export const StatusBadge = ({ status }) => {
  const styles = {
    REQUESTED: 'bg-amber-50 text-amber-800 border-amber-200',
    ACCEPTED: 'bg-blue-50 text-blue-800 border-blue-200',
    COMPLETED: 'bg-emerald-50 text-emerald-800 border-emerald-200',
    REJECTED: 'bg-rose-50 text-rose-800 border-rose-200',
    CANCELLED: 'bg-gray-100 text-gray-600 border-gray-200',
    AVAILABLE: 'bg-emerald-50 text-emerald-800 border-emerald-200',
    IN_PROGRESS: 'bg-amber-50 text-amber-900 border-amber-300 font-semibold',
    SOLD: 'bg-slate-100 text-slate-700 border-slate-300',
    REMOVED: 'bg-gray-100 text-gray-500 border-gray-200',
  };

  const label = status === 'IN_PROGRESS' ? 'IN PROGRESS' : status;

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${styles[status] || 'bg-gray-100 text-gray-700 border-gray-200'}`}>
      {label}
    </span>
  );
};

export const ProficiencyBadge = ({ level }) => {
  const styles = {
    BEGINNER: 'bg-slate-50 text-slate-700 border-slate-200',
    INTERMEDIATE: 'bg-sky-50 text-sky-700 border-sky-200',
    ADVANCED: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    EXPERT: 'bg-amber-50 text-amber-800 border-amber-200 font-semibold',
  };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs border ${styles[level] || 'bg-gray-100 text-gray-700'}`}>
      {level}
    </span>
  );
};
