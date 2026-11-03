import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { StatusBadge } from '../components/Badge';
import { Modal } from '../components/Modal';
import { Pagination } from '../components/Pagination';
import {
  ShoppingBag,
  Search,
  Plus,
  Tag,
  CheckCircle2,
  AlertCircle,
  Clock,
  User,
  ShieldCheck,
  PackageCheck,
  Sparkles,
  Mail,
  Check,
  X,
  MessageSquare,
  Send,
  Inbox,
  SendHorizontal,
} from 'lucide-react';

export const Marketplace = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const initialTab = searchParams.get('tab') || 'ALL';
  const [activeTab, setActiveTab] = useState(initialTab); // ALL, MINE, INQUIRIES, SENT_INQUIRIES, PURCHASES
  const [listings, setListings] = useState([]);
  const [inquiries, setInquiries] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filters
  const [category, setCategory] = useState('');
  const [itemCondition, setItemCondition] = useState('');
  const [search, setSearch] = useState('');

  // Post Listing Modal
  const [postModalOpen, setPostModalOpen] = useState(false);
  const [postForm, setPostForm] = useState({
    title: '',
    description: '',
    price: '',
    category: 'Textbooks',
    item_condition: 'GOOD',
  });
  const [postLoading, setPostLoading] = useState(false);
  const [postError, setPostError] = useState('');

  // Send Inquiry Modal
  const [inquiryModalOpen, setInquiryModalOpen] = useState(false);
  const [inquiryTarget, setInquiryTarget] = useState(null);
  const [inquiryMessage, setInquiryMessage] = useState('Hi, I am interested in purchasing this item. Is it still available?');
  const [inquiryLoading, setInquiryLoading] = useState(false);
  const [inquirySuccess, setInquirySuccess] = useState('');
  const [inquiryError, setInquiryError] = useState('');

  // Buy Request Modal
  const [buyModalOpen, setBuyModalOpen] = useState(false);
  const [targetListing, setTargetListing] = useState(null);
  const [buyConfirmed, setBuyConfirmed] = useState(false);
  const [buyLoading, setBuyLoading] = useState(false);
  const [buySuccess, setBuySuccess] = useState('');
  const [buyError, setBuyError] = useState('');

  // Seller Confirm Payment Modal
  const [sellerModalOpen, setSellerModalOpen] = useState(false);
  const [sellerTarget, setSellerTarget] = useState(null);
  const [sellerLoading, setSellerLoading] = useState(false);
  const [sellerError, setSellerError] = useState('');

  // Cancel Deal Modal
  const [cancelModalOpen, setCancelModalOpen] = useState(false);
  const [cancelTarget, setCancelTarget] = useState(null);
  const [cancelLoading, setCancelLoading] = useState(false);
  const [cancelError, setCancelError] = useState('');

  // Sync tab with URL query parameter
  useEffect(() => {
    const tabParam = searchParams.get('tab');
    if (tabParam && ['ALL', 'MINE', 'INQUIRIES', 'SENT_INQUIRIES', 'PURCHASES'].includes(tabParam)) {
      setActiveTab(tabParam);
    }
  }, [searchParams]);

  const handleTabChange = (newTab) => {
    setActiveTab(newTab);
    setPage(1);
    setSearchParams(newTab === 'ALL' ? {} : { tab: newTab });
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'INQUIRIES' || activeTab === 'SENT_INQUIRIES') {
        const endpoint =
          activeTab === 'INQUIRIES'
            ? '/marketplace/inquiries/received'
            : '/marketplace/inquiries/sent';
        const resp = await api.get(`${endpoint}?page=${page}&page_size=10`);
        setInquiries(resp.data.items || []);
        setTotal(resp.data.total);
        setTotalPages(resp.data.total_pages);
      } else {
        let endpoint = '/listings';
        const params = new URLSearchParams();
        params.append('page', page);
        params.append('page_size', 9);

        if (activeTab === 'MINE') {
          endpoint = '/listings/mine';
        } else if (activeTab === 'PURCHASES') {
          endpoint = '/listings/purchases';
        } else {
          if (category) params.append('category', category);
          if (itemCondition) params.append('item_condition', itemCondition);
          if (search) params.append('search', search);
        }

        const resp = await api.get(`${endpoint}?${params.toString()}`);
        setListings(resp.data.items || []);
        setTotal(resp.data.total);
        setTotalPages(resp.data.total_pages);
      }
    } catch (err) {
      console.error('Failed to load marketplace data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [page, activeTab, category, itemCondition]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchData();
  };

  const handlePostSubmit = async (e) => {
    e.preventDefault();
    setPostLoading(true);
    setPostError('');
    try {
      await api.post('/listings', {
        ...postForm,
        price: parseFloat(postForm.price),
      });
      setPostModalOpen(false);
      setPostForm({ title: '', description: '', price: '', category: 'Textbooks', item_condition: 'GOOD' });
      fetchData();
    } catch (err) {
      setPostError(err.response?.data?.error?.message || 'Failed to create listing.');
    } finally {
      setPostLoading(false);
    }
  };

  // Inquiry Handlers
  const openInquiryModal = (item) => {
    if (!user) {
      navigate('/login');
      return;
    }
    setInquiryTarget(item);
    setInquiryMessage('Hi, I am interested in purchasing this item. Is it still available?');
    setInquirySuccess('');
    setInquiryError('');
    setInquiryModalOpen(true);
  };

  const handleInquirySubmit = async (e) => {
    e.preventDefault();
    setInquiryLoading(true);
    setInquiryError('');
    setInquirySuccess('');
    try {
      await api.post(`/marketplace/listings/${inquiryTarget.listing_id}/inquiries`, {
        message: inquiryMessage,
      });
      setInquirySuccess('Inquiry sent successfully! The seller has received an in-app notification and email.');
      setTimeout(() => {
        setInquiryModalOpen(false);
      }, 1500);
    } catch (err) {
      setInquiryError(err.response?.data?.error?.message || 'Failed to send inquiry.');
    } finally {
      setInquiryLoading(false);
    }
  };

  const handleUpdateInquiryStatus = async (inquiryId, newStatus) => {
    try {
      await api.patch(`/marketplace/inquiries/${inquiryId}/status`, { status: newStatus });
      fetchData();
    } catch (err) {
      alert(err.response?.data?.error?.message || 'Failed to update status');
    }
  };

  // Buy Request Handlers
  const openBuyModal = (item) => {
    if (!user) {
      navigate('/login');
      return;
    }
    setTargetListing(item);
    setBuyConfirmed(false);
    setBuyError('');
    setBuySuccess('');
    setBuyModalOpen(true);
  };

  const handleBuyConfirm = async () => {
    setBuyLoading(true);
    setBuyError('');
    setBuySuccess('');
    try {
      await api.post(`/listings/${targetListing.listing_id}/purchase`);
      setBuySuccess('Purchase request submitted! The item is now marked In Progress. Coordinate on campus with the seller.');
      setTimeout(() => {
        setBuyModalOpen(false);
        fetchData();
      }, 1400);
    } catch (err) {
      setBuyError(err.response?.data?.error?.message || 'Purchase request could not be completed.');
    } finally {
      setBuyLoading(false);
    }
  };

  const openSellerConfirmModal = (item) => {
    setSellerTarget(item);
    setSellerError('');
    setSellerModalOpen(true);
  };

  const handleSellerConfirm = async () => {
    setSellerLoading(true);
    setSellerError('');
    try {
      await api.post(`/listings/${sellerTarget.listing_id}/confirm-sale`);
      setSellerModalOpen(false);
      fetchData();
    } catch (err) {
      setSellerError(err.response?.data?.error?.message || 'Failed to confirm sale.');
    } finally {
      setSellerLoading(false);
    }
  };

  const openCancelModal = (item) => {
    setCancelTarget(item);
    setCancelError('');
    setCancelModalOpen(true);
  };

  const handleCancelSale = async () => {
    setCancelLoading(true);
    setCancelError('');
    try {
      await api.post(`/listings/${cancelTarget.listing_id}/cancel-sale`);
      setCancelModalOpen(false);
      fetchData();
    } catch (err) {
      setCancelError(err.response?.data?.error?.message || 'Failed to cancel deal.');
    } finally {
      setCancelLoading(false);
    }
  };

  return (
    <div className="space-y-8 py-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-serif font-bold text-academic-primary">Campus Student Marketplace</h1>
          <p className="text-xs text-academic-muted mt-1">
            Exchange textbooks, lab gear, and study supplies directly between verified JKLU students.
          </p>
        </div>

        {user && (
          <button
            onClick={() => setPostModalOpen(true)}
            className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-lg bg-academic-burgundy text-white font-semibold text-xs shadow-xs hover:bg-academic-burgundy/90 transition-all self-start sm:self-auto"
          >
            <Plus className="w-4 h-4" />
            <span>Post Item for Sale</span>
          </button>
        )}
      </div>

      {/* Navigation Tabs and Filters */}
      <div className="bg-academic-card border border-academic-border rounded-xl p-4 shadow-xs space-y-4">
        {/* Navigation Tabs */}
        <div className="flex flex-wrap items-center gap-1.5 border-b border-academic-border/70 pb-3">
          {[
            { id: 'ALL', label: 'Explore Marketplace' },
            ...(user
              ? [
                  { id: 'MINE', label: 'My Listings' },
                  { id: 'INQUIRIES', label: 'Inquiries Received' },
                  { id: 'SENT_INQUIRIES', label: 'My Sent Inquiries' },
                  { id: 'PURCHASES', label: 'My Purchases' },
                ]
              : []),
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleTabChange(tab.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                activeTab === tab.id
                  ? 'bg-academic-burgundy text-white shadow-xs'
                  : 'text-academic-muted hover:text-academic-primary hover:bg-academic-secondary'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Filter controls (only on Explore tab) */}
        {activeTab === 'ALL' && (
          <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            <div className="relative sm:col-span-2">
              <input
                type="text"
                placeholder="Search items by title or keywords..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-8 pr-3 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary placeholder:text-academic-muted/50 focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
              />
              <Search className="absolute left-2.5 top-2.5 w-3.5 h-3.5 text-academic-muted" />
            </div>

            <div>
              <select
                value={category}
                onChange={(e) => {
                  setCategory(e.target.value);
                  setPage(1);
                }}
                className="w-full px-2.5 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
              >
                <option value="">All Categories</option>
                <option value="Textbooks">Textbooks</option>
                <option value="Electronics">Electronics</option>
                <option value="Lab Equipment">Lab Equipment</option>
                <option value="Hostel Essentials">Hostel Essentials</option>
                <option value="Stationery">Stationery</option>
              </select>
            </div>

            <div>
              <select
                value={itemCondition}
                onChange={(e) => {
                  setItemCondition(e.target.value);
                  setPage(1);
                }}
                className="w-full px-2.5 py-2 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
              >
                <option value="">Any Condition</option>
                <option value="NEW">Brand New</option>
                <option value="LIKE_NEW">Like New</option>
                <option value="GOOD">Good Condition</option>
                <option value="FAIR">Fair Condition</option>
              </select>
            </div>
          </form>
        )}
      </div>

      {/* View 1: Inquiries Received Tab */}
      {activeTab === 'INQUIRIES' ? (
        loading ? (
          <div className="py-20 text-center text-xs text-academic-muted">Loading received inquiries...</div>
        ) : inquiries.length === 0 ? (
          <div className="py-20 text-center bg-academic-card border border-academic-border rounded-xl p-8 space-y-2">
            <Inbox className="w-10 h-10 text-academic-muted mx-auto" />
            <p className="font-serif font-bold text-base text-academic-primary">No inquiries received yet</p>
            <p className="text-xs text-academic-muted">When prospective buyers ask about your items, their messages appear here.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {inquiries.map((inq) => (
              <div
                key={inq.inquiry_id}
                className="bg-academic-card border border-academic-border rounded-xl p-5 shadow-xs space-y-3"
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2 border-b border-academic-border/60 pb-3">
                  <div>
                    <span className="text-[10px] uppercase font-bold text-academic-muted tracking-wider">Item Inquired</span>
                    <h3 className="font-serif font-bold text-base text-academic-primary">{inq.listing_title}</h3>
                    <p className="text-xs font-semibold text-academic-burgundy mt-0.5">₹ {parseFloat(inq.listing_price).toFixed(2)}</p>
                  </div>

                  <div className="flex items-center space-x-2">
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${
                        inq.inquiry_status === 'PENDING'
                          ? 'bg-amber-50 text-amber-900 border-amber-300'
                          : inq.inquiry_status === 'RESPONDED'
                          ? 'bg-blue-50 text-blue-900 border-blue-200'
                          : 'bg-gray-100 text-gray-700 border-gray-200'
                      }`}
                    >
                      {inq.inquiry_status}
                    </span>
                    <span className="text-[11px] text-academic-muted font-mono">
                      {new Date(inq.created_at).toLocaleString([], {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </div>
                </div>

                {/* Buyer Information & Message */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                  <div className="bg-academic-secondary/50 rounded-lg p-3 space-y-1">
                    <p className="font-semibold text-academic-primary">Buyer Details:</p>
                    <p>Name: <span className="font-medium text-academic-primary">{inq.buyer_name}</span></p>
                    <p>Roll No: <span className="font-mono text-academic-primary">{inq.buyer_roll_no}</span></p>
                    <p>
                      Email:{' '}
                      <a href={`mailto:${inq.buyer_email}`} className="text-academic-burgundy hover:underline font-mono">
                        {inq.buyer_email}
                      </a>
                    </p>
                  </div>

                  <div className="md:col-span-2 bg-academic-secondary/30 rounded-lg p-3 space-y-1 border border-academic-border/50">
                    <p className="font-semibold text-academic-primary">Buyer Inquiry Message:</p>
                    <p className="text-academic-muted leading-relaxed whitespace-pre-line">{inq.message}</p>
                  </div>
                </div>

                {/* Seller Actions */}
                <div className="flex flex-wrap items-center justify-end gap-2 pt-2 border-t border-academic-border/50">
                  <a
                    href={`mailto:${inq.buyer_email}?subject=Re: Inquiry regarding ${encodeURIComponent(inq.listing_title)} on SkillSwap JKLU`}
                    className="px-3 py-1.5 rounded-lg border border-academic-border bg-academic-card hover:bg-academic-secondary text-academic-primary font-semibold text-xs flex items-center space-x-1"
                  >
                    <Mail className="w-3.5 h-3.5 text-academic-muted" />
                    <span>Email Buyer</span>
                  </a>

                  {inq.inquiry_status === 'PENDING' && (
                    <button
                      onClick={() => handleUpdateInquiryStatus(inq.inquiry_id, 'RESPONDED')}
                      className="px-3 py-1.5 rounded-lg bg-academic-secondary text-academic-primary font-semibold text-xs hover:bg-academic-border/50 transition-colors"
                    >
                      Mark Responded
                    </button>
                  )}

                  {inq.inquiry_status !== 'CLOSED' && (
                    <button
                      onClick={() => handleUpdateInquiryStatus(inq.inquiry_id, 'CLOSED')}
                      className="px-3 py-1.5 rounded-lg border border-gray-300 text-gray-700 bg-gray-50 hover:bg-gray-100 font-semibold text-xs transition-colors"
                    >
                      Close Inquiry
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )
      ) : activeTab === 'SENT_INQUIRIES' ? (
        /* View 2: Sent Inquiries Tab */
        loading ? (
          <div className="py-20 text-center text-xs text-academic-muted">Loading sent inquiries...</div>
        ) : inquiries.length === 0 ? (
          <div className="py-20 text-center bg-academic-card border border-academic-border rounded-xl p-8 space-y-2">
            <SendHorizontal className="w-10 h-10 text-academic-muted mx-auto" />
            <p className="font-serif font-bold text-base text-academic-primary">No sent inquiries</p>
            <p className="text-xs text-academic-muted">You haven't contacted any sellers yet. Explore the marketplace to find items.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {inquiries.map((inq) => (
              <div
                key={inq.inquiry_id}
                className="bg-academic-card border border-academic-border rounded-xl p-5 shadow-xs space-y-3"
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2 border-b border-academic-border/60 pb-3">
                  <div>
                    <span className="text-[10px] uppercase font-bold text-academic-muted tracking-wider">Item Inquired</span>
                    <h3 className="font-serif font-bold text-base text-academic-primary">{inq.listing_title}</h3>
                    <p className="text-xs font-semibold text-academic-burgundy mt-0.5">₹ {parseFloat(inq.listing_price).toFixed(2)}</p>
                  </div>

                  <div className="flex items-center space-x-2">
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${
                        inq.inquiry_status === 'PENDING'
                          ? 'bg-amber-50 text-amber-900 border-amber-300'
                          : inq.inquiry_status === 'RESPONDED'
                          ? 'bg-blue-50 text-blue-900 border-blue-200'
                          : 'bg-gray-100 text-gray-700 border-gray-200'
                      }`}
                    >
                      {inq.inquiry_status}
                    </span>
                    <span className="text-[11px] text-academic-muted font-mono">
                      {new Date(inq.created_at).toLocaleDateString([], { month: 'short', day: 'numeric' })}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                  <div className="bg-academic-secondary/50 rounded-lg p-3 space-y-1">
                    <p className="font-semibold text-academic-primary">Seller Details:</p>
                    <p>Name: <span className="font-medium text-academic-primary">{inq.seller_name}</span></p>
                    <p>Roll No: <span className="font-mono text-academic-primary">{inq.seller_roll_no}</span></p>
                    <p>
                      Email:{' '}
                      <a href={`mailto:${inq.seller_email}`} className="text-academic-burgundy hover:underline font-mono">
                        {inq.seller_email}
                      </a>
                    </p>
                  </div>

                  <div className="md:col-span-2 bg-academic-secondary/30 rounded-lg p-3 space-y-1 border border-academic-border/50">
                    <p className="font-semibold text-academic-primary">Your Message to Seller:</p>
                    <p className="text-academic-muted leading-relaxed whitespace-pre-line">{inq.message}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )
      ) : (
        /* View 3: Listing Cards Grid (Explore, Mine, Purchases) */
        loading ? (
          <div className="py-20 text-center text-xs text-academic-muted">Loading marketplace listings...</div>
        ) : listings.length === 0 ? (
          <div className="py-20 text-center bg-academic-card border border-academic-border rounded-xl p-8 space-y-2">
            <ShoppingBag className="w-10 h-10 text-academic-muted mx-auto" />
            <p className="font-serif font-bold text-base text-academic-primary">No items found</p>
            <p className="text-xs text-academic-muted">Try adjusting your filters or post a new item.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {listings.map((item) => {
              const isSeller = user?.roll_no === item.seller_roll_no;
              const isBuyer = user?.roll_no === item.buyer_roll_no;

              return (
                <div
                  key={item.listing_id}
                  className="bg-academic-card border border-academic-border rounded-xl p-5 shadow-xs card-hover flex flex-col justify-between space-y-4"
                >
                  <div className="space-y-3">
                    {/* Top Tags */}
                    <div className="flex items-start justify-between">
                      <div className="flex items-center space-x-1.5">
                        <span className="text-[10px] font-semibold text-academic-accent uppercase tracking-wider bg-academic-secondary px-2 py-0.5 rounded border border-academic-border">
                          {item.category}
                        </span>
                        <span className="text-[10px] font-mono text-academic-muted bg-academic-secondary/60 px-1.5 py-0.5 rounded">
                          {item.item_condition}
                        </span>
                      </div>

                      <StatusBadge status={item.status} />
                    </div>

                    {/* Title & Price */}
                    <div>
                      <h3 className="font-serif font-bold text-base text-academic-primary leading-tight">
                        {item.title}
                      </h3>
                      <div className="flex items-baseline space-x-2 mt-1">
                        <span className="text-xl font-bold font-serif text-academic-burgundy">
                          ₹ {parseFloat(item.price).toFixed(0)}
                        </span>
                        {item.original_price_text && item.original_price_text !== String(parseInt(item.price, 10)) && (
                          <span className="text-xs text-academic-muted font-mono">
                            ({item.original_price_text})
                          </span>
                        )}
                      </div>
                    </div>

                    <p className="text-xs text-academic-muted leading-relaxed line-clamp-3">
                      {item.description}
                    </p>

                    {/* Seller / Buyer details */}
                    <div className="bg-academic-secondary/50 rounded-lg p-2.5 text-xs text-academic-muted space-y-1">
                      <p>
                        <span className="font-semibold text-academic-primary">Seller:</span> {item.seller_name || item.seller_roll_no}{' '}
                        <span className="font-mono text-[10px]">({item.seller_roll_no})</span>
                      </p>
                      {item.status === 'IN_PROGRESS' && (
                        <p className="text-amber-800 font-medium">
                          <span className="font-semibold">Deal In Progress:</span> Buyer {item.buyer_name || item.buyer_roll_no}{' '}
                          <span className="font-mono text-[10px]">({item.buyer_roll_no})</span>
                        </p>
                      )}
                      {item.status === 'SOLD' && item.buyer_name && (
                        <p className="text-slate-700">
                          <span className="font-semibold">Purchased by:</span> {item.buyer_name}{' '}
                          <span className="font-mono text-[10px]">({item.buyer_roll_no})</span>
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="pt-2 border-t border-academic-border/60">
                    {item.status === 'AVAILABLE' ? (
                      isSeller ? (
                        <span className="block text-center text-xs font-semibold text-academic-muted py-2 bg-academic-secondary/60 rounded-lg">
                          Your Active Listing
                        </span>
                      ) : (
                        <div className="grid grid-cols-2 gap-2">
                          <button
                            onClick={() => openInquiryModal(item)}
                            className="py-2.5 rounded-lg border border-academic-border bg-academic-secondary hover:bg-academic-border/60 text-academic-primary font-semibold text-xs transition-all flex items-center justify-center space-x-1"
                            title="Send inquiry to seller"
                          >
                            <Mail className="w-3.5 h-3.5 text-academic-muted" />
                            <span>Ask Seller</span>
                          </button>

                          <button
                            onClick={() => openBuyModal(item)}
                            className="py-2.5 rounded-lg bg-academic-burgundy text-white font-semibold text-xs shadow-xs hover:bg-academic-burgundy/90 transition-all flex items-center justify-center space-x-1"
                          >
                            <ShoppingBag className="w-3.5 h-3.5" />
                            <span>Request to Buy</span>
                          </button>
                        </div>
                      )
                    ) : item.status === 'IN_PROGRESS' ? (
                      isSeller ? (
                        <div className="space-y-2">
                          <div className="p-2 bg-amber-50 border border-amber-200 rounded text-[11px] text-amber-900 leading-snug">
                            <strong>{item.buyer_name || item.buyer_roll_no}</strong> claimed this item. Coordinate in person and confirm once payment & handover are complete.
                          </div>
                          <div className="grid grid-cols-2 gap-2">
                            <button
                              onClick={() => openCancelModal(item)}
                              className="py-2 rounded-lg border border-rose-300 text-rose-700 bg-rose-50/50 hover:bg-rose-100 font-semibold text-xs transition-all"
                            >
                              Cancel Deal
                            </button>
                            <button
                              onClick={() => openSellerConfirmModal(item)}
                              className="py-2 rounded-lg bg-emerald-700 text-white hover:bg-emerald-800 font-semibold text-xs shadow-xs transition-all flex items-center justify-center space-x-1"
                            >
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              <span>Confirm Payment</span>
                            </button>
                          </div>
                        </div>
                      ) : isBuyer ? (
                        <div className="space-y-2">
                          <div className="p-2 bg-amber-50 border border-amber-200 rounded text-[11px] text-amber-900 leading-snug">
                            You claimed this item! Please meet the seller on campus to pay and collect. The seller will mark it as Sold.
                          </div>
                          <div className="grid grid-cols-2 gap-2">
                            {item.seller_email && (
                              <a
                                href={`mailto:${item.seller_email}?subject=Coordination for ${encodeURIComponent(item.title)} on SkillSwap JKLU`}
                                className="py-2 rounded-lg border border-academic-border bg-academic-secondary hover:bg-academic-border/60 text-academic-primary font-semibold text-xs transition-all flex items-center justify-center space-x-1"
                              >
                                <Mail className="w-3.5 h-3.5 text-academic-muted" />
                                <span>Email Seller</span>
                              </a>
                            )}
                            <button
                              onClick={() => openCancelModal(item)}
                              className="py-2 rounded-lg border border-rose-300 text-rose-700 bg-rose-50/50 hover:bg-rose-100 font-semibold text-xs transition-all"
                            >
                              Cancel Request
                            </button>
                          </div>
                        </div>
                      ) : (
                        <span className="block text-center text-xs font-semibold text-amber-800 py-2 bg-amber-50 rounded-lg border border-amber-200">
                          ⏳ Deal In Progress (Reserved)
                        </span>
                      )
                    ) : item.status === 'SOLD' ? (
                      <span className="block text-center text-xs font-semibold text-slate-600 py-2 bg-slate-100 rounded-lg border border-slate-200">
                        {isBuyer ? '✓ You Purchased This Item' : isSeller ? '✓ Sold to Student' : 'Sold to Student'}
                      </span>
                    ) : (
                      <span className="block text-center text-xs text-gray-500 py-2 bg-gray-100 rounded-lg">
                        Removed by Seller
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )
      )}

      {/* Pagination */}
      <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />

      {/* Post Listing Modal */}
      <Modal isOpen={postModalOpen} onClose={() => setPostModalOpen(false)} title="Post Item on Campus Marketplace">
        <form onSubmit={handlePostSubmit} className="space-y-4 text-xs">
          {postError && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg">
              {postError}
            </div>
          )}

          <div>
            <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
              Item Title *
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Operating System Concepts (Silberschatz 10th Ed)"
              value={postForm.title}
              onChange={(e) => setPostForm({ ...postForm, title: e.target.value })}
              className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
                Category *
              </label>
              <select
                value={postForm.category}
                onChange={(e) => setPostForm({ ...postForm, category: e.target.value })}
                className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
              >
                <option value="Textbooks">Textbooks</option>
                <option value="Electronics">Electronics</option>
                <option value="Lab Equipment">Lab Equipment</option>
                <option value="Hostel Essentials">Hostel Essentials</option>
                <option value="Stationery">Stationery</option>
              </select>
            </div>

            <div>
              <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
                Item Condition *
              </label>
              <select
                value={postForm.item_condition}
                onChange={(e) => setPostForm({ ...postForm, item_condition: e.target.value })}
                className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
              >
                <option value="NEW">Brand New</option>
                <option value="LIKE_NEW">Like New</option>
                <option value="GOOD">Good Condition</option>
                <option value="FAIR">Fair Condition</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
              Price (INR ₹) *
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              required
              placeholder="450.00"
              value={postForm.price}
              onChange={(e) => setPostForm({ ...postForm, price: e.target.value })}
              className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
            />
          </div>

          <div>
            <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
              Description & Highlights *
            </label>
            <textarea
              rows={3}
              required
              placeholder="Describe edition, course relevance, included accessories, or condition details..."
              value={postForm.description}
              onChange={(e) => setPostForm({ ...postForm, description: e.target.value })}
              className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
            />
          </div>

          <div className="pt-2 flex justify-end space-x-2">
            <button
              type="button"
              onClick={() => setPostModalOpen(false)}
              className="px-4 py-2 rounded-lg border border-academic-border bg-academic-card text-academic-muted hover:bg-academic-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={postLoading}
              className="px-4 py-2 rounded-lg bg-academic-burgundy text-white font-semibold shadow-xs hover:bg-academic-burgundy/90 disabled:opacity-50"
            >
              {postLoading ? 'Posting...' : 'Publish Listing'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Send Inquiry Modal */}
      <Modal
        isOpen={inquiryModalOpen}
        onClose={() => setInquiryModalOpen(false)}
        title={`Send Inquiry: ${inquiryTarget?.title}`}
      >
        <form onSubmit={handleInquirySubmit} className="space-y-4 text-xs">
          {inquiryError && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg">
              {inquiryError}
            </div>
          )}

          {inquirySuccess && (
            <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>{inquirySuccess}</span>
            </div>
          )}

          {/* Product Details Header */}
          <div className="bg-academic-secondary/60 rounded-xl p-3.5 border border-academic-border space-y-1">
            <div className="flex justify-between items-start">
              <div>
                <h4 className="font-serif font-bold text-base text-academic-primary">{inquiryTarget?.title}</h4>
                <p className="text-[11px] text-academic-muted">Category: {inquiryTarget?.category} • {inquiryTarget?.item_condition}</p>
              </div>
              <span className="font-serif font-bold text-base text-academic-burgundy">
                ₹ {inquiryTarget ? parseFloat(inquiryTarget.price).toFixed(2) : '0.00'}
              </span>
            </div>
          </div>

          {/* Seller Contact Info */}
          <div className="bg-academic-card border border-academic-border rounded-xl p-3 space-y-1 text-academic-muted">
            <p className="font-semibold text-academic-primary">Seller:</p>
            <p>Name: <span className="font-medium text-academic-primary">{inquiryTarget?.seller_name}</span> ({inquiryTarget?.seller_roll_no})</p>
            <p>Official Email: <span className="font-mono text-academic-primary">{inquiryTarget?.seller_email || 'Verified JKLU Student'}</span></p>
          </div>

          <div>
            <label className="block font-semibold text-academic-primary mb-1 uppercase tracking-wider">
              Your Message to Seller *
            </label>
            <textarea
              rows={4}
              required
              placeholder="Ask about item condition, edition, meeting location on campus..."
              value={inquiryMessage}
              onChange={(e) => setInquiryMessage(e.target.value)}
              className="w-full p-2.5 rounded-lg border border-academic-border bg-academic-bg text-academic-primary focus:outline-none focus:ring-1 focus:ring-academic-burgundy"
            />
            <p className="text-[10px] text-academic-muted mt-1">
              Submitting an inquiry notifies the seller via in-app notification and email. It does not mark the item as sold.
            </p>
          </div>

          <div className="pt-2 flex justify-end space-x-2">
            <button
              type="button"
              onClick={() => setInquiryModalOpen(false)}
              className="px-4 py-2 rounded-lg border border-academic-border bg-academic-card text-academic-muted hover:bg-academic-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={inquiryLoading || !!inquirySuccess}
              className="px-4 py-2 rounded-lg bg-academic-burgundy text-white font-semibold shadow-xs hover:bg-academic-burgundy/90 disabled:opacity-50 flex items-center space-x-1.5"
            >
              <Send className="w-3.5 h-3.5" />
              <span>{inquiryLoading ? 'Sending...' : 'Send Inquiry'}</span>
            </button>
          </div>
        </form>
      </Modal>

      {/* Buy Request Modal */}
      <Modal isOpen={buyModalOpen} onClose={() => setBuyModalOpen(false)} title={`Purchase Reservation: ${targetListing?.title}`}>
        <div className="space-y-4 text-xs">
          {buyError && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg">
              {buyError}
            </div>
          )}

          {buySuccess && (
            <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>{buySuccess}</span>
            </div>
          )}

          {/* Item Details */}
          <div className="bg-academic-secondary/60 rounded-xl p-4 space-y-2 border border-academic-border">
            <div className="flex justify-between items-start">
              <div>
                <h4 className="font-serif font-bold text-base text-academic-primary">{targetListing?.title}</h4>
                <p className="text-[11px] text-academic-muted uppercase font-semibold mt-0.5">
                  {targetListing?.category} • Condition: {targetListing?.item_condition}
                </p>
              </div>
              <div className="text-right shrink-0">
                <span className="text-xl font-bold font-serif text-academic-burgundy block">
                  ₹ {targetListing ? parseFloat(targetListing.price).toFixed(2) : '0.00'}
                </span>
                {targetListing?.original_price_text && (
                  <span className="text-[10px] text-academic-muted font-mono block">
                    ({targetListing.original_price_text})
                  </span>
                )}
              </div>
            </div>
            <p className="text-academic-muted text-xs leading-relaxed pt-1 border-t border-academic-border/60">
              {targetListing?.description}
            </p>
          </div>

          {/* Seller Information Box */}
          <div className="bg-academic-card border border-academic-border rounded-xl p-3.5 space-y-2 text-xs">
            <p className="font-semibold text-academic-primary flex items-center space-x-1.5">
              <User className="w-3.5 h-3.5 text-academic-burgundy" />
              <span>Seller Information</span>
            </p>
            <div className="text-academic-muted space-y-1">
              <p>Name: <span className="font-medium text-academic-primary">{targetListing?.seller_name || 'JKLU Student'}</span></p>
              <p>Roll No: <span className="font-mono text-academic-primary">{targetListing?.seller_roll_no}</span></p>
              <p>
                Official Email:{' '}
                {targetListing?.seller_email ? (
                  <a href={`mailto:${targetListing.seller_email}`} className="text-academic-burgundy hover:underline font-mono">
                    {targetListing.seller_email}
                  </a>
                ) : (
                  <span className="text-academic-muted font-mono">Verified JKLU Email</span>
                )}
              </p>
            </div>
          </div>

          {/* Two-step Process Notice */}
          <div className="p-3 bg-amber-50 border border-amber-200 text-amber-900 rounded-lg space-y-1.5">
            <p className="font-semibold flex items-center space-x-1.5 text-xs">
              <Clock className="w-3.5 h-3.5 text-amber-700" />
              <span>How Peer Marketplace Works:</span>
            </p>
            <ol className="list-decimal list-inside text-[11px] text-amber-800 space-y-1">
              <li><strong>Reserve item:</strong> Clicking submit puts this item <em>In Progress</em>, reserving it for you.</li>
              <li><strong>Meet on campus:</strong> Coordinate directly with the seller to inspect and pay (Cash/UPI).</li>
              <li><strong>Seller confirms:</strong> Once paid and handed over, the seller confirms receipt to mark it as <em>Sold</em>.</li>
            </ol>
          </div>

          {/* Confirmation Checkbox */}
          <div className="p-3 rounded-lg border border-academic-border bg-academic-secondary/30">
            <label className="flex items-start space-x-2.5 cursor-pointer">
              <input
                type="checkbox"
                checked={buyConfirmed}
                onChange={(e) => setBuyConfirmed(e.target.checked)}
                className="mt-0.5 w-4 h-4 text-academic-burgundy rounded border-academic-border focus:ring-academic-burgundy"
              />
              <span className="text-xs text-academic-primary font-medium">
                Yes, I understand and want to initiate this reservation request with {targetListing?.seller_name || targetListing?.seller_roll_no}.
              </span>
            </label>
          </div>

          <div className="pt-2 flex justify-end space-x-2">
            <button
              type="button"
              onClick={() => setBuyModalOpen(false)}
              className="px-4 py-2 rounded-lg border border-academic-border bg-academic-card text-academic-muted hover:bg-academic-secondary"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleBuyConfirm}
              disabled={buyLoading || !buyConfirmed || !!buySuccess}
              className="px-4 py-2 rounded-lg bg-academic-burgundy text-white font-semibold shadow-xs hover:bg-academic-burgundy/90 disabled:opacity-50 flex items-center space-x-1.5"
            >
              <ShoppingBag className="w-3.5 h-3.5" />
              <span>{buyLoading ? 'Submitting...' : 'Submit Buy Request'}</span>
            </button>
          </div>
        </div>
      </Modal>

      {/* Seller Confirm Payment Modal */}
      <Modal
        isOpen={sellerModalOpen}
        onClose={() => setSellerModalOpen(false)}
        title="Confirm Payment & Item Handover"
      >
        <div className="space-y-4 text-xs">
          {sellerError && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg">
              {sellerError}
            </div>
          )}

          <div className="p-3.5 bg-academic-secondary/60 rounded-xl border border-academic-border space-y-2">
            <h4 className="font-serif font-bold text-base text-academic-primary">{sellerTarget?.title}</h4>
            <div className="text-academic-muted space-y-1">
              <p>Amount: <strong className="text-academic-burgundy">₹ {sellerTarget ? parseFloat(sellerTarget.price).toFixed(2) : '0.00'}</strong></p>
              <p>Buyer: <strong>{sellerTarget?.buyer_name || sellerTarget?.buyer_roll_no}</strong> ({sellerTarget?.buyer_roll_no})</p>
            </div>
          </div>

          <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-900 rounded-lg text-xs leading-relaxed">
            Please confirm only after you have physically received payment and handed the item over to the student buyer. This will permanently mark the item as <strong>SOLD</strong>.
          </div>

          <div className="pt-2 flex justify-end space-x-2">
            <button
              type="button"
              onClick={() => setSellerModalOpen(false)}
              className="px-4 py-2 rounded-lg border border-academic-border bg-academic-card text-academic-muted hover:bg-academic-secondary"
            >
              Not Yet
            </button>
            <button
              type="button"
              onClick={handleSellerConfirm}
              disabled={sellerLoading}
              className="px-4 py-2 rounded-lg bg-emerald-700 text-white font-semibold shadow-xs hover:bg-emerald-800 disabled:opacity-50 flex items-center space-x-1.5"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>{sellerLoading ? 'Confirming...' : 'Yes, Confirm Payment Received'}</span>
            </button>
          </div>
        </div>
      </Modal>

      {/* Cancel Deal Modal */}
      <Modal
        isOpen={cancelModalOpen}
        onClose={() => setCancelModalOpen(false)}
        title="Cancel In-Progress Deal"
      >
        <div className="space-y-4 text-xs">
          {cancelError && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg">
              {cancelError}
            </div>
          )}

          <p className="text-academic-primary">
            Are you sure you want to cancel the deal for <strong className="font-serif">{cancelTarget?.title}</strong>?
          </p>

          <p className="text-academic-muted leading-relaxed">
            The deal will be released, and the listing will immediately return to <strong>AVAILABLE</strong> status so other students can explore and request it.
          </p>

          <div className="pt-2 flex justify-end space-x-2">
            <button
              type="button"
              onClick={() => setCancelModalOpen(false)}
              className="px-4 py-2 rounded-lg border border-academic-border bg-academic-card text-academic-muted hover:bg-academic-secondary"
            >
              Keep Deal Active
            </button>
            <button
              type="button"
              onClick={handleCancelSale}
              disabled={cancelLoading}
              className="px-4 py-2 rounded-lg bg-rose-700 text-white font-semibold shadow-xs hover:bg-rose-800 disabled:opacity-50"
            >
              {cancelLoading ? 'Releasing...' : 'Confirm Release to Available'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
