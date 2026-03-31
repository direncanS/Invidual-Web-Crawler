import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { listJobs } from '../api/crawl';
import { extractApiError } from '../api/client';
import Card from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import Button from '../components/ui/Button';
import Spinner from '../components/ui/Spinner';
import EmptyState from '../components/ui/EmptyState';
import ErrorBanner from '../components/ui/ErrorBanner';
import { Plus, Globe, Eye } from 'lucide-react';

export default function Dashboard() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    try {
      const res = await listJobs();
      const sorted = (res.data.jobs || []).sort(
        (a, b) => new Date(b.created_at) - new Date(a.created_at)
      );
      setJobs(sorted);
    } catch (err) {
      setError(extractApiError(err));
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size={32} />
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <Button onClick={() => navigate('/crawl/new')}>
          <Plus size={16} />
          New Crawl
        </Button>
      </div>

      <ErrorBanner message={error} />

      {jobs.length === 0 ? (
        <Card>
          <EmptyState
            icon={Globe}
            title="No crawl jobs yet"
            description="Start your first web crawl to discover and analyze PDFs."
          >
            <Button onClick={() => navigate('/crawl/new')}>
              <Plus size={16} />
              New Crawl
            </Button>
          </EmptyState>
        </Card>
      ) : (
        <div className="space-y-3">
          {jobs.map((job) => (
            <Card key={job.id} className="hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-3">
                    <Globe size={18} className="shrink-0 text-gray-400" />
                    <span className="truncate text-sm font-medium text-gray-900">
                      {job.start_url}
                    </span>
                    <Badge status={job.status} />
                  </div>
                  <div className="mt-1 ml-8 flex gap-4 text-xs text-gray-500">
                    <span>Depth: {job.depth}</span>
                    <span>{new Date(job.created_at).toLocaleString()}</span>
                  </div>
                </div>
                <Link to={`/jobs/${job.id}`}>
                  <Button variant="secondary" className="shrink-0">
                    <Eye size={14} />
                    View Details
                  </Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
