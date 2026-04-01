import { useState } from 'react';
import { Link } from 'react-router-dom';
import { searchTopWords } from '../api/search';
import { downloadPdf } from '../api/pdfs';
import { extractApiError } from '../api/client';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import Table from '../components/ui/Table';
import Spinner from '../components/ui/Spinner';
import EmptyState from '../components/ui/EmptyState';
import ErrorBanner from '../components/ui/ErrorBanner';
import { Search as SearchIcon, BarChart3, Download, FileText } from 'lucide-react';

export default function Search() {
  const [word, setWord] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [downloadingId, setDownloadingId] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!word.trim()) return;

    setLoading(true);
    setError('');
    try {
      const res = await searchTopWords(word.trim());
      setResults(res.data.results || []);
    } catch (err) {
      setError(extractApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (pdf) => {
    setDownloadingId(pdf.id);
    try {
      const res = await downloadPdf(pdf.id);
      const url = URL.createObjectURL(res.data);
      const a = document.createElement('a');
      a.href = url;
      a.download = pdf.source_url?.split('/').pop() || 'document.pdf';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(extractApiError(err));
    } finally {
      setDownloadingId(null);
    }
  };

  return (
    <div>
      <h1 className="mb-2 text-2xl font-bold text-gray-900">Search</h1>
      <p className="mb-6 text-sm text-gray-500">
        Search across the top-10 word statistics of your indexed PDFs.
      </p>

      <Card className="mb-6">
        <form onSubmit={handleSearch} className="flex gap-3">
          <div className="flex-1">
            <Input
              value={word}
              onChange={(e) => setWord(e.target.value)}
              placeholder="Enter a word to search..."
            />
          </div>
          <Button type="submit" loading={loading}>
            <SearchIcon size={16} />
            Search
          </Button>
        </form>
      </Card>

      <ErrorBanner message={error} />

      {loading && (
        <div className="flex justify-center py-8">
          <Spinner size={24} />
        </div>
      )}

      {results !== null && !loading && (
        results.length === 0 ? (
          <Card>
            <EmptyState
              icon={FileText}
              title="No PDFs found"
              description="No PDFs found with this word in their top-10 statistics."
            />
          </Card>
        ) : (
          <Table headers={['Source URL', 'Downloaded', 'Actions']}>
            {results.map((pdf) => (
              <tr key={pdf.id}>
                <td className="max-w-xs truncate px-4 py-3 text-sm text-gray-900">{pdf.source_url}</td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {pdf.downloaded_at ? new Date(pdf.downloaded_at).toLocaleString() : '—'}
                </td>
                <td className="px-4 py-3">
                  <div className="flex gap-2">
                    <Link to={`/pdfs/${pdf.id}`}>
                      <Button variant="secondary" className="text-xs">
                        <BarChart3 size={12} />
                        View Stats
                      </Button>
                    </Link>
                    <Button
                      variant="secondary"
                      className="text-xs"
                      onClick={() => handleDownload(pdf)}
                      loading={downloadingId === pdf.id}
                    >
                      <Download size={12} />
                      Download
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </Table>
        )
      )}
    </div>
  );
}
