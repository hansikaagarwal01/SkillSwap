import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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
} from 'lucide-react';

export const Marketplace = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState('ALL'); // ALL, MINE, PURCHASES
  const [listings, setListings] = useState([]);
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

  const fetchListings = async () => {
    setLoading(true);
    try {
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
      setListings(resp.data.items);
      setTotal(resp.data.total);
      setTotalPages(resp.data.total_pages);
    } catch (err) {
      console.error('Failed to load listings', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchListings();
  }, [page, activeTab, category, itemCondition]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchListings();
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
      fetchListings();
    } catch (err) {
      setPostError(err.response?.data?.error?.message || 'Failed to create listing.');
    } finally {
      setPostLoading(false);
    }
  };

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
        fetchListings();
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
      fetchListings();
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
      fetchListings();
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
            Exchange course textbooks, lab supplies, calculators, and electronics safely between verified students.
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

      {/* Tabs and Filters */}
      <div className="bg-academic-card border border-academic-border rounded-xl p-4 shadow-xs space-y-4">
        {/* Navigation Tabs */}
        <div className="flex items-center space-x-1 border-b border-academic-border/70 pb-3">
          {[
            { id: 'ALL', label: 'Explore Marketplace' },
            ...(user
              ? [
                  { id: 'MINE', label: 'My Listings' },
                  { id: 'PURCHASES', label: 'My Purchases' },
                ]
              : []),
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => {
                setActiveTab(tab.id);
                setPage(1);
              }}
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

      {/* Listings Grid */}
      {loading ? (
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
                        <a
                          href={`mailto:${item.seller_roll_no.toLowerCase()}@jklu.edu.in?subject=Inquiry regarding ${encodeURIComponent(item.title)} on SkillSwap JKLU`}
                          className="py-2.5 rounded-lg border border-academic-border bg-academic-secondary hover:bg-academic-border/60 text-academic-primary font-semibold text-xs transition-all flex items-center justify-center space-x-1"
                          title="Contact seller via official JKLU email before purchasing"
                        >
                          <Mail className="w-3.5 h-3.5 text-academic-muted" />
                          <span>Ask Seller</span>
                        </a>

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
                          <a
                            href={`mailto:${item.seller_roll_no.toLowerCase()}@jklu.edu.in?subject=Coordination for ${encodeURIComponent(item.title)} on SkillSwap JKLU`}
                            className="py-2 rounded-lg border border-academic-border bg-academic-secondary hover:bg-academic-border/60 text-academic-primary font-semibold text-xs transition-all flex items-center justify-center space-x-1"
                          >
                            <Mail className="w-3.5 h-3.5 text-academic-muted" />
                            <span>Email Seller</span>
                          </a>
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

      {/* Buy Request Modal */}
      <Modal isOpen={buyModalOpen} onClose={() => setBuyModalOpen(false)} title={`Purchase Inquiry: ${targetListing?.title}`}>
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

          {/* Seller Information & Inquiry Box */}
          <div className="bg-academic-card border border-academic-border rounded-xl p-3.5 space-y-2 text-xs">
            <p className="font-semibold text-academic-primary flex items-center space-x-1.5">
              <User className="w-3.5 h-3.5 text-academic-burgundy" />
              <span>Seller Information</span>
            </p>
            <div className="text-academic-muted space-y-1">
              <p>Name: <span className="font-medium text-academic-primary">{targetListing?.seller_name || 'JKLU Student'}</span></p>
              <p>Roll No: <span className="font-mono text-academic-primary">{targetListing?.seller_roll_no}</span></p>
              <p>Official Email: <a href={`mailto:${targetListing?.seller_roll_no?.toLowerCase()}@jklu.edu.in`} className="text-academic-burgundy hover:underline font-mono">{targetListing?.seller_roll_no?.toLowerCase()}@jklu.edu.in</a></p>
            </div>
            <div className="pt-2">
              <a
                href={`mailto:${targetListing?.seller_roll_no?.toLowerCase()}@jklu.edu.in?subject=Inquiry regarding ${encodeURIComponent(targetListing?.title || '')} on SkillSwap JKLU&body=Hi ${encodeURIComponent(targetListing?.seller_name || '')},%0D%0A%0D%0AI saw your listing for "${encodeURIComponent(targetListing?.title || '')}" on SkillSwap JKLU for ₹${targetListing?.price}. Is this item still available and can we meet on campus?%0D%0A%0D%0AThanks,%0D%0A${encodeURIComponent(user?.name || '')} (${user?.roll_no})`}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center space-x-1.5 text-xs font-semibold text-academic-burgundy hover:underline"
              >
                <Mail className="w-3.5 h-3.5" />
                <span>Ask / Inquire with Seller via Email First &rarr;</span>
              </a>
            </div>
          </div>

          {/* Two-step Process Notice */}
          <div className="p-3 bg-amber-50 border border-amber-200 text-amber-900 rounded-lg space-y-1.5">
            <p className="font-semibold flex items-center space-x-1.5 text-xs">
              <Clock className="w-3.5 h-3.5 text-amber-700" />
              <span>How Peer Marketplace Works:</span>
            </p>
            <ol className="list-decimal list-inside text-[11px] text-amber-800 space-y-1">
              <li><strong>Reserve item:</strong> Clicking confirm puts this item <em>In Progress</em>, holding it for you.</li>
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
                Yes, I understand and want to initiate this purchase request with {targetListing?.seller_roll_no}.
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
