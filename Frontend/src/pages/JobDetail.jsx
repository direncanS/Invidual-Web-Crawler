import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getJob, getJobPages, getJobPdfs } from '../api/crawl';
import { extractApiError } from '../api/client';
import { usePolling } from '../hooks/usePolling';
import Card from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import Table from '../components/ui/Table';
import Spinner from '../components/ui/Spinner';
import EmptyState from '../components/ui/EmptyState';
import ErrorBanner from '../components/ui/ErrorBanner';
import Button from '../components/ui/Button';
import { ArrowLeft, Globe, FileText, ExternalLink, BarChart3 } from 'lucide-react';

export default function JobDetail() {
  const { jobId } = useParams();
  const [job, setJob] = useState(null);
  const [pages, setPages] = useState([]);
  const [pdfs, setPdfs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchData = useCallback(async () => {
    try {
      const [jobRes, pagesRes, pdfsRes] = await Promise.all([
        getJob(jobId),
        getJobPages(jobId),
        getJobPdfs(jobId),
      ]);
      setJob(jobRes.data);
      setPages(Array.isArray(pagesRes.data) ? pagesRes.data : pagesRes.data.pages || []);
      setPdfs(pdfsRes.data.pdfs || []);
    } catch (err) {
      setError(extractApiError(err));
    } finally {
      setLoading(false);
    }
  }, [jobId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const isActive = job?.status === 'queued' || job?.status === 'running';
  usePolling(fetchData, 2000, isActive);

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size={32} />
      </div>
    );
  }

  if (error) {
    return <ErrorBanner message={error} />;
  }

  return (
    <div>
      <Link to="/dashboard" className="mb-4 inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700">
        <ArrowLeft size={14} />
        Back to Dashboard
      </Link>

      <Card className="mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Job Details</h1>
            <div className="mt-2 space-y-1 text-sm text-gray-600">
              <p><span className="font-medium">URL:</span> {job?.start_url}</p>
              <p><span className="font-medium">Depth:</span> {job?.depth}</p>
              <p><span className="font-medium">Started:</span> {job?.created_at ? new Date(job.created_at).toLocaleString() : '—'}</p>
              {job?.finished_at && (
                <p><span className="font-medium">Finished:</span> {new Date(job.finished_at).toLocaleString()}</p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge status={job?.status} />
            {isActive && <Spinner size={16} />}
          </div>
        </div>
      </Card>

      {/* Pages */}
      <div className="mb-6">
        <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold text-gray-900">
          <Globe size={18} />
          Crawled Pages ({pages.length})
        </h2>
        {pages.length === 0 ? (
          <Card>
            <EmptyState icon={Globe} title="No pages crawled yet" description={isActive ? 'Crawling in progress...' : 'No pages were found.'} />
          </Card>
        ) : (
          <Table headers={['URL', 'Depth', 'Status', 'Fetched At']}>
            {pages.map((p) => (
              <tr key={p.id}>
                <td className="max-w-xs truncate px-4 py-3 text-sm text-gray-900">{p.url}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{p.depth_level}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{p.status_code}</td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {p.fetched_at ? new Date(p.fetched_at).toLocaleString() : '—'}
                </td>
              </tr>
            ))}
          </Table>
        )}
      </div>

      {/* PDFs */}
      <div>
        <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold text-gray-900">
          <FileText size={18} />
          Discovered PDFs ({pdfs.length})
        </h2>
        {pdfs.length === 0 ? (
          <Card>
            <EmptyState icon={FileText} title="No PDFs found" description={isActive ? 'Still crawling...' : 'No PDF documents were discovered.'} />
          </Card>
        ) : (
          <Table headers={['Source URL', 'Downloaded', 'Actions']}>
            {pdfs.map((pdf) => (
              <tr key={pdf.id}>
                <td className="max-w-xs truncate px-4 py-3 text-sm text-gray-900">{pdf.source_url}</td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {pdf.downloaded_at ? new Date(pdf.downloaded_at).toLocaleString() : '—'}
                </td>
                <td className="px-4 py-3">
                  <Link to={`/pdfs/${pdf.id}`}>
                    <Button variant="secondary" className="text-xs">
                      <BarChart3 size={12} />
                      View Stats
                    </Button>
                  </Link>
                </td>
              </tr>
            ))}
          </Table>
        )}
      </div>
    </div>
  );
}
