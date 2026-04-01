import { Link } from 'react-router-dom';
import { Home } from 'lucide-react';
import Button from '../components/ui/Button';

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <h1 className="text-6xl font-bold text-gray-900">404</h1>
      <p className="mt-2 text-lg text-gray-500">Page not found</p>
      <p className="mt-1 text-sm text-gray-400">The page you're looking for doesn't exist.</p>
      <Link to="/" className="mt-6">
        <Button>
          <Home size={16} />
          Go Home
        </Button>
      </Link>
    </div>
  );
}
