import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { StatusBadge } from '../components/Badge';
import { Modal } from '../components/Modal';
import { Pagination } from '../components/Pagination';
import {
  Calendar,
  Clock,
  Video,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Star,
  ExternalLink,
  RotateCcw,
  Sparkles,
  Edit2,
} from 'lucide-react';

export const Sessions = () => {
  const { user, refreshUser } = useAuth();
  const [roleTab, setRoleTab] = useState('ALL'); // ALL, LEARNER, MENTOR
  const [statusFilter, setStatusFilter] = useState('');
  const [sessions, setSessions] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Review Modal state
  const [reviewModalOpen, setReviewModalOpen] = useState(false);
  const [activeSession, setActiveSession] = useState(null);
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [reviewLoading, setReviewLoading] = useState(false);
  const [reviewError, setReviewError] = useState('');

  // View Session Reviews Modal state
  const [viewReviewsOpen, setViewReviewsOpen] = useState(false);
  const [sessionReviews, setSessionReviews] = useState([]);
  const [reviewsLoading, setReviewsLoading] = useState(false);
  const [reviewsError, setReviewsError] = useState('');

  // Reschedule Modal state
  const [rescheduleModalOpen, setRescheduleModalOpen] = useState(false);
  const [rescheduleTime, setRescheduleTime] = useState('');
  const [rescheduleLoading, setRescheduleLoading] = useState(false);
  const [rescheduleError, setRescheduleError] = useState('');

  // Edit Session Modal state
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editTopic, setEditTopic] = useState('');
  const [editMode, setEditMode] = useState('ONLINE');
  const [editMeetingLink, setEditMeetingLink] = useState('');
  const [editScheduledAt, setEditScheduledAt] = useState('');
  const [editLoading, setEditLoading] = useState(false);
  const [editError, setEditError] = useState('');

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('page', page);
      params.append('page_size', 8);
      if (roleTab !== 'ALL') params.append('role', roleTab);
      if (statusFilter) params.append('status', statusFilter);

      const resp = await api.get(`/sessions?${params.toString()}`);
      setSessions(resp.data.items);
      setTotal(resp.data.total);
      setTotalPages(resp.data.total_pages);
    } catch (err) {
      console.error('Failed to load sessions', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, [page, roleTab, statusFilter]);

  const handleUpdateStatus = async (sessionId, newStatus) => {
    try {
      await api.patch(`/sessions/${sessionId}/status`, { status: newStatus });
      fetchSessions();
      if (newStatus === 'COMPLETED') {
        refreshUser();
      }
    } catch (err) {
      alert(err.response?.data?.error?.message || 'Failed to update session status.');
    }
  };

  const handleRescheduleSubmit = async (e) => {
    e.preventDefault();
    setRescheduleLoading(true);
    setRescheduleError('');
    try {
      await api.patch(`/sessions/${activeSession.session_id}/reschedule`, {
        scheduled_at: new Date(rescheduleTime).toISOString(),
      });
      setRescheduleModalOpen(false);
      fetchSessions();
    } catch (err) {
      setRescheduleError(err.response?.data?.error?.message || 'Failed to reschedule.');
    } finally {
      setRescheduleLoading(false);
    }
  };

  const openEditModal = (sess) => {
    setActiveSession(sess);
    setEditTopic(sess.topic || '');
    setEditMode(sess.mode || 'ONLINE');
    setEditMeetingLink(sess.meeting_link || '');
    setEditScheduledAt(sess.scheduled_at ? sess.scheduled_at.slice(0, 16) : '');
    setEditError('');
    setEditModalOpen(true);
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    setEditLoading(true);
    setEditError('');
    try {
      await api.patch(`/sessions/${activeSession.session_id}`, {
        topic: editTopic.trim(),
        mode: editMode,
        scheduled_at: new Date(editScheduledAt).toISOString(),
        meeting_link: editMode === 'ONLINE' ? (editMeetingLink.trim() || null) : null,
      });
      setEditModalOpen(false);
      fetchSessions();
    } catch (err) {
      setEditError(err.response?.data?.error?.message || 'Failed to update session.');
    } finally {
      setEditLoading(false);
    }
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    setReviewLoading(true);
    setReviewError('');
    try {
      await api.post('/reviews', {
        session_id: activeSession.session_id,
        rating: parseInt(rating, 10),
        comment: comment.trim() || null,
      });
      setReviewModalOpen(false);
      fetchSessions();
    } catch (err) {
      setReviewError(err.response?.data?.error?.message || 'Failed to submit review.');
    } finally {
      setReviewLoading(false);
    }
  };

  const openViewReviewsModal = async (sess) => {
    setActiveSession(sess);
    setViewReviewsOpen(true);
    setReviewsLoading(true);
    setReviewsError('');
    try {
      const resp = await api.get(`/sessions/${sess.session_id}/reviews`);
      setSessionReviews(resp.data || []);
    } catch (err) {
      setReviewsError(err.response?.data?.error?.message || 'Failed to load reviews.');
    } finally {
      setReviewsLoading(false);
    }
  };

  return (
    <div className="space-y-8 py-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-serif font-bold text-academic-primary">Peer Mentoring Sessions</h1>
        <p className="text-xs text-academic-muted mt-1">
          Manage your scheduled 1-on-1 mentorship interactions, verify session completions, and exchange reviews.
        </p>
      </div>

      {/* Role Tabs and Status Filter */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-academic-card border border-academic-border rounded-xl p-4 shadow-xs">
        {/* Tabs */}
        <div className="flex items-center space-x-1">
          {[
            { id: 'ALL', label: 'All Sessions' },
            { id: 'LEARNER', label: 'As Learner' },
            { id: 'MENTOR', label: 'As Mentor' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => {
                setRoleTab(tab.id);
                setPage(1);
              }}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                roleTab === tab.id
                  ? 'bg-academic-burgundy text-white shadow-xs'
                  : 'text-academic-muted hover:text-academic-primary hover:bg-academic-secondary'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Status Filter */}
        <div className="flex items-center space-x-2 text-xs">
          <span className="font-semibold text-academic-muted uppercase tracking-wider">Status:</span>
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="px-2.5 py-1.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
          >
            <option value="">All Statuses</option>
            <option value="REQUESTED">REQUESTED</option>
            <option value="ACCEPTED">ACCEPTED</option>
            <option value="COMPLETED">COMPLETED</option>
            <option value="CANCELLED">CANCELLED</option>
            <option value="REJECTED">REJECTED</option>
          </select>
        </div>
      </div>

      {/* Sessions Grid */}
      {loading ? (
        <div className="py-20 text-center text-xs text-academic-muted">Loading your academic sessions...</div>
      ) : sessions.length === 0 ? (
        <div className="py-20 text-center bg-academic-card border border-academic-border rounded-xl p-8 space-y-2">
          <Calendar className="w-10 h-10 text-academic-muted mx-auto" />
          <p className="font-serif font-bold text-base text-academic-primary">No sessions found</p>
          <p className="text-xs text-academic-muted">
            You don't have any sessions matching the selected filter. Explore mentors to request a session.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {sessions.map((sess) => {
            const isMentor = user?.roll_no === sess.mentor_roll_no;
            const isLearner = user?.roll_no === sess.learner_roll_no;
            const partnerName = isMentor ? sess.learner_name : sess.mentor_name;
            const partnerRoll = isMentor ? sess.learner_roll_no : sess.mentor_roll_no;
            const partnerRoleLabel = isMentor ? 'Learner' : 'Mentor';

            return (
              <div
                key={sess.session_id}
                className="bg-academic-card border border-academic-border rounded-xl p-5 shadow-xs card-hover flex flex-col justify-between space-y-4"
              >
                <div className="space-y-3">
                  {/* Top Header */}
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="text-[10px] font-mono text-academic-muted">Session #{sess.session_id}</span>
                      <h3 className="font-serif font-bold text-base text-academic-primary mt-0.5">
                        {sess.topic}
                      </h3>
                      <p className="text-xs text-academic-accent font-medium">Focus: {sess.skill_name}</p>
                    </div>

                    <StatusBadge status={sess.status} />
                  </div>

                  {/* Partner Info */}
                  <div className="bg-academic-secondary/60 rounded-lg p-3 text-xs space-y-1">
                    <p className="text-[11px] font-semibold text-academic-muted uppercase tracking-wider">
                      {partnerRoleLabel} Partner
                    </p>
                    <p className="font-semibold text-academic-primary">
                      {partnerName}{' '}
                      <span className="font-mono text-academic-muted text-[10px]">({partnerRoll})</span>
                    </p>
                  </div>

                  {/* Details */}
                  <div className="space-y-1.5 text-xs text-academic-muted">
                    <div className="flex items-center space-x-1.5">
                      <Clock className="w-3.5 h-3.5 text-academic-muted shrink-0" />
                      <span>{new Date(sess.scheduled_at).toLocaleString()}</span>
                    </div>

                    <div className="flex items-center space-x-1.5">
                      <Video className="w-3.5 h-3.5 text-academic-muted shrink-0" />
                      <span>Mode: {sess.mode}</span>
                      {sess.meeting_link && sess.mode === 'ONLINE' && (
                        <a
                          href={sess.meeting_link}
                          target="_blank"
                          rel="noreferrer"
                          className="text-academic-burgundy font-semibold hover:underline inline-flex items-center space-x-0.5 ml-2"
                        >
                          <span>Join Meeting</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </div>
                  </div>

                  {/* Reputation Reward Pill on Completion */}
                  {sess.status === 'COMPLETED' && (
                    <div className="flex items-center space-x-1.5 bg-amber-50 border border-amber-200 text-amber-900 px-3 py-1.5 rounded-lg text-xs font-semibold">
                      <Sparkles className="w-4 h-4 text-amber-500" />
                      <span>Verified Completion (+10 Reputation Awarded to Mentor)</span>
                    </div>
                  )}
                </div>

                {/* State Machine Action Buttons */}
                <div className="pt-2 border-t border-academic-border/60 flex flex-wrap gap-2 text-xs">
                  {/* REQUESTED Actions for Mentor */}
                  {sess.status === 'REQUESTED' && isMentor && (
                    <>
                      <button
                        onClick={() => handleUpdateStatus(sess.session_id, 'ACCEPTED')}
                        className="px-3 py-1.5 rounded-lg bg-emerald-600 text-white font-semibold hover:bg-emerald-700 transition-colors flex items-center space-x-1"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Accept Session</span>
                      </button>
                      <button
                        onClick={() => handleUpdateStatus(sess.session_id, 'REJECTED')}
                        className="px-3 py-1.5 rounded-lg border border-rose-300 bg-rose-50 text-rose-700 font-semibold hover:bg-rose-100 transition-colors flex items-center space-x-1"
                      >
                        <XCircle className="w-3.5 h-3.5" />
                        <span>Decline</span>
                      </button>
                    </>
                  )}

                  {/* ACCEPTED Actions for Mentor */}
                  {sess.status === 'ACCEPTED' && isMentor && (
                    <button
                      onClick={() => handleUpdateStatus(sess.session_id, 'COMPLETED')}
                      className="px-3 py-1.5 rounded-lg bg-academic-burgundy text-white font-semibold hover:bg-academic-burgundy/90 transition-colors flex items-center space-x-1 shadow-xs"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Complete Session (+10 Pts)</span>
                    </button>
                  )}

                  {/* Reschedule, Edit & Cancel for pending/accepted */}
                  {(sess.status === 'REQUESTED' || sess.status === 'ACCEPTED') && (
                    <>
                      <button
                        onClick={() => openEditModal(sess)}
                        className="px-3 py-1.5 rounded-lg border border-academic-border bg-academic-secondary hover:bg-academic-border/60 text-academic-primary transition-colors flex items-center space-x-1"
                      >
                        <Edit2 className="w-3.5 h-3.5 text-academic-muted" />
                        <span>Edit Details</span>
                      </button>

                      <button
                        onClick={() => {
                          setActiveSession(sess);
                          setRescheduleTime(sess.scheduled_at.slice(0, 16));
                          setRescheduleModalOpen(true);
                        }}
                        className="px-3 py-1.5 rounded-lg border border-academic-border bg-academic-secondary hover:bg-academic-border/60 text-academic-primary transition-colors flex items-center space-x-1"
                      >
                        <RotateCcw className="w-3.5 h-3.5 text-academic-muted" />
                        <span>Reschedule</span>
                      </button>

                      <button
                        onClick={() => handleUpdateStatus(sess.session_id, 'CANCELLED')}
                        className="px-3 py-1.5 rounded-lg text-academic-muted hover:text-rose-600 transition-colors"
                      >
                        Cancel
                      </button>
                    </>
                  )}

                  {/* Review Buttons on COMPLETED */}
                  {sess.status === 'COMPLETED' && (
                    <>
                      {!sess.has_review ? (
                        <button
                          onClick={() => {
                            setActiveSession(sess);
                            setRating(5);
                            setComment('');
                            setReviewError('');
                            setReviewModalOpen(true);
                          }}
                          className="px-3 py-1.5 rounded-lg border border-amber-300 bg-amber-50 text-amber-900 font-semibold hover:bg-amber-100 transition-colors flex items-center space-x-1"
                        >
                          <Star className="w-3.5 h-3.5 text-amber-500 fill-amber-400" />
                          <span>Leave Peer Review</span>
                        </button>
                      ) : (
                        <span className="px-3 py-1.5 rounded-lg border border-emerald-200 bg-emerald-50 text-emerald-800 font-semibold flex items-center space-x-1">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                          <span>Reviewed</span>
                        </span>
                      )}

                      <button
                        onClick={() => openViewReviewsModal(sess)}
                        className="px-3 py-1.5 rounded-lg border border-academic-border bg-academic-secondary hover:bg-academic-border/60 text-academic-primary font-semibold transition-colors flex items-center space-x-1"
                      >
                        <Star className="w-3.5 h-3.5 text-academic-muted" />
                        <span>View Reviews</span>
                      </button>
                    </>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Pagination */}
      <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />

      {/* Reschedule Modal */}
      <Modal
        isOpen={rescheduleModalOpen}
        onClose={() => setRescheduleModalOpen(false)}
        title={`Reschedule Session #${activeSession?.session_id}`}
      >
        <form onSubmit={handleRescheduleSubmit} className="space-y-4 text-xs">
          {rescheduleError && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg">
              {rescheduleError}
            </div>
          )}

          <div>
            <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
              New Date & Time *
            </label>
            <input
              type="datetime-local"
              required
              value={rescheduleTime}
              onChange={(e) => setRescheduleTime(e.target.value)}
              className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
            />
          </div>

          <div className="pt-2 flex justify-end space-x-2">
            <button
              type="button"
              onClick={() => setRescheduleModalOpen(false)}
              className="px-4 py-2 rounded-lg border border-academic-border bg-academic-card text-academic-muted hover:bg-academic-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={rescheduleLoading}
              className="px-4 py-2 rounded-lg bg-academic-burgundy text-white font-semibold shadow-xs hover:bg-academic-burgundy/90 disabled:opacity-50"
            >
              {rescheduleLoading ? 'Updating...' : 'Save New Time'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Edit Session Details Modal */}
      <Modal
        isOpen={editModalOpen}
        onClose={() => setEditModalOpen(false)}
        title={`Edit Session #${activeSession?.session_id} Details`}
      >
        <form onSubmit={handleEditSubmit} className="space-y-4 text-xs">
          {editError && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg">
              {editError}
            </div>
          )}

          <div>
            <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
              Topic / Focus Questions *
            </label>
            <textarea
              required
              rows={3}
              value={editTopic}
              onChange={(e) => setEditTopic(e.target.value)}
              className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
                Mode *
              </label>
              <select
                value={editMode}
                onChange={(e) => setEditMode(e.target.value)}
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
                value={editScheduledAt}
                onChange={(e) => setEditScheduledAt(e.target.value)}
                className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
              />
            </div>
          </div>

          {editMode === 'ONLINE' && (
            <div>
              <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
                Google Meet / Zoom Meeting Link
              </label>
              <input
                type="url"
                value={editMeetingLink}
                placeholder="https://meet.google.com/..."
                onChange={(e) => setEditMeetingLink(e.target.value)}
                className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
              />
            </div>
          )}

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
              {editLoading ? 'Saving Changes...' : 'Save Session Details'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Review Modal */}
      <Modal
        isOpen={reviewModalOpen}
        onClose={() => setReviewModalOpen(false)}
        title={`Peer Review for Session #${activeSession?.session_id}`}
      >
        <form onSubmit={handleReviewSubmit} className="space-y-4 text-xs">
          {reviewError && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg">
              {reviewError}
            </div>
          )}

          <div>
            <label className="block font-semibold text-academic-primary mb-2 uppercase tracking-wider">
              Rating (1 to 5 Stars) *
            </label>
            <div className="flex items-center space-x-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  type="button"
                  key={star}
                  onClick={() => setRating(star)}
                  className="p-1 text-2xl focus:outline-none hover:scale-110 transition-transform"
                >
                  <Star
                    className={`w-7 h-7 ${
                      star <= rating ? 'fill-amber-400 text-amber-500' : 'text-academic-border'
                    }`}
                  />
                </button>
              ))}
              <span className="font-semibold text-academic-primary ml-2">{rating} out of 5</span>
            </div>
          </div>

          <div>
            <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
              Constructive Peer Feedback
            </label>
            <textarea
              rows={3}
              placeholder="How helpful was this session? Share your thoughts on technical depth and clarity."
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
            />
          </div>

          <div className="pt-2 flex justify-end space-x-2">
            <button
              type="button"
              onClick={() => setReviewModalOpen(false)}
              className="px-4 py-2 rounded-lg border border-academic-border bg-academic-card text-academic-muted hover:bg-academic-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={reviewLoading}
              className="px-4 py-2 rounded-lg bg-academic-burgundy text-white font-semibold shadow-xs hover:bg-academic-burgundy/90 disabled:opacity-50"
            >
              {reviewLoading ? 'Submitting...' : 'Post Verified Review'}
            </button>
          </div>
        </form>
      </Modal>

      {/* View Session Reviews Modal */}
      <Modal
        isOpen={viewReviewsOpen}
        onClose={() => setViewReviewsOpen(false)}
        title={`Peer Reviews for Session #${activeSession?.session_id}`}
      >
        <div className="space-y-4 text-xs">
          {reviewsError && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg">
              {reviewsError}
            </div>
          )}

          {reviewsLoading ? (
            <p className="text-center text-academic-muted py-6">Loading session reviews...</p>
          ) : sessionReviews.length === 0 ? (
            <p className="text-center text-academic-muted py-6">
              No reviews have been submitted for this session yet.
            </p>
          ) : (
            <div className="space-y-3">
              {sessionReviews.map((rev) => (
                <div
                  key={`${rev.session_id}-${rev.roll_no}`}
                  className="p-3.5 rounded-xl border border-academic-border bg-academic-secondary/40 space-y-1.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-academic-primary">
                      {rev.reviewer_name || rev.roll_no}{' '}
                      <span className="text-academic-muted font-normal">
                        reviewed {rev.reviewee_name || rev.reviewee_roll_no}
                      </span>
                    </span>
                    <span className="inline-flex items-center space-x-1 font-semibold text-amber-800 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded">
                      <Star className="w-3 h-3 fill-amber-400 text-amber-500" />
                      <span>{rev.rating}/5</span>
                    </span>
                  </div>
                  {rev.comment && (
                    <p className="text-academic-muted leading-relaxed">{rev.comment}</p>
                  )}
                  <p className="text-[10px] text-academic-muted font-mono">
                    {new Date(rev.created_at).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          )}

          <div className="pt-2 flex justify-end">
            <button
              type="button"
              onClick={() => setViewReviewsOpen(false)}
              className="px-4 py-2 rounded-lg border border-academic-border bg-academic-card text-academic-primary hover:bg-academic-secondary font-semibold"
            >
              Close
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
