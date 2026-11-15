import React, { Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { ErrorBoundary } from './components/ErrorBoundary';

// Code-split pages for performance and lazy chunk loading
const Home = React.lazy(() => import('./pages/Home').then(m => ({ default: m.Home })));
const Login = React.lazy(() => import('./pages/Login').then(m => ({ default: m.Login })));
const Register = React.lazy(() => import('./pages/Register').then(m => ({ default: m.Register })));
const Mentors = React.lazy(() => import('./pages/Mentors').then(m => ({ default: m.Mentors })));
const Skills = React.lazy(() => import('./pages/Skills').then(m => ({ default: m.Skills })));
const Sessions = React.lazy(() => import('./pages/Sessions').then(m => ({ default: m.Sessions })));
const Marketplace = React.lazy(() => import('./pages/Marketplace').then(m => ({ default: m.Marketplace })));
const Leaderboard = React.lazy(() => import('./pages/Leaderboard').then(m => ({ default: m.Leaderboard })));
const Analytics = React.lazy(() => import('./pages/Analytics').then(m => ({ default: m.Analytics })));
const Profile = React.lazy(() => import('./pages/Profile').then(m => ({ default: m.Profile })));
const Admin = React.lazy(() => import('./pages/Admin').then(m => ({ default: m.Admin })));
const VerifyEmail = React.lazy(() => import('./pages/VerifyEmail').then(m => ({ default: m.VerifyEmail })));

const PageLoader = () => (
  <div className="py-24 flex flex-col items-center justify-center text-center">
    <div className="w-8 h-8 border-2 border-academic-burgundy border-t-transparent rounded-full animate-spin mb-3"></div>
    <p className="text-xs text-academic-muted font-medium">Loading page...</p>
  </div>
);

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) {
    return <div className="py-20 text-center text-xs text-academic-muted">Authenticating user session...</div>;
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

const AdminRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) {
    return <div className="py-20 text-center text-xs text-academic-muted">Verifying administrator rights...</div>;
  }
  if (!user || user.role !== 'ADMIN') {
    return <Navigate to="/" replace />;
  }
  return children;
};

export default function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <BrowserRouter>
          <div className="flex flex-col min-h-screen bg-academic-bg text-academic-primary font-sans">
            <Navbar />

            <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8">
              <Suspense fallback={<PageLoader />}>
                <Routes>
                  {/* Public Routes */}
                  <Route path="/" element={<Home />} />
                  <Route path="/login" element={<Login />} />
                  <Route path="/register" element={<Register />} />
                  <Route path="/verify-email" element={<VerifyEmail />} />
                  <Route path="/mentors" element={<Mentors />} />
                  <Route path="/skills" element={<Skills />} />
                  <Route path="/marketplace" element={<Marketplace />} />
                  <Route path="/leaderboard" element={<Leaderboard />} />
                  <Route path="/analytics" element={<Analytics />} />

                  {/* Protected Routes */}
                  <Route
                    path="/sessions"
                    element={
                      <ProtectedRoute>
                        <Sessions />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/profile"
                    element={
                      <ProtectedRoute>
                        <Profile />
                      </ProtectedRoute>
                    }
                  />

                  {/* Admin Route */}
                  <Route
                    path="/admin"
                    element={
                      <AdminRoute>
                        <Admin />
                      </AdminRoute>
                    }
                  />

                  {/* Fallback */}
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </Suspense>
            </main>

            <Footer />
          </div>
        </BrowserRouter>
      </AuthProvider>
    </ErrorBoundary>
  );
}
