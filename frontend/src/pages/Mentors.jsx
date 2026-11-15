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
  Layers,
  GraduationCap,
} from 'lucide-react';

export const Mentors = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  // Tab State: 'DIRECTORY' (All students) vs 'MENTORS' (Verified mentors with can_teach=true)
  const [activeTab, setActiveTab] = useState('DIRECTORY');

  // Directory (Students) State
  const [students, setStudents] = useState([]);
  const [studentTotal, setStudentTotal] = useState(0);
  const [studentPage, setStudentPage] = useState(1);
  const [studentTotalPages, setStudentTotalPages] = useState(1);

  // Mentors State
  const [mentors, setMentors] = useState([]);
  const [mentorTotal, setMentorTotal] = useState(0);
  const [mentorPage, setMentorPage] = useState(1);
  const [mentorTotalPages, setMentorTotalPages] = useState(1);

  const [loading, setLoading] = useState(true);

  // Filter states
  const [skillsList, setSkillsList] = useState([]);
  const [selectedSkill, setSelectedSkill] = useState('');
  const [desiredSkill, setDesiredSkill] = useState('');
  const [selectedProgram, setSelectedProgram] = useState('');
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');

  // Request Modal state for mentorship booking
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

  // Fetch student directory
  const fetchStudents = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('page', studentPage);
      params.append('page_size', 9);
      if (selectedSkill) params.append('skill_id', selectedSkill);
      if (desiredSkill) params.append('desired_skill_id', desiredSkill);
      if (selectedProgram) params.append('program', selectedProgram);
      if (debouncedSearch) params.append('q', debouncedSearch);

      const resp = await api.get(`/students?${params.toString()}`);
      setStudents(resp.data.items);
      setStudentTotal(resp.data.total);
      setStudentTotalPages(resp.data.total_pages);
    } catch (err) {
      console.error('Failed to load students directory', err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch mentors with can_teach=true
  const fetchMentors = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('page', mentorPage);
      params.append('page_size', 9);
      if (selectedSkill) params.append('skill_id', selectedSkill);
      if (selectedProgram) params.append('program', selectedProgram);
      if (debouncedSearch) params.append('q', debouncedSearch);

      const resp = await api.get(`/mentors?${params.toString()}`);
      setMentors(resp.data.items);
      setMentorTotal(resp.data.total);
      setMentorTotalPages(resp.data.total_pages);
    } catch (err) {
      console.error('Failed to load mentors', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (debouncedSearch === search) return;
    const timer = setTimeout(() => {
      setStudentPage(1);
      setMentorPage(1);
      setDebouncedSearch(search);
    }, 350);
    return () => clearTimeout(timer);
  }, [search, debouncedSearch]);

  useEffect(() => {
    if (activeTab === 'DIRECTORY') {
      fetchStudents();
    } else {
      fetchMentors();
    }
  }, [activeTab, studentPage, mentorPage, selectedSkill, desiredSkill, selectedProgram, debouncedSearch]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setStudentPage(1);
    setMentorPage(1);
    if (debouncedSearch !== search) {
      setDebouncedSearch(search);
    } else if (activeTab === 'DIRECTORY') {
      fetchStudents();
    } else {
      fetchMentors();
    }
  };

  const openRequestModal = async (mentor) => {
    if (!user) {
      navigate('/login');
      return;
    }

    const fallbackSkills = Array.isArray(mentor.skills)
      ? mentor.skills.filter((sk) => sk.can_teach)
      : mentor.skill_id
      ? [{
          skill_id: mentor.skill_id,
          skill_name: mentor.skill_name,
          proficiency_level: mentor.proficiency_level,
          can_teach: true,
        }]
      : [];
    const defaultSkillId = mentor.skill_id || (fallbackSkills.length > 0 ? fallbackSkills[0].skill_id : '');

    setSelectedMentor(mentor);
    setRequestData({
      skill_id: defaultSkillId,
      topic: '',
      mode: 'ONLINE',
      scheduled_at: new Date(Date.now() + 86400000 * 2).toISOString().slice(0, 16),
      meeting_link: '',
    });
    setRequestError('');
    setRequestSuccess('');

    try {
      const resp = await api.get(`/students/${mentor.roll_no}/skills`);
      const fetchedSkills = Array.isArray(resp.data) ? resp.data : [];
      const teachable = fetchedSkills.length > 0
        ? fetchedSkills.filter((sk) => sk.can_teach)
        : fallbackSkills;
      setMentorSkills(teachable);
      if (teachable.length === 0) {
        setRequestData((prev) => ({ ...prev, skill_id: '' }));
        setRequestError('This student has no skills marked as available to teach.');
      } else if (!teachable.some((sk) => String(sk.skill_id) === String(defaultSkillId))) {
        setRequestData((prev) => ({ ...prev, skill_id: teachable[0].skill_id }));
      }
    } catch (err) {
      setMentorSkills(fallbackSkills);
      if (fallbackSkills.length === 0) {
        setRequestError('This student has no skills marked as available to teach.');
      }
    }

    setRequestModalOpen(true);
  };

  const handleRequestSubmit = async (e) => {
    e.preventDefault();
    setRequestLoading(true);
    setRequestError('');
    setRequestSuccess('');

    try {
      const payload = {
        mentor_roll_no: selectedMentor.roll_no,
        skill_id: parseInt(requestData.skill_id, 10),
        topic: requestData.topic,
        mode: requestData.mode,
        scheduled_at: new Date(requestData.scheduled_at).toISOString(),
        meeting_link: requestData.mode === 'ONLINE' ? (requestData.meeting_link.trim() || null) : null,
      };

      await api.post('/sessions', payload);
      setRequestSuccess('Mentorship request booked successfully! View status in Sessions tab.');
      setTimeout(() => {
        setRequestModalOpen(false);
        navigate('/sessions');
      }, 1500);
    } catch (err) {
      const msg = err.response?.data?.error?.message || 'Failed to submit mentorship request.';
      setRequestError(msg);
    } finally {
      setRequestLoading(false);
    }
  };

  return (
    <div className="space-y-8 py-6">
      {/* Page Title & Navigation Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-serif font-bold text-academic-primary">
            JKLU Student Directory & Mentors
          </h1>
          <p className="text-xs text-academic-muted mt-1">
            Discover fellow classmates across BTECH, BBA, and BDES programs, their possessed skills, and desired learning goals.
          </p>
        </div>

        {/* Tab Toggle */}
        <div className="inline-flex rounded-xl bg-academic-secondary p-1 border border-academic-border self-start">
          <button
            onClick={() => setActiveTab('DIRECTORY')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'DIRECTORY'
                ? 'bg-academic-card text-academic-primary shadow-xs'
                : 'text-academic-muted hover:text-academic-primary'
            }`}
          >
            Student Directory ({studentTotal ?? 0})
          </button>
          <button
            onClick={() => setActiveTab('MENTORS')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'MENTORS'
                ? 'bg-academic-card text-academic-primary shadow-xs'
                : 'text-academic-muted hover:text-academic-primary'
            }`}
          >
            Verified Mentors ({mentorTotal})
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-academic-card border border-academic-border rounded-xl p-4 shadow-xs">
        <form
          onSubmit={handleSearchSubmit}
          className={`grid grid-cols-1 gap-3 text-xs ${
            activeTab === 'DIRECTORY' ? 'sm:grid-cols-5' : 'sm:grid-cols-4'
          }`}
        >
          {/* Search */}
          <div className="sm:col-span-2 flex gap-2">
            <div className="relative flex-1">
              <input
                type="text"
                placeholder="Search by student name, roll number, or skill (e.g. Python, Guitar)..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-8 pr-3 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary placeholder:text-academic-muted/50 focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
              />
              <Search className="absolute left-2.5 top-2.5 w-3.5 h-3.5 text-academic-muted" />
            </div>
            <button
              type="submit"
              className="px-3.5 py-2 rounded-lg bg-academic-burgundy text-white font-semibold hover:bg-academic-burgundy/90 transition-colors shrink-0"
            >
              Search
            </button>
          </div>

          {/* Program filter */}
          <div>
            <select
              value={selectedProgram}
              onChange={(e) => {
                setSelectedProgram(e.target.value);
                setStudentPage(1);
                setMentorPage(1);
              }}
              className="w-full px-2.5 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
            >
              <option value="">All Programs</option>
              <option value="BTECH">B.Tech</option>
              <option value="BBA">BBA</option>
              <option value="BDES">B.Des</option>
            </select>
          </div>

          {/* Skill Filter */}
          <div>
            <select
              value={selectedSkill}
              onChange={(e) => {
                setSelectedSkill(e.target.value);
                setStudentPage(1);
                setMentorPage(1);
              }}
              className="w-full px-2.5 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
            >
              <option value="">All Skills ({skillsList.length})</option>
              {skillsList.map((sk) => (
                <option key={sk.skill_id} value={sk.skill_id}>
                  {sk.name}
                </option>
              ))}
            </select>
          </div>

          {activeTab === 'DIRECTORY' && (
            <div>
              <select
                value={desiredSkill}
                onChange={(e) => {
                  setDesiredSkill(e.target.value);
                  setStudentPage(1);
                }}
                className="w-full px-2.5 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
              >
                <option value="">Wants to Learn (Any)</option>
                {skillsList.map((sk) => (
                  <option key={sk.skill_id} value={sk.skill_id}>
                    Wants: {sk.name}
                  </option>
                ))}
              </select>
            </div>
          )}
        </form>
      </div>

      {/* Main Content Area */}
      {loading ? (
        <div className="py-20 text-center text-xs text-academic-muted">Loading student records...</div>
      ) : activeTab === 'DIRECTORY' ? (
        /* Tab 1: Student Directory */
        students.length === 0 ? (
          <div className="py-20 text-center bg-academic-card border border-academic-border rounded-xl p-8 space-y-2">
            <Users className="w-10 h-10 text-academic-muted mx-auto" />
            <p className="font-serif font-bold text-base text-academic-primary">No students match your search criteria</p>
            <p className="text-xs text-academic-muted">Try resetting search keywords or selecting a different academic program.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {students.map((st) => (
              <div
                key={st.roll_no}
                className="bg-academic-card border border-academic-border rounded-xl p-5 shadow-xs card-hover flex flex-col justify-between space-y-4"
              >
                <div className="space-y-3">
                  {/* Student Header */}
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-11 h-11 rounded-full bg-academic-burgundy text-white font-serif font-bold flex items-center justify-center text-base shadow-xs">
                        {st.name.charAt(0)}
                      </div>
                      <div>
                        <h3 className="font-serif font-bold text-base text-academic-primary leading-tight">
                          {st.name}
                        </h3>
                        <p className="text-xs font-mono text-academic-muted leading-tight mt-0.5">
                          {st.roll_no}
                        </p>
                      </div>
                    </div>

                    <ProgramBadge program={st.program} />
                  </div>

                  {/* Possessed Skills */}
                  <div className="space-y-1.5 pt-2 border-t border-academic-border/60">
                    <p className="text-[10px] font-semibold text-academic-muted uppercase tracking-wider flex items-center space-x-1">
                      <BookOpen className="w-3 h-3 text-academic-burgundy" />
                      <span>Possessed Skills ({st.skills?.length || 0})</span>
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {st.skills && st.skills.length > 0 ? (
                        st.skills.map((sk) => (
                          <span
                            key={sk.skill_id}
                            className="bg-academic-secondary px-2 py-0.5 rounded text-[11px] font-medium text-academic-primary border border-academic-border/60"
                          >
                            {sk.skill_name}
                          </span>
                        ))
                      ) : (
                        <span className="text-[11px] text-academic-muted italic">None specified</span>
                      )}
                    </div>
                  </div>

                  {/* Desired Skills */}
                  <div className="space-y-1.5 pt-1">
                    <p className="text-[10px] font-semibold text-academic-muted uppercase tracking-wider flex items-center space-x-1">
                      <Sparkles className="w-3 h-3 text-amber-600" />
                      <span>Wants to Learn ({st.desired_skills?.length || 0})</span>
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {st.desired_skills && st.desired_skills.length > 0 ? (
                        st.desired_skills.map((ds) => (
                          <span
                            key={ds.skill_id}
                            className="bg-amber-50/70 text-amber-900 border border-amber-200/70 px-2 py-0.5 rounded text-[11px]"
                          >
                            {ds.skill_name}
                          </span>
                        ))
                      ) : (
                        <span className="text-[11px] text-academic-muted italic">None specified</span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="pt-2 border-t border-academic-border/60 text-xs text-academic-muted flex items-center justify-between">
                  <span className="font-mono text-[11px]">{st.email}</span>
                  <span className="font-semibold text-academic-burgundy">{st.reputation_points} pts</span>
                </div>

                <div className="pt-2">
                  {(() => {
                    const teachableSkills = (st.skills || []).filter((sk) => sk.can_teach);
                    const isSelf = user?.roll_no === st.roll_no;
                    const cannotTeach = teachableSkills.length === 0;
                    return (
                      <button
                        type="button"
                        onClick={() => openRequestModal(st)}
                        disabled={isSelf || cannotTeach}
                        className="w-full py-2.5 rounded-lg bg-academic-burgundy text-white font-semibold text-xs shadow-xs hover:bg-academic-burgundy/90 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center space-x-1.5"
                      >
                        <Calendar className="w-3.5 h-3.5" />
                        <span>
                          {isSelf
                            ? 'Your Own Profile'
                            : cannotTeach
                            ? (!st.skills || st.skills.length === 0 ? 'No Skills Listed' : 'Not Available to Mentor')
                            : 'Request Peer Session'}
                        </span>
                      </button>
                    );
                  })()}
                </div>
              </div>
            ))}
          </div>
        )
      ) : (
        /* Tab 2: Verified Mentors (can_teach=true) */
        mentors.length === 0 ? (
          <div className="bg-academic-card border border-academic-border rounded-2xl p-10 text-center max-w-2xl mx-auto space-y-4">
            <div className="w-12 h-12 rounded-xl bg-academic-secondary text-academic-accent flex items-center justify-center mx-auto">
              <Users className="w-6 h-6" />
            </div>
            <div className="space-y-1">
              <h3 className="font-serif font-bold text-lg text-academic-primary">
                No Mentors Available Yet
              </h3>
              <p className="text-xs text-academic-muted leading-relaxed max-w-md mx-auto">
                In strict adherence to our university survey integration rules, student skills were imported with mentor availability disabled by default (`can_teach = FALSE`).
              </p>
              <p className="text-xs text-academic-muted leading-relaxed max-w-md mx-auto pt-1">
                Once a student claims their profile and turns on mentor availability for their skills in their Profile tab, they will appear here and can accept 1-on-1 peer sessions!
              </p>
            </div>
            <button
              onClick={() => setActiveTab('DIRECTORY')}
              className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-academic-burgundy text-white font-semibold text-xs shadow-xs hover:bg-academic-burgundy/90 transition-colors"
            >
              <span>Browse All Students in Student Directory</span>
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mentors.map((mentor) => (
              <div
                key={`${mentor.roll_no}-${mentor.skill_id}`}
                className="bg-academic-card border border-academic-border rounded-xl p-6 shadow-xs card-hover flex flex-col justify-between space-y-4"
              >
                <div>
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
                          {mentor.roll_no}
                        </p>
                      </div>
                    </div>

                    <ProgramBadge program={mentor.program} />
                  </div>

                  <div className="flex items-center space-x-3 mt-4 pt-3 border-t border-academic-border/70 text-xs">
                    <div className="flex items-center space-x-1 font-semibold text-amber-800 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                      <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-500" />
                      <span>{mentor.reputation_points} pts</span>
                    </div>

                    <div className="flex items-center space-x-1 text-academic-muted">
                      <span>{mentor.avg_rating ? `★ ${mentor.avg_rating.toFixed(1)}` : 'New Mentor'}</span>
                      <span>({mentor.total_reviews ?? 0} reviews)</span>
                    </div>
                  </div>

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

                <div className="pt-2">
                  <button
                    type="button"
                    onClick={() => openRequestModal(mentor)}
                    disabled={user?.roll_no === mentor.roll_no}
                    className="w-full py-2.5 rounded-lg bg-academic-burgundy text-white font-semibold text-xs shadow-xs hover:bg-academic-burgundy/90 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center space-x-1.5"
                  >
                    <Calendar className="w-3.5 h-3.5" />
                    <span>{user?.roll_no === mentor.roll_no ? 'Your Own Profile' : 'Request Mentorship'}</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )
      )}

      {/* Pagination */}
      {activeTab === 'DIRECTORY' ? (
        <Pagination page={studentPage} totalPages={studentTotalPages} onPageChange={setStudentPage} />
      ) : (
        <Pagination page={mentorPage} totalPages={mentorTotalPages} onPageChange={setMentorPage} />
      )}

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

          <div className="bg-academic-secondary border border-academic-border rounded-lg p-3 space-y-1 text-academic-primary">
            <p className="font-semibold flex items-center space-x-1">
              <Sparkles className="w-3.5 h-3.5 text-academic-accent" />
              <span>100% Free Peer Mentorship Policy</span>
            </p>
            <p className="text-[11px] text-academic-muted">
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
              disabled={requestLoading || mentorSkills.length === 0}
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
