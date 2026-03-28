import { Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import ProtectedRoute from './components/layout/ProtectedRoute';

import Landing from './pages/Landing';
import Register from './pages/Register';
import Login from './pages/Login';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import NewCrawl from './pages/NewCrawl';
import JobDetail from './pages/JobDetail';
import PdfStats from './pages/PdfStats';
import Search from './pages/Search';
import Wordclouds from './pages/Wordclouds';
import NotFound from './pages/NotFound';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/register" element={<Layout><Register /></Layout>} />
      <Route path="/login" element={<Layout><Login /></Layout>} />
      <Route path="/forgot-password" element={<Layout><ForgotPassword /></Layout>} />
      <Route path="/reset-password" element={<Layout><ResetPassword /></Layout>} />
      <Route
        path="/dashboard"
        element={<ProtectedRoute><Layout><Dashboard /></Layout></ProtectedRoute>}
      />
      <Route
        path="/profile"
        element={<ProtectedRoute><Layout><Profile /></Layout></ProtectedRoute>}
      />
      <Route
        path="/crawl/new"
        element={<ProtectedRoute><Layout><NewCrawl /></Layout></ProtectedRoute>}
      />
      <Route
        path="/jobs/:jobId"
        element={<ProtectedRoute><Layout><JobDetail /></Layout></ProtectedRoute>}
      />
      <Route
        path="/pdfs/:pdfId"
        element={<ProtectedRoute><Layout><PdfStats /></Layout></ProtectedRoute>}
      />
      <Route
        path="/search"
        element={<ProtectedRoute><Layout><Search /></Layout></ProtectedRoute>}
      />
      <Route
        path="/wordclouds"
        element={<ProtectedRoute><Layout><Wordclouds /></Layout></ProtectedRoute>}
      />
      <Route path="*" element={<Layout><NotFound /></Layout>} />
    </Routes>
  );
}
