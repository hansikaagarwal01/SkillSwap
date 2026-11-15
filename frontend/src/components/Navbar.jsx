import React, { useState, useEffect, useRef } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import {
  BookOpen,
  Users,
  Calendar,
  ShoppingBag,
  Award,
  BarChart3,
  ShieldCheck,
  LogOut,
  User,
  Star,
  Bell,
  CheckCheck,
  Check,
  Clock,
  ChevronDown,
} from 'lucide-react';

export const Navbar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const [unreadCount, setUnreadCount] = useState(0);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [loadingNotifs, setLoadingNotifs] = useState(false);
  const popoverRef = useRef(null);

  const navLinks = [
    { to: '/mentors', label: 'Students & Mentors', icon: Users },
    { to: '/skills', label: 'Skills', icon: BookOpen },
    { to: '/sessions', label: 'Sessions', icon: Calendar, authRequired: true },
    { to: '/marketplace', label: 'Marketplace', icon: ShoppingBag },
    { to: '/leaderboard', label: 'Leaderboard', icon: Award },
    { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  ];

  if (user && user.role === 'ADMIN') {
    navLinks.push({ to: '/admin', label: 'Admin', icon: ShieldCheck, authRequired: true });
  }

  const isActive = (path) => location.pathname === path;

  // Poll / fetch unread notification count with user scoping and cancellation
  useEffect(() => {
    if (!user) {
      setNotifications([]);
      setUnreadCount(0);
      setNotificationsOpen(false);
      return;
    }

    let active = true;
    const currentRoll = user.roll_no;

    const fetchCount = async () => {
      try {
        const resp = await api.get('/notifications/unread-count');
        if (active && user?.roll_no === currentRoll) {
          setUnreadCount(resp.data.unread_count || 0);
        }
      } catch (err) {
        // Quiet fail if network/auth not ready
      }
    };

    fetchCount();
    const timer = setInterval(fetchCount, 30000);

    return () => {
      active = false;
      clearInterval(timer);
    };
  }, [user?.roll_no, location.pathname]);

  const fetchNotifications = async () => {
    if (!user) return;
    const currentRoll = user.roll_no;
    setLoadingNotifs(true);
    try {
      const resp = await api.get('/notifications?page_size=8');
      if (user?.roll_no === currentRoll) {
        setNotifications(resp.data.items || []);
      }
    } catch (err) {
      console.error('Failed to load notifications', err);
    } finally {
      setLoadingNotifs(false);
    }
  };

  // Close notifications popover on click outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target)) {
        setNotificationsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleToggleNotifications = () => {
    if (!notificationsOpen) {
      fetchNotifications();
    }
    setNotificationsOpen(!notificationsOpen);
  };

  const handleMarkAsRead = async (notif) => {
    try {
      if (!notif.is_read) {
        await api.patch(`/notifications/${notif.notification_id}/read`);
        setNotifications((prev) =>
          prev.map((n) => (n.notification_id === notif.notification_id ? { ...n, is_read: true } : n))
        );
        setUnreadCount((prev) => Math.max(0, prev - 1));
      }
      setNotificationsOpen(false);
      if (notif.inquiry_id) {
        navigate('/marketplace?tab=INQUIRIES');
      }
    } catch (err) {
      console.error('Failed to mark notification as read', err);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await api.patch('/notifications/read-all');
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error('Failed to mark all as read', err);
    }
  };

  const handleLogout = () => {
    setNotifications([]);
    setUnreadCount(0);
    setNotificationsOpen(false);
    logout();
  };

  return (
    <header className="sticky top-0 z-40 bg-academic-card/95 backdrop-blur-md border-b border-academic-border shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 rounded-lg bg-academic-burgundy text-white flex items-center justify-center font-serif font-bold text-xl shadow-xs group-hover:bg-academic-accent transition-colors">
              SK
            </div>
            <div>
              <span className="font-serif font-bold text-xl text-academic-primary tracking-tight block leading-tight">
                SkillSwap <span className="text-academic-burgundy font-sans text-sm font-semibold uppercase tracking-wider">JKLU</span>
              </span>
              <span className="text-xs text-academic-muted block leading-none">Peer Mentoring & Campus Exchange</span>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1">
            {navLinks.map(({ to, label, icon: Icon, authRequired }) => {
              if (authRequired && !user) return null;
              const active = isActive(to);
              return (
                <Link
                  key={to}
                  to={to}
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    active
                      ? 'bg-academic-secondary text-academic-burgundy font-semibold'
                      : 'text-academic-primary/80 hover:text-academic-primary hover:bg-academic-secondary/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${active ? 'text-academic-burgundy' : 'text-academic-muted'}`} />
                  <span>{label}</span>
                </Link>
              );
            })}
          </nav>

          {/* User Controls */}
          <div className="flex items-center space-x-3">
            {user ? (
              <div className="flex items-center space-x-2 sm:space-x-3">
                {/* Reputation Badge */}
                <div className="hidden lg:flex items-center space-x-1 bg-amber-50 border border-amber-200 text-amber-900 px-2.5 py-1 rounded-full text-xs font-semibold shadow-xs">
                  <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-500" />
                  <span>{user.reputation_points} pts</span>
                </div>

                {/* Notifications Bell */}
                <div className="relative" ref={popoverRef}>
                  <button
                    onClick={handleToggleNotifications}
                    className={`relative p-2 rounded-lg border transition-all ${
                      notificationsOpen
                        ? 'bg-academic-secondary border-academic-burgundy text-academic-burgundy'
                        : 'border-academic-border text-academic-muted hover:text-academic-primary hover:bg-academic-secondary/60'
                    }`}
                    title="In-app Notifications"
                  >
                    <Bell className="w-4 h-4" />
                    {unreadCount > 0 && (
                      <span className="absolute -top-1 -right-1 bg-academic-burgundy text-white text-[10px] font-bold rounded-full h-4 min-w-[16px] px-1 flex items-center justify-center shadow-xs">
                        {unreadCount > 9 ? '9+' : unreadCount}
                      </span>
                    )}
                  </button>

                  {/* Notifications Popover Dropdown */}
                  {notificationsOpen && (
                    <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-academic-card border border-academic-border rounded-xl shadow-lg z-50 overflow-hidden text-xs">
                      <div className="p-3 border-b border-academic-border/70 flex items-center justify-between bg-academic-secondary/40">
                        <div className="flex items-center space-x-1.5 font-serif font-bold text-academic-primary text-sm">
                          <Bell className="w-4 h-4 text-academic-burgundy" />
                          <span>Notifications</span>
                          {unreadCount > 0 && (
                            <span className="bg-academic-burgundy/10 text-academic-burgundy text-[10px] px-1.5 py-0.5 rounded-full font-semibold">
                              {unreadCount} new
                            </span>
                          )}
                        </div>

                        {unreadCount > 0 && (
                          <button
                            onClick={handleMarkAllAsRead}
                            className="text-[11px] text-academic-burgundy hover:underline flex items-center space-x-1"
                          >
                            <CheckCheck className="w-3 h-3" />
                            <span>Mark all read</span>
                          </button>
                        )}
                      </div>

                      <div className="max-h-80 overflow-y-auto divide-y divide-academic-border/40">
                        {loadingNotifs ? (
                          <div className="py-8 text-center text-academic-muted">Loading notifications...</div>
                        ) : notifications.length === 0 ? (
                          <div className="py-8 text-center text-academic-muted space-y-1">
                            <Bell className="w-6 h-6 text-academic-muted/50 mx-auto" />
                            <p className="font-semibold text-academic-primary">No notifications</p>
                            <p className="text-[11px]">Product inquiries and session updates will appear here.</p>
                          </div>
                        ) : (
                          notifications.map((notif) => (
                            <div
                              key={notif.notification_id}
                              onClick={() => handleMarkAsRead(notif)}
                              className={`p-3 cursor-pointer transition-colors hover:bg-academic-secondary/60 flex items-start space-x-2.5 ${
                                !notif.is_read ? 'bg-amber-50/40' : ''
                              }`}
                            >
                              <div
                                className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${
                                  !notif.is_read ? 'bg-academic-burgundy' : 'bg-transparent'
                                }`}
                              />
                              <div className="flex-1 space-y-0.5">
                                <div className="flex items-baseline justify-between">
                                  <p className="font-semibold text-academic-primary">{notif.title}</p>
                                  <span className="text-[10px] text-academic-muted font-mono">
                                    {new Date(notif.created_at).toLocaleDateString([], {
                                      month: 'short',
                                      day: 'numeric',
                                    })}
                                  </span>
                                </div>
                                <p className="text-academic-muted text-[11px] leading-relaxed line-clamp-2">
                                  {notif.message}
                                </p>
                              </div>
                            </div>
                          ))
                        )}
                      </div>

                      <div className="p-2 border-t border-academic-border/70 bg-academic-secondary/30 text-center">
                        <Link
                          to="/marketplace?tab=INQUIRIES"
                          onClick={() => setNotificationsOpen(false)}
                          className="text-[11px] font-semibold text-academic-burgundy hover:underline"
                        >
                          View Marketplace Inquiries &rarr;
                        </Link>
                      </div>
                    </div>
                  )}
                </div>

                {/* Profile Pill */}
                <Link
                  to="/profile"
                  className="flex items-center space-x-2 pl-2 pr-3 py-1.5 rounded-lg border border-academic-border hover:bg-academic-secondary transition-colors"
                >
                  <div className="w-7 h-7 rounded-full bg-academic-burgundy text-white flex items-center justify-center text-xs font-bold">
                    {user.name.charAt(0)}
                  </div>
                  <div className="text-left hidden sm:block">
                    <p className="text-xs font-semibold text-academic-primary leading-tight">{user.name}</p>
                    <p className="text-[10px] text-academic-muted leading-tight font-mono">{user.roll_no}</p>
                  </div>
                </Link>

                {/* Logout Button */}
                <button
                  onClick={handleLogout}
                  title="Logout"
                  className="p-2 text-academic-muted hover:text-academic-burgundy hover:bg-academic-secondary rounded-lg transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Link
                  to="/login"
                  className="px-3.5 py-1.5 text-xs font-medium text-academic-primary hover:text-academic-burgundy transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="px-3.5 py-1.5 text-xs font-semibold bg-academic-burgundy text-white rounded-lg hover:bg-academic-burgundy/90 transition-colors shadow-xs"
                >
                  Join Community
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
