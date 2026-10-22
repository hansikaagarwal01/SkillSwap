import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Modal } from '../components/Modal';
import {
  BookOpen,
  Search,
  Plus,
  Users,
  CheckCircle2,
  Sparkles,
  Layers,
} from 'lucide-react';

export const Skills = () => {
  const { user } = useAuth();
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [search, setSearch] = useState('');

  // Add Skill Modal
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [newSkill, setNewSkill] = useState({ name: '', category: 'Computer Science', description: '' });
  const [createLoading, setCreateLoading] = useState(false);
  const [createError, setCreateError] = useState('');

  // Add to My Skills Modal
  const [addMySkillModalOpen, setAddMySkillModalOpen] = useState(false);
  const [targetSkill, setTargetSkill] = useState(null);
  const [mySkillForm, setMySkillForm] = useState({ proficiency_level: 'INTERMEDIATE', can_teach: true });
  const [mySkillLoading, setMySkillLoading] = useState(false);
  const [mySkillSuccess, setMySkillSuccess] = useState('');
  const [mySkillError, setMySkillError] = useState('');

  const fetchSkills = async () => {
    setLoading(true);
    try {
      const resp = await api.get('/skills');
      setSkills(resp.data);
    } catch (err) {
      console.error('Failed to load skills', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSkills();
  }, []);

  const categories = ['ALL', ...new Set(skills.map((s) => s.category))];

  const filteredSkills = skills.filter((s) => {
    const matchesCategory = selectedCategory === 'ALL' || s.category === selectedCategory;
    const matchesSearch =
      s.name.toLowerCase().includes(search.toLowerCase()) ||
      (s.description && s.description.toLowerCase().includes(search.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  const handleCreateSkill = async (e) => {
    e.preventDefault();
    setCreateLoading(true);
    setCreateError('');
    try {
      await api.post('/skills', newSkill);
      setCreateModalOpen(false);
      setNewSkill({ name: '', category: 'Computer Science', description: '' });
      fetchSkills();
    } catch (err) {
      setCreateError(err.response?.data?.error?.message || 'Failed to add new skill.');
    } finally {
      setCreateLoading(false);
    }
  };

  const openAddMySkillModal = (skill) => {
    setTargetSkill(skill);
    setMySkillForm({ proficiency_level: 'INTERMEDIATE', can_teach: true });
    setMySkillError('');
    setMySkillSuccess('');
    setAddMySkillModalOpen(true);
  };

  const handleAddMySkillSubmit = async (e) => {
    e.preventDefault();
    setMySkillLoading(true);
    setMySkillError('');
    setMySkillSuccess('');

    try {
      await api.post(`/students/${user.roll_no}/skills`, {
        skill_id: targetSkill.skill_id,
        proficiency_level: mySkillForm.proficiency_level,
        can_teach: mySkillForm.can_teach,
      });
      setMySkillSuccess(`Added ${targetSkill.name} to your academic skill profile!`);
      setTimeout(() => {
        setAddMySkillModalOpen(false);
      }, 1500);
    } catch (err) {
      setMySkillError(err.response?.data?.error?.message || 'Failed to update student skills.');
    } finally {
      setMySkillLoading(false);
    }
  };

  return (
    <div className="space-y-8 py-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-serif font-bold text-academic-primary">Skills & Talents Catalog</h1>
          <p className="text-xs text-academic-muted mt-1">
            Explore academic competencies, music, dance, fine arts, photography, sports, and creative talents across JKLU.
          </p>
        </div>

        <button
          onClick={() => setCreateModalOpen(true)}
          className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-lg bg-academic-burgundy text-white font-semibold text-xs shadow-xs hover:bg-academic-burgundy/90 transition-all self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Register New Skill</span>
        </button>
      </div>

      {/* Filter and Search */}
      <div className="bg-academic-card border border-academic-border rounded-xl p-4 shadow-xs space-y-4">
        <div className="relative">
          <input
            type="text"
            placeholder="Search skill catalog by name or domain keywords..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-8 pr-3 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary text-xs placeholder:text-academic-muted/50 focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
          />
          <Search className="absolute left-2.5 top-2.5 w-3.5 h-3.5 text-academic-muted" />
        </div>

        {/* Category Pills */}
        <div className="flex flex-wrap gap-1.5 pt-1">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                selectedCategory === cat
                  ? 'bg-academic-burgundy text-white shadow-xs'
                  : 'bg-academic-secondary text-academic-muted hover:text-academic-primary hover:bg-academic-border/50'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Skills Grid */}
      {loading ? (
        <div className="py-20 text-center text-xs text-academic-muted">Loading skills catalog...</div>
      ) : filteredSkills.length === 0 ? (
        <div className="py-20 text-center bg-academic-card border border-academic-border rounded-xl p-8 space-y-2">
          <Layers className="w-10 h-10 text-academic-muted mx-auto" />
          <p className="font-serif font-bold text-base text-academic-primary">No skills found</p>
          <p className="text-xs text-academic-muted">Try a different keyword or create this skill.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredSkills.map((sk) => (
            <div
              key={sk.skill_id}
              className="bg-academic-card border border-academic-border rounded-xl p-5 shadow-xs card-hover flex flex-col justify-between space-y-4"
            >
              <div className="space-y-2">
                <div className="flex items-start justify-between">
                  <span className="text-[10px] font-semibold text-academic-accent uppercase tracking-wider bg-academic-secondary px-2 py-0.5 rounded border border-academic-border">
                    {sk.category}
                  </span>
                  <span className="font-mono text-[10px] text-academic-muted">ID: #{sk.skill_id}</span>
                </div>

                <h3 className="font-serif font-bold text-base text-academic-primary">{sk.name}</h3>

                <p className="text-xs text-academic-muted leading-relaxed line-clamp-2">
                  {sk.description || 'Core academic competency registered in university curriculum.'}
                </p>
              </div>

              {user && (
                <div className="pt-2 border-t border-academic-border/60">
                  <button
                    onClick={() => openAddMySkillModal(sk)}
                    className="w-full py-1.5 rounded-lg border border-academic-border bg-academic-secondary/60 hover:bg-academic-secondary text-academic-primary text-xs font-semibold transition-colors flex items-center justify-center space-x-1"
                  >
                    <Plus className="w-3.5 h-3.5 text-academic-burgundy" />
                    <span>Add to My Profile</span>
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Suggest Skill Modal */}
      <Modal isOpen={createModalOpen} onClose={() => setCreateModalOpen(false)} title="Register Academic Skill">
        <form onSubmit={handleCreateSkill} className="space-y-4 text-xs">
          {createError && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg">
              {createError}
            </div>
          )}

          <div>
            <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
              Skill Name *
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Distributed Systems & Raft Consensus"
              value={newSkill.name}
              onChange={(e) => setNewSkill({ ...newSkill, name: e.target.value })}
              className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
            />
          </div>

          <div>
            <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
              Skill Domain / Category *
            </label>
            <select
              value={newSkill.category}
              onChange={(e) => setNewSkill({ ...newSkill, category: e.target.value })}
              className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy font-medium"
            >
              <option value="Computer Science">Computer Science & Programming</option>
              <option value="Design">Design & UI/UX</option>
              <option value="Business">Business & Management</option>
              <option value="Music & Performing Arts">Music & Performing Arts (Guitar, Vocals, Production)</option>
              <option value="Dance & Performing Arts">Dance & Performing Arts (Western, Classical, Hip-Hop)</option>
              <option value="Fine Arts & Visual Media">Fine Arts & Visual Media (Sketching, Painting, Photography)</option>
              <option value="Literary & Creative Arts">Literary & Creative Arts (Poetry, Creative Writing)</option>
              <option value="Sports & Strategy">Sports & Strategy (Chess, Tactics)</option>
              <option value="Communication">Communication & Public Speaking</option>
              <option value="Electronics">Electronics & Hardware</option>
            </select>
          </div>

          <div>
            <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
              Skill Scope / Learning Description
            </label>
            <textarea
              rows={3}
              placeholder="Brief description of learning objectives..."
              value={newSkill.description}
              onChange={(e) => setNewSkill({ ...newSkill, description: e.target.value })}
              className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
            />
          </div>

          <div className="pt-2 flex justify-end space-x-2">
            <button
              type="button"
              onClick={() => setCreateModalOpen(false)}
              className="px-4 py-2 rounded-lg border border-academic-border bg-academic-card text-academic-muted hover:bg-academic-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createLoading}
              className="px-4 py-2 rounded-lg bg-academic-burgundy text-white font-semibold shadow-xs hover:bg-academic-burgundy/90 disabled:opacity-50"
            >
              {createLoading ? 'Registering...' : 'Register Skill'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Add To My Skills Modal */}
      <Modal
        isOpen={addMySkillModalOpen}
        onClose={() => setAddMySkillModalOpen(false)}
        title={`Add "${targetSkill?.name}" to Your Skills`}
      >
        <form onSubmit={handleAddMySkillSubmit} className="space-y-4 text-xs">
          {mySkillError && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg">
              {mySkillError}
            </div>
          )}

          {mySkillSuccess && (
            <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>{mySkillSuccess}</span>
            </div>
          )}

          <div>
            <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
              Your Proficiency Level *
            </label>
            <select
              value={mySkillForm.proficiency_level}
              onChange={(e) => setMySkillForm({ ...mySkillForm, proficiency_level: e.target.value })}
              className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
            >
              <option value="BEGINNER">BEGINNER (Fundamentals)</option>
              <option value="INTERMEDIATE">INTERMEDIATE (Course Projects Completed)</option>
              <option value="ADVANCED">ADVANCED (Internship / Advanced Lab)</option>
              <option value="EXPERT">EXPERT (Hackathon Winner / Research Level)</option>
            </select>
          </div>

          <div className="flex items-center space-x-3 p-3 bg-academic-secondary/60 rounded-lg border border-academic-border">
            <input
              type="checkbox"
              id="can_teach"
              checked={mySkillForm.can_teach}
              onChange={(e) => setMySkillForm({ ...mySkillForm, can_teach: e.target.checked })}
              className="w-4 h-4 text-academic-burgundy rounded border-academic-border focus:ring-academic-burgundy"
            />
            <label htmlFor="can_teach" className="cursor-pointer">
              <p className="font-semibold text-academic-primary">I can teach this to peers</p>
              <p className="text-[11px] text-academic-muted">
                Listing yourself as a mentor allows peers to book sessions with you and boosts your discoverability.
              </p>
            </label>
          </div>

          <div className="pt-2 flex justify-end space-x-2">
            <button
              type="button"
              onClick={() => setAddMySkillModalOpen(false)}
              className="px-4 py-2 rounded-lg border border-academic-border bg-academic-card text-academic-muted hover:bg-academic-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={mySkillLoading}
              className="px-4 py-2 rounded-lg bg-academic-burgundy text-white font-semibold shadow-xs hover:bg-academic-burgundy/90 disabled:opacity-50"
            >
              {mySkillLoading ? 'Saving...' : 'Save to Profile'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
