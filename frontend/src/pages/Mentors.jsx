import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { ProgramBadge, ProficiencyBadge } from '../components/Badge';
import { Modal } from '../components/Modal';
import { Pagination } from '../components/Pagination';
import {
  Users,
  Search,
  Filter,
  Star,
  BookOpen,
  Calendar,
  Sparkles,
  CheckCircle2,
  Clock,
  ExternalLink,
  Music,
  Palette,
  Activity,
  Code,
  Briefcase,
  Layers,
} from 'lucide-react';

export const Mentors = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [mentors, setMentors] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filter states
  const [skillsList, setSkillsList] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [selectedSkill, setSelectedSkill] = useState('');
  const [selectedProgram, setSelectedProgram] = useState('');
  const [minRating, setMinRating] = useState('');
  const [search, setSearch] = useState('');

  // Request Modal state
  const [requestModalOpen, setRequestModalOpen] = useState(false);
  const [selectedMentor, setSelectedMentor] = useState(null);
  const [mentorSkills, setMentorSkills] = useState([]);
  const [requestData, setRequestData] = useState({
    skill_id: '',
    topic: '',
    mode: 'ONLINE',
    scheduled_at: '',
    meeting_link: '',
  });
  const [requestLoading, setRequestLoading] = useState(false);
  const [requestSuccess, setRequestSuccess] = useState('');
  const [requestError, setRequestError] = useState('');

  // Fetch skills catalog for filter dropdown
  useEffect(() => {
    api
      .get('/skills')
      .then((res) => setSkillsList(res.data))
      .catch((err) => console.error('Failed to fetch skills catalog', err));
  }, []);

  // Fetch mentors with filters
  const fetchMentors = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('page', page);
      params.append('page_size', 9);
      if (selectedSkill) params.append('skill_id', selectedSkill);
      if (selectedProgram) params.append('program', selectedProgram);
      if (minRating) params.append('min_rating', minRating);
      if (search) {
        params.append('q', search);
      } else if (selectedCategory && selectedCategory !== 'ALL') {
        params.append('q', selectedCategory);
      }

      const resp = await api.get(`/mentors?${params.toString()}`);
      setMentors(resp.data.items);
      setTotal(resp.data.total);
      setTotalPages(resp.data.total_pages);
    } catch (err) {
      console.error('Failed to load mentors', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMentors();
  }, [page, selectedCategory, selectedSkill, selectedProgram, minRating]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchMentors();
  };

  const handleCategorySelect = (category) => {
    setSelectedCategory(category);
    setSelectedSkill('');
    setPage(1);
  };

  const openRequestModal = async (mentor) => {
    if (!user) {
      navigate('/login');
      return;
    }

    setSelectedMentor(mentor);
    const initialSkillId = mentor.skill_id;
    setRequestData({
      skill_id: initialSkillId,
      topic: '',
      mode: 'ONLINE',
      scheduled_at: new Date(Date.now() + 86400000 * 2).toISOString().slice(0, 16),
      meeting_link: 'https://meet.google.com/abc-defg-hij',
    });
    setMentorSkills([
      {
        skill_id: mentor.skill_id,
        skill_name: mentor.skill_name,
        proficiency_level: mentor.proficiency_level,
      },
    ]);
    setRequestError('');
    setRequestSuccess('');
    setRequestModalOpen(true);

    // Fetch all teachable skills for this mentor so the learner can pick any
    try {
      const res = await api.get(`/students/${mentor.roll_no}/skills`);
      const teachable = res.data.filter((s) => s.can_teach);
      if (teachable.length > 0) {
        setMentorSkills(teachable);
      }
    } catch (e) {
      // Keep initial single skill
    }
  };

  const handleRequestSubmit = async (e) => {
    e.preventDefault();
    setRequestLoading(true);
    setRequestError('');
    setRequestSuccess('');

    const parsedSkillId = parseInt(requestData.skill_id, 10);
    if (!parsedSkillId || isNaN(parsedSkillId)) {
      setRequestError('Please select a valid skill for mentorship.');
      setRequestLoading(false);
      return;
    }

    try {
      const payload = {
        mentor_roll_no: selectedMentor.roll_no,
        skill_id: parsedSkillId,
        topic: requestData.topic.trim(),
        mode: requestData.mode,
        scheduled_at: new Date(requestData.scheduled_at).toISOString(),
        meeting_link: requestData.mode === 'ONLINE' ? requestData.meeting_link : null,
      };

      await api.post('/sessions', payload);
      setRequestSuccess('Mentorship session requested successfully! Mentor notified.');
      setTimeout(() => {
        setRequestModalOpen(false);
        navigate('/sessions');
      }, 1500);
    } catch (err) {
      const msg = err.response?.data?.error?.message || 'Failed to submit request.';
      setRequestError(msg);
    } finally {
      setRequestLoading(false);
    }
  };

  // Derive categories from skills list
  const categories = ['ALL', ...new Set(skillsList.map((s) => s.category).filter(Boolean))];

  // Scoped skills for dropdown
  const filteredSkillsList =
    selectedCategory === 'ALL'
      ? skillsList
      : skillsList.filter((s) => s.category === selectedCategory);

  return (
    <div className="space-y-8 py-6">
      {/* Header & Filter Bar */}
      <div className="space-y-4">
        <div>
          <h1 className="text-3xl font-serif font-bold text-academic-primary">Verified Peer Mentors</h1>
          <p className="text-xs text-academic-muted mt-1">
            Connect 1-on-1 with verified campus mentors across technical subjects, guitar, dance, fine arts, photography, and creative passions. 100% free of cost.
          </p>
        </div>

        {/* Category Filter Pills */}
        <div className="flex items-center space-x-2 overflow-x-auto pb-1 scrollbar-none text-xs">
          {categories.map((cat) => {
            const isSelected = selectedCategory === cat;
            return (
              <button
                key={cat}
                type="button"
                onClick={() => handleCategorySelect(cat)}
                className={`px-3 py-1.5 rounded-full border font-medium whitespace-nowrap transition-all ${
                  isSelected
                    ? 'bg-academic-burgundy text-white border-academic-burgundy shadow-xs'
                    : 'bg-academic-card text-academic-muted border-academic-border hover:bg-academic-secondary hover:text-academic-primary'
                }`}
              >
                {cat === 'ALL' ? '🌟 All Domains' : cat}
              </button>
            );
          })}
        </div>

        {/* Search & Fine Controls */}
        <div className="bg-academic-card border border-academic-border rounded-xl p-4 shadow-xs space-y-3">
          <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3 text-xs">
            {/* Search */}
            <div className="relative sm:col-span-2">
              <input
                type="text"
                placeholder="Search mentor by name, roll no, or skill (e.g. Guitar, Python)..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-8 pr-3 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary placeholder:text-academic-muted/50 focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
              />
              <Search className="absolute left-2.5 top-2.5 w-3.5 h-3.5 text-academic-muted" />
            </div>

            {/* Skill dropdown */}
            <div>
              <select
                value={selectedSkill}
                onChange={(e) => {
                  setSelectedSkill(e.target.value);
                  setPage(1);
                }}
                className="w-full px-2.5 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
              >
                <option value="">All Skills ({filteredSkillsList.length})</option>
                {filteredSkillsList.map((sk) => (
                  <option key={sk.skill_id} value={sk.skill_id}>
                    {sk.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Program dropdown */}
            <div>
              <select
                value={selectedProgram}
                onChange={(e) => {
                  setSelectedProgram(e.target.value);
                  setPage(1);
                }}
                className="w-full px-2.5 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
              >
                <option value="">All Programs</option>
                <option value="BTECH">B.Tech</option>
                <option value="BBA">BBA</option>
                <option value="BDES">B.Des</option>
              </select>
            </div>

            {/* Rating Filter */}
            <div>
              <select
                value={minRating}
                onChange={(e) => {
                  setMinRating(e.target.value);
                  setPage(1);
                }}
                className="w-full px-2.5 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
              >
                <option value="">Any Rating</option>
                <option value="4.5">★ 4.5 & above</option>
                <option value="4.0">★ 4.0 & above</option>
              </select>
            </div>
          </form>
        </div>
      </div>

      {/* Mentor Cards Grid */}
      {loading ? (
        <div className="py-20 text-center text-xs text-academic-muted">Loading verified peer mentors...</div>
      ) : mentors.length === 0 ? (
        <div className="py-20 text-center bg-academic-card border border-academic-border rounded-xl p-8 space-y-2">
          <Users className="w-10 h-10 text-academic-muted mx-auto" />
          <p className="font-serif font-bold text-base text-academic-primary">No mentors matched your filter</p>
          <p className="text-xs text-academic-muted">Try resetting search criteria or choosing a different skill or domain.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {mentors.map((mentor) => (
            <div
              key={`${mentor.roll_no}-${mentor.skill_id}`}
              className="bg-academic-card border border-academic-border rounded-xl p-6 shadow-xs card-hover flex flex-col justify-between space-y-4"
            >
              <div>
                {/* Header */}
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-11 h-11 rounded-full bg-academic-burgundy text-white font-serif font-bold flex items-center justify-center text-base shadow-xs">
                      {mentor.name.charAt(0)}
                    </div>
                    <div>
                      <h3 className="font-serif font-bold text-base text-academic-primary leading-tight">
                        {mentor.name}
                      </h3>
                      <p className="text-xs font-mono text-academic-muted leading-tight mt-0.5">
                        {mentor.roll_no} • {mentor.admission_year}
                      </p>
                    </div>
                  </div>

                  <ProgramBadge program={mentor.program} />
                </div>

                {/* Rating & Reputation stats */}
                <div className="flex items-center space-x-3 mt-4 pt-3 border-t border-academic-border/70 text-xs">
                  <div className="flex items-center space-x-1 font-semibold text-amber-800 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                    <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-500" />
                    <span>{mentor.reputation_points} pts</span>
                  </div>

                  <div className="flex items-center space-x-1 text-academic-muted">
                    <span>
                      {mentor.avg_rating ? `★ ${mentor.avg_rating.toFixed(1)}` : 'New Mentor'}
                    </span>
                    <span>({mentor.total_reviews ?? 0} reviews)</span>
                  </div>
                </div>

                {/* Teachable skill */}
                <div className="mt-4 space-y-1.5">
                  <p className="text-[11px] font-semibold text-academic-muted uppercase tracking-wider">
                    Teachable Subject
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    <div className="inline-flex items-center space-x-1.5 bg-academic-secondary px-2.5 py-1 rounded border border-academic-border/60 text-xs">
                      <span className="font-semibold text-academic-primary">{mentor.skill_name}</span>
                      <ProficiencyBadge level={mentor.proficiency_level} />
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Button */}
              <div className="pt-2">
                <button
                  type="button"
                  onClick={() => openRequestModal(mentor)}
                  disabled={user?.roll_no === mentor.roll_no}
                  className="w-full py-2.5 rounded-lg bg-academic-burgundy text-white font-semibold text-xs shadow-xs hover:bg-academic-burgundy/90 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center space-x-1.5"
                >
                  <Calendar className="w-3.5 h-3.5" />
                  <span>
                    {user?.roll_no === mentor.roll_no ? 'Your Own Profile' : 'Request Mentorship'}
                  </span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />

      {/* Request Mentorship Modal */}
      <Modal
        isOpen={requestModalOpen}
        onClose={() => setRequestModalOpen(false)}
        title={`Request Mentorship with ${selectedMentor?.name}`}
      >
        <form onSubmit={handleRequestSubmit} className="space-y-4 text-xs">
          {requestError && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg">
              {requestError}
            </div>
          )}

          {requestSuccess && (
            <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>{requestSuccess}</span>
            </div>
          )}

          <div className="bg-amber-50/70 border border-amber-200 rounded-lg p-3 space-y-1 text-amber-900">
            <p className="font-semibold flex items-center space-x-1">
              <Sparkles className="w-3.5 h-3.5 text-amber-600" />
              <span>100% Free Peer Mentorship Policy</span>
            </p>
            <p className="text-[11px] text-amber-800">
              Sessions carry zero credit costs. Mentor receives +10 non-spendable reputation points upon verified completion.
            </p>
          </div>

          <div>
            <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
              Mentorship Subject / Focus Skill *
            </label>
            <select
              value={requestData.skill_id}
              onChange={(e) => setRequestData({ ...requestData, skill_id: parseInt(e.target.value, 10) })}
              required
              className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy font-medium"
            >
              {mentorSkills.map((sk) => (
                <option key={sk.skill_id} value={sk.skill_id}>
                  {sk.skill_name} ({sk.proficiency_level})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
              Specific Questions / Objectives *
            </label>
            <textarea
              required
              rows={3}
              placeholder="e.g. Need assistance with fingerpicking transitions, guitar tuning, and understanding chord progressions."
              value={requestData.topic}
              onChange={(e) => setRequestData({ ...requestData, topic: e.target.value })}
              className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
                Mode *
              </label>
              <select
                value={requestData.mode}
                onChange={(e) => setRequestData({ ...requestData, mode: e.target.value })}
                className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
              >
                <option value="ONLINE">Online (Google Meet)</option>
                <option value="OFFLINE">Offline (Campus Library)</option>
              </select>
            </div>

            <div>
              <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
                Scheduled Time *
              </label>
              <input
                type="datetime-local"
                required
                value={requestData.scheduled_at}
                onChange={(e) => setRequestData({ ...requestData, scheduled_at: e.target.value })}
                className="w-full p-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
              />
            </div>
          </div>

          {requestData.mode === 'ONLINE' && (
            <div>
              <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
                Online Meeting Link
              </label>
              <input
                type="url"
                value={requestData.meeting_link}
                onChange={(e) => setRequestData({ ...requestData, meeting_link: e.target.value })}
                placeholder="https://meet.google.com/..."
                className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
              />
            </div>
          )}

          <div className="pt-2 flex justify-end space-x-2">
            <button
              type="button"
              onClick={() => setRequestModalOpen(false)}
              className="px-4 py-2 rounded-lg border border-academic-border bg-academic-card text-academic-muted hover:bg-academic-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={requestLoading}
              className="px-4 py-2 rounded-lg bg-academic-burgundy text-white font-semibold shadow-xs hover:bg-academic-burgundy/90 disabled:opacity-50"
            >
              {requestLoading ? 'Sending Request...' : 'Confirm Mentorship Request'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
