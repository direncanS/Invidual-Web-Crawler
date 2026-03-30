import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Globe, LogOut, User, LayoutDashboard, Search, Cloud } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navLink = (to, label, Icon) => {
    const active = location.pathname === to;
    return (
      <Link
        to={to}
        className={`inline-flex items-center gap-1.5 px-3 py-2 text-sm font-medium rounded-lg transition-colors
          ${active ? 'bg-indigo-50 text-indigo-700' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'}`}
      >
        <Icon size={16} />
        {label}
      </Link>
    );
  };

  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link to={isAuthenticated ? '/dashboard' : '/'} className="flex items-center gap-2 text-lg font-bold text-indigo-600">
          <Globe size={24} />
          <span>WebCrawler</span>
        </Link>

        {isAuthenticated && (
          <div className="flex items-center gap-1">
            {navLink('/dashboard', 'Dashboard', LayoutDashboard)}
            {navLink('/search', 'Search', Search)}
            {navLink('/wordclouds', 'Wordclouds', Cloud)}
            {navLink('/profile', 'Profile', User)}
            <button
              onClick={handleLogout}
              className="inline-flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <LogOut size={16} />
              Logout
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}
