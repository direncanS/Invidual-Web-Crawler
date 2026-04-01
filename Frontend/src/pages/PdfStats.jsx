import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getPdf, downloadPdf, getTopWords } from '../api/pdfs';
import { extractApiError } from '../api/client';
import Card from '../components/ui/Card';
import Spinner from '../components/ui/Spinner';
import Button from '../components/ui/Button';
import ErrorBanner from '../components/ui/ErrorBanner';
import { ArrowLeft, Download, BarChart3, Cloud } from 'lucide-react';

export default function PdfStats() {
  const { pdfId } = useParams();
  const [pdf, setPdf] = useState(null);
  const [words, setWords] = useState(null);
  const [loading, setLoading] = useState(true);
  const [wordsLoading, setWordsLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloading, setDownloading] = useState(false);

  const fetchWords = useCallback(async () => {
    try {
      const res = await getTopWords(pdfId);
      setWords(res.data.words || []);
      setWordsLoading(false);
    } catch (err) {
      if (err.response?.status === 409) {
        setTimeout(fetchWords, 2000);
      } else {
        setError(extractApiError(err));
        setWordsLoading(false);
      }
    }
  }, [pdfId]);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await getPdf(pdfId);
        setPdf(res.data);
      } catch (err) {
        setError(extractApiError(err));
      } finally {
        setLoading(false);
      }
    };
    load();
    fetchWords();
  }, [pdfId, fetchWords]);

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const res = await downloadPdf(pdfId);
      const url = URL.createObjectURL(res.data);
      const a = document.createElement('a');
      a.href = url;
      a.download = pdf?.source_url?.split('/').pop() || 'document.pdf';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(extractApiError(err));
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size={32} />
      </div>
    );
  }

  const maxCount = words?.length ? Math.max(...words.map((w) => w.count)) : 1;

  return (
    <div className="mx-auto max-w-2xl">
      <Link to="/dashboard" className="mb-4 inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700">
        <ArrowLeft size={14} />
        Back to Dashboard
      </Link>

      <ErrorBanner message={error} />

      <Card className="mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">PDF Statistics</h1>
            <p className="mt-1 text-sm text-gray-500 break-all">{pdf?.source_url}</p>
            {pdf?.downloaded_at && (
              <p className="mt-1 text-xs text-gray-400">Downloaded: {new Date(pdf.downloaded_at).toLocaleString()}</p>
            )}
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={handleDownload} loading={downloading}>
              <Download size={14} />
              Download
            </Button>
            <Link to={`/wordclouds?pdf=${pdfId}`}>
              <Button variant="secondary">
                <Cloud size={14} />
                Wordcloud
              </Button>
            </Link>
          </div>
        </div>
      </Card>

      <Card>
        <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-gray-900">
          <BarChart3 size={18} />
          Top 10 Words
        </h2>
        {wordsLoading ? (
          <div className="flex items-center justify-center py-8">
            <Spinner size={24} />
            <span className="ml-2 text-sm text-gray-500">Analyzing PDF...</span>
          </div>
        ) : words?.length === 0 ? (
          <p className="py-4 text-sm text-gray-500">No word statistics available.</p>
        ) : (
          <div className="space-y-3">
            {words.map((w, i) => (
              <div key={w.word} className="flex items-center gap-3">
                <span className="w-6 text-right text-sm font-medium text-gray-400">{i + 1}</span>
                <span className="w-24 text-sm font-medium text-gray-900">{w.word}</span>
                <div className="flex-1">
                  <div className="h-6 rounded-full bg-gray-100">
                    <div
                      className="h-6 rounded-full bg-indigo-500 transition-all"
                      style={{ width: `${(w.count / maxCount) * 100}%` }}
                    />
                  </div>
                </div>
                <span className="w-12 text-right text-sm text-gray-500">{w.count}</span>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
