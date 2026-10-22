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

  // Purchase Modal
  const [buyModalOpen, setBuyModalOpen] = useState(false);
  const [targetListing, setTargetListing] = useState(null);
  const [buyLoading, setBuyLoading] = useState(false);
  const [buySuccess, setBuySuccess] = useState('');
  const [buyError, setBuyError] = useState('');

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
      setBuySuccess('Purchase successful! The item is now marked SOLD.');
      setTimeout(() => {
        setBuyModalOpen(false);
        fetchListings();
      }, 1500);
    } catch (err) {
      setBuyError(err.response?.data?.error?.message || 'Purchase could not be completed.');
    } finally {
      setBuyLoading(false);
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
                    <p className="text-xl font-bold font-serif text-academic-burgundy mt-1">
                      ₹ {parseFloat(item.price).toFixed(2)}
                    </p>
                  </div>

                  <p className="text-xs text-academic-muted leading-relaxed line-clamp-3">
                    {item.description}
                  </p>

                  {/* Seller / Buyer details */}
                  <div className="bg-academic-secondary/50 rounded-lg p-2.5 text-xs text-academic-muted space-y-1">
                    <p>
                      <span className="font-semibold text-academic-primary">Seller:</span> {item.seller_name}{' '}
                      <span className="font-mono text-[10px]">({item.seller_roll_no})</span>
                    </p>
                    {item.status === 'SOLD' && item.buyer_name && (
                      <p className="text-slate-700">
                        <span className="font-semibold">Purchased by:</span> {item.buyer_name}{' '}
                        <span className="font-mono text-[10px]">({item.buyer_roll_no})</span>
                      </p>
                    )}
                  </div>
                </div>

                {/* Purchase Button */}
                <div className="pt-2 border-t border-academic-border/60">
                  {item.status === 'AVAILABLE' ? (
                    isSeller ? (
                      <span className="block text-center text-xs font-semibold text-academic-muted py-2 bg-academic-secondary/60 rounded-lg">
                        Your Active Listing
                      </span>
                    ) : (
                      <button
                        onClick={() => openBuyModal(item)}
                        className="w-full py-2.5 rounded-lg bg-emerald-700 text-white font-semibold text-xs shadow-xs hover:bg-emerald-800 transition-all flex items-center justify-center space-x-1.5"
                      >
                        <ShoppingBag className="w-3.5 h-3.5" />
                        <span>Purchase Item (₹ {parseFloat(item.price).toFixed(0)})</span>
                      </button>
                    )
                  ) : item.status === 'SOLD' ? (
                    <span className="block text-center text-xs font-semibold text-slate-600 py-2 bg-slate-100 rounded-lg border border-slate-200">
                      {isBuyer ? '✓ You Purchased This Item' : 'Sold to Student'}
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

      {/* Buy Confirmation Modal */}
      <Modal isOpen={buyModalOpen} onClose={() => setBuyModalOpen(false)} title="Confirm Academic Marketplace Purchase">
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

          <div className="bg-academic-secondary/60 rounded-xl p-4 space-y-2 border border-academic-border">
            <h4 className="font-serif font-bold text-base text-academic-primary">{targetListing?.title}</h4>
            <p className="text-academic-muted">{targetListing?.description}</p>
            <div className="pt-2 border-t border-academic-border/70 flex justify-between items-center">
              <span className="font-semibold text-academic-muted">Total Price:</span>
              <span className="text-xl font-bold font-serif text-academic-burgundy">
                ₹ {targetListing ? parseFloat(targetListing.price).toFixed(2) : '0.00'}
              </span>
            </div>
          </div>

          <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-3 text-indigo-900 space-y-1">
            <p className="font-semibold flex items-center space-x-1">
              <ShieldCheck className="w-3.5 h-3.5 text-indigo-600" />
              <span>Safe Concurrency Checkout Guarantee</span>
            </p>
            <p className="text-[11px] text-indigo-800">
              Purchases are executed atomically in MySQL using conditional updates. If another peer claims this item concurrently, race conditions are blocked.
            </p>
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
              disabled={buyLoading || !!buySuccess}
              className="px-4 py-2 rounded-lg bg-emerald-700 text-white font-semibold shadow-xs hover:bg-emerald-800 disabled:opacity-50"
            >
              {buyLoading ? 'Processing...' : 'Confirm & Buy'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
