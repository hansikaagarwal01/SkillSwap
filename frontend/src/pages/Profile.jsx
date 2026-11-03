import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { ProgramBadge, ProficiencyBadge } from '../components/Badge';
import { Modal } from '../components/Modal';
import {
  User,
  GraduationCap,
  Star,
  Award,
  BookOpen,
  Briefcase,
  Calendar,
  Plus,
  Edit2,
  Trash2,
  CheckCircle2,
  AlertCircle,
  Clock,
  ShieldCheck,
} from 'lucide-react';

export const Profile = () => {
  const { user, refreshUser } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  // Edit phone modal
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [phone, setPhone] = useState('');
  const [editLoading, setEditLoading] = useState(false);
  const [editError, setEditError] = useState('');

  // Add Experience modal
  const [expModalOpen, setExpModalOpen] = useState(false);
  const [expForm, setExpForm] = useState({
    role_title: '',
    organization: '',
    exp_type: 'INTERNSHIP',
    start_date: '',
    end_date: '',
    description: '',
  });
  const [expLoading, setExpLoading] = useState(false);
  const [expError, setExpError] = useState('');

  // Skill Management Modal state
  const [skillModalOpen, setSkillModalOpen] = useState(false);
  const [editingSkill, setEditingSkill] = useState(null);
  const [catalogSkills, setCatalogSkills] = useState([]);
  const [skillForm, setSkillForm] = useState({
    skill_id: '',
    proficiency_level: 'INTERMEDIATE',
    can_teach: true,
  });
  const [skillLoading, setSkillLoading] = useState(false);
  const [skillError, setSkillError] = useState('');

  const fetchProfile = async () => {
    if (!user) return;
    setLoading(true);
    try {
      const resp = await api.get(`/students/${user.roll_no}`);
      setProfile(resp.data);
      setPhone(resp.data.phone || '');
    } catch (err) {
      console.error('Failed to load profile', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
    api.get('/skills').then((res) => setCatalogSkills(res.data)).catch(() => {});
  }, [user]);

  const openAddSkillModal = () => {
    setEditingSkill(null);
    setSkillForm({
      skill_id: catalogSkills[0]?.skill_id || '',
      proficiency_level: 'INTERMEDIATE',
      can_teach: true,
    });
    setSkillError('');
    setSkillModalOpen(true);
  };

  const openEditSkillModal = (sk) => {
    setEditingSkill(sk);
    setSkillForm({
      skill_id: sk.skill_id,
      proficiency_level: sk.proficiency_level,
      can_teach: sk.can_teach,
    });
    setSkillError('');
    setSkillModalOpen(true);
  };

  const handleSaveSkill = async (e) => {
    e.preventDefault();
    setSkillLoading(true);
    setSkillError('');
    try {
      await api.post(`/students/${user.roll_no}/skills`, {
        skill_id: parseInt(skillForm.skill_id, 10),
        proficiency_level: skillForm.proficiency_level,
        can_teach: Boolean(skillForm.can_teach),
      });
      setSkillModalOpen(false);
      fetchProfile();
    } catch (err) {
      setSkillError(err.response?.data?.error?.message || 'Failed to save skill.');
    } finally {
      setSkillLoading(false);
    }
  };

  const handleDeleteSkill = async (skillId) => {
    if (!window.confirm('Are you sure you want to remove this skill from your profile?')) return;
    try {
      await api.delete(`/students/${user.roll_no}/skills/${skillId}`);
      fetchProfile();
    } catch (err) {
      alert(err.response?.data?.error?.message || 'Failed to remove skill.');
    }
  };

  const handleEditProfile = async (e) => {
    e.preventDefault();
    setEditLoading(true);
    setEditError('');
    try {
      await api.patch(`/students/${user.roll_no}`, {
        phone: phone.trim() || null,
      });
      setEditModalOpen(false);
      fetchProfile();
      refreshUser();
    } catch (err) {
      setEditError(err.response?.data?.error?.message || 'Failed to update profile.');
    } finally {
      setEditLoading(false);
    }
  };

  const handleAddExperience = async (e) => {
    e.preventDefault();
    setExpLoading(true);
    setExpError('');
    try {
      await api.post(`/students/${user.roll_no}/experiences`, {
        ...expForm,
        end_date: expForm.end_date || null,
      });
      setExpModalOpen(false);
      setExpForm({
        role_title: '',
        organization: '',
        exp_type: 'INTERNSHIP',
        start_date: '',
        end_date: '',
        description: '',
      });
      fetchProfile();
    } catch (err) {
      setExpError(err.response?.data?.error?.message || 'Failed to add experience.');
    } finally {
      setExpLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="py-20 text-center space-y-3">
        <p className="text-academic-muted text-sm">Please sign in to view your profile.</p>
      </div>
    );
  }

  if (loading) {
    return <div className="py-20 text-center text-xs text-academic-muted">Loading student profile...</div>;
  }

  return (
    <div className="space-y-8 py-6">
      {/* Profile Card Header */}
      <div className="bg-academic-card border border-academic-border rounded-2xl p-6 sm:p-8 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div className="flex items-start sm:items-center space-x-4">
            <div className="w-16 h-16 rounded-2xl bg-academic-burgundy text-white font-serif font-bold text-2xl flex items-center justify-center shadow-md shrink-0">
              {profile?.name.charAt(0)}
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-2xl font-serif font-bold text-academic-primary">{profile?.name}</h1>
                <ProgramBadge program={profile?.program} />
              </div>
              <p className="text-xs font-mono text-academic-muted mt-0.5">
                {profile?.roll_no} • {profile?.email}
              </p>
              <p className="text-xs text-academic-muted mt-1">
                Department of {profile?.department_name} • Admitted {profile?.admission_year}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="bg-amber-50 border border-amber-200 rounded-xl px-4 py-2.5 text-center">
              <span className="text-[10px] font-semibold text-amber-800 uppercase tracking-wider block">
                Reputation Points
              </span>
              <span className="font-serif font-bold text-2xl text-amber-900 flex items-center justify-center space-x-1">
                <Star className="w-4 h-4 fill-amber-400 text-amber-500" />
                <span>{profile?.reputation_points}</span>
              </span>
            </div>

            <button
              onClick={() => setEditModalOpen(true)}
              className="p-2.5 rounded-xl border border-academic-border bg-academic-secondary hover:bg-academic-border/60 text-academic-primary transition-colors flex items-center space-x-1 text-xs font-semibold"
            >
              <Edit2 className="w-3.5 h-3.5" />
              <span>Edit Details</span>
            </button>
          </div>
        </div>

        {/* Universal Roll_No Immutability Notice */}
        <div className="mt-6 pt-4 border-t border-academic-border/70 flex items-center space-x-2 text-[11px] text-academic-muted font-mono">
          <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>Universal Primary Key: {profile?.roll_no} (Immutable by academic protocol)</span>
        </div>
      </div>

      {/* Two Columns: Skills Portfolio & Experience Timeline */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Skills Portfolio */}
        <div className="bg-academic-card border border-academic-border rounded-2xl p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-academic-border pb-3">
            <div className="flex items-center space-x-2">
              <BookOpen className="w-4 h-4 text-academic-burgundy" />
              <h3 className="font-serif font-bold text-base text-academic-primary">Verified Skills</h3>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-xs text-academic-muted">{profile?.skills?.length || 0} Listed</span>
              <button
                type="button"
                onClick={openAddSkillModal}
                className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-md bg-academic-burgundy text-white text-xs font-semibold hover:bg-academic-burgundy/90 transition-colors shadow-xs"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Skill</span>
              </button>
            </div>
          </div>

          {profile?.skills?.length === 0 ? (
            <p className="text-xs text-academic-muted py-6 text-center">No skills registered yet.</p>
          ) : (
            <div className="space-y-2.5">
              {profile?.skills?.map((sk) => (
                <div
                  key={sk.skill_id}
                  className="flex items-center justify-between p-3 rounded-lg border border-academic-border bg-academic-secondary/40 text-xs"
                >
                  <div>
                    <p className="font-semibold text-academic-primary">{sk.skill_name}</p>
                    <p className="text-[10px] text-academic-muted uppercase">{sk.category}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    {sk.can_teach && (
                      <span className="text-[10px] font-semibold bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded">
                        Mentor
                      </span>
                    )}
                    <ProficiencyBadge level={sk.proficiency_level} />
                    <button
                      type="button"
                      onClick={() => openEditSkillModal(sk)}
                      className="p-1 text-academic-muted hover:text-academic-primary hover:bg-academic-secondary rounded transition-colors"
                      title="Edit skill or toggle mentor availability"
                    >
                      <Edit2 className="w-3.5 h-3.5" />
                    </button>
                    <button
                      type="button"
                      onClick={() => handleDeleteSkill(sk.skill_id)}
                      className="p-1 text-academic-muted hover:text-rose-600 hover:bg-rose-50 rounded transition-colors"
                      title="Remove skill"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Desired Skills to Learn */}
          <div className="pt-4 border-t border-academic-border space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-semibold text-academic-primary uppercase tracking-wider">
                Desired Learning Goals ({profile?.desired_skills?.length || 0})
              </h4>
              <span className="text-[10px] text-academic-muted">Survey Recorded</span>
            </div>
            {profile?.desired_skills?.length === 0 ? (
              <p className="text-xs text-academic-muted py-2 text-center">No desired skills listed yet.</p>
            ) : (
              <div className="flex flex-wrap gap-1.5">
                {profile?.desired_skills?.map((ds) => (
                  <span
                    key={ds.skill_id}
                    className="bg-amber-50/80 text-amber-900 border border-amber-200/80 px-2.5 py-1 rounded-md text-xs font-medium"
                  >
                    {ds.skill_name}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Experience Portfolio */}
        <div className="bg-academic-card border border-academic-border rounded-2xl p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-academic-border pb-3">
            <div className="flex items-center space-x-2">
              <Briefcase className="w-4 h-4 text-academic-burgundy" />
              <h3 className="font-serif font-bold text-base text-academic-primary">Academic Experience</h3>
            </div>
            <button
              onClick={() => setExpModalOpen(true)}
              className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-md bg-academic-burgundy text-white text-xs font-semibold hover:bg-academic-burgundy/90 transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add</span>
            </button>
          </div>

          {profile?.experiences?.length === 0 ? (
            <p className="text-xs text-academic-muted py-6 text-center">
              No internships or projects listed yet. Click Add to showcase your portfolio.
            </p>
          ) : (
            <div className="space-y-3">
              {profile?.experiences?.map((exp) => (
                <div key={exp.exp_no} className="p-3.5 rounded-lg border border-academic-border bg-academic-secondary/30 space-y-1 text-xs">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-semibold text-academic-primary">{exp.role_title}</h4>
                      <p className="text-academic-muted font-medium">{exp.organization}</p>
                    </div>
                    <span className="text-[10px] font-semibold uppercase tracking-wider bg-academic-secondary px-2 py-0.5 rounded border border-academic-border">
                      {exp.exp_type}
                    </span>
                  </div>

                  <p className="text-[11px] text-academic-muted flex items-center space-x-1">
                    <Calendar className="w-3 h-3" />
                    <span>
                      {exp.start_date} to {exp.end_date || 'Present'}
                    </span>
                  </p>

                  {exp.description && (
                    <p className="text-academic-muted pt-1 text-[11px] leading-relaxed">
                      {exp.description}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Edit Details Modal */}
      <Modal isOpen={editModalOpen} onClose={() => setEditModalOpen(false)} title="Update Contact Information">
        <form onSubmit={handleEditProfile} className="space-y-4 text-xs">
          {editError && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg">
              {editError}
            </div>
          )}

          <div>
            <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
              Roll Number (Universal PK - Immutable)
            </label>
            <input
              type="text"
              disabled
              value={profile?.roll_no}
              className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-secondary text-academic-muted font-mono cursor-not-allowed"
            />
          </div>

          <div>
            <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
              Phone Number
            </label>
            <input
              type="tel"
              placeholder="9829011001"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
            />
          </div>

          <div className="pt-2 flex justify-end space-x-2">
            <button
              type="button"
              onClick={() => setEditModalOpen(false)}
              className="px-4 py-2 rounded-lg border border-academic-border bg-academic-card text-academic-muted hover:bg-academic-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={editLoading}
              className="px-4 py-2 rounded-lg bg-academic-burgundy text-white font-semibold shadow-xs hover:bg-academic-burgundy/90 disabled:opacity-50"
            >
              {editLoading ? 'Saving...' : 'Update Details'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Add Experience Modal */}
      <Modal isOpen={expModalOpen} onClose={() => setExpModalOpen(false)} title="Add Academic Experience / Project">
        <form onSubmit={handleAddExperience} className="space-y-4 text-xs">
          {expError && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg">
              {expError}
            </div>
          )}

          <div>
            <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
              Role Title *
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Full Stack Intern / Lead Architect"
              value={expForm.role_title}
              onChange={(e) => setExpForm({ ...expForm, role_title: e.target.value })}
              className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
                Organization / Lab *
              </label>
              <input
                type="text"
                required
                placeholder="e.g. JKLU AI Lab"
                value={expForm.organization}
                onChange={(e) => setExpForm({ ...expForm, organization: e.target.value })}
                className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
              />
            </div>

            <div>
              <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
                Experience Type *
              </label>
              <select
                value={expForm.exp_type}
                onChange={(e) => setExpForm({ ...expForm, exp_type: e.target.value })}
                className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
              >
                <option value="INTERNSHIP">Internship</option>
                <option value="PROJECT">Academic Project</option>
                <option value="HACKATHON">Hackathon</option>
                <option value="ACHIEVEMENT">Academic Award</option>
                <option value="OTHER">Other</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
                Start Date *
              </label>
              <input
                type="date"
                required
                value={expForm.start_date}
                onChange={(e) => setExpForm({ ...expForm, start_date: e.target.value })}
                className="w-full p-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
              />
            </div>

            <div>
              <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
                End Date (Leave blank if ongoing)
              </label>
              <input
                type="date"
                value={expForm.end_date}
                onChange={(e) => setExpForm({ ...expForm, end_date: e.target.value })}
                className="w-full p-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
              />
            </div>
          </div>

          <div>
            <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
              Description / Responsibilities
            </label>
            <textarea
              rows={3}
              placeholder="Key technologies used, quantitative impact, or research contributions..."
              value={expForm.description}
              onChange={(e) => setExpForm({ ...expForm, description: e.target.value })}
              className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
            />
          </div>

          <div className="pt-2 flex justify-end space-x-2">
            <button
              type="button"
              onClick={() => setExpModalOpen(false)}
              className="px-4 py-2 rounded-lg border border-academic-border bg-academic-card text-academic-muted hover:bg-academic-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={expLoading}
              className="px-4 py-2 rounded-lg bg-academic-burgundy text-white font-semibold shadow-xs hover:bg-academic-burgundy/90 disabled:opacity-50"
            >
              {expLoading ? 'Saving...' : 'Add to Portfolio'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Add / Edit Skill Modal */}
      <Modal
        isOpen={skillModalOpen}
        onClose={() => setSkillModalOpen(false)}
        title={editingSkill ? `Edit Skill: ${editingSkill.skill_name}` : 'Add Skill to Profile'}
      >
        <form onSubmit={handleSaveSkill} className="space-y-4 text-xs">
          {skillError && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg">
              {skillError}
            </div>
          )}

          <div>
            <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
              Skill *
            </label>
            {editingSkill ? (
              <div className="p-2.5 rounded-lg border border-academic-border bg-academic-secondary/60 text-academic-primary font-semibold">
                {editingSkill.skill_name} ({editingSkill.category})
              </div>
            ) : (
              <select
                required
                value={skillForm.skill_id}
                onChange={(e) => setSkillForm({ ...skillForm, skill_id: e.target.value })}
                className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy font-medium"
              >
                <option value="" disabled>Select a skill from catalog...</option>
                {catalogSkills.map((sk) => (
                  <option key={sk.skill_id} value={sk.skill_id}>
                    {sk.name} — {sk.category}
                  </option>
                ))}
              </select>
            )}
          </div>

          <div>
            <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
              Proficiency Level *
            </label>
            <select
              value={skillForm.proficiency_level}
              onChange={(e) => setSkillForm({ ...skillForm, proficiency_level: e.target.value })}
              className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
            >
              <option value="BEGINNER">BEGINNER</option>
              <option value="INTERMEDIATE">INTERMEDIATE</option>
              <option value="ADVANCED">ADVANCED</option>
              <option value="EXPERT">EXPERT</option>
            </select>
          </div>

          <div className="p-3 rounded-lg border border-academic-border bg-academic-secondary/40 space-y-1">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={skillForm.can_teach}
                onChange={(e) => setSkillForm({ ...skillForm, can_teach: e.target.checked })}
                className="w-4 h-4 text-academic-burgundy rounded border-academic-border focus:ring-academic-burgundy"
              />
              <span className="font-semibold text-academic-primary">Available to mentor peers (Can Teach)</span>
            </label>
            <p className="text-[11px] text-academic-muted pl-6">
              Checking this allows classmates to find you in the Mentors directory and request 1-on-1 peer sessions with you.
            </p>
          </div>

          <div className="pt-2 flex justify-end space-x-2">
            <button
              type="button"
              onClick={() => setSkillModalOpen(false)}
              className="px-4 py-2 rounded-lg border border-academic-border bg-academic-card text-academic-muted hover:bg-academic-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={skillLoading || (!editingSkill && !skillForm.skill_id)}
              className="px-4 py-2 rounded-lg bg-academic-burgundy text-white font-semibold shadow-xs hover:bg-academic-burgundy/90 disabled:opacity-50"
            >
              {skillLoading ? 'Saving...' : editingSkill ? 'Update Skill' : 'Add Skill'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
