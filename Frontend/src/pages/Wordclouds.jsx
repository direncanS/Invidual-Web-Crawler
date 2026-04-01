import { useState, useEffect, useRef, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { listPdfs } from '../api/pdfs';
import { createSingle, createMulti, createInterval, getImage } from '../api/wordclouds';
import { extractApiError } from '../api/client';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Spinner from '../components/ui/Spinner';
import EmptyState from '../components/ui/EmptyState';
import ErrorBanner from '../components/ui/ErrorBanner';
import { Cloud, Image as ImageIcon, CheckSquare } from 'lucide-react';

const tabs = [
  { key: 'single', label: 'Single PDF' },
  { key: 'multi', label: 'Multiple PDFs' },
  { key: 'interval', label: 'Date Interval' },
];

export default function Wordclouds() {
  const [searchParams] = useSearchParams();
  const preselectedPdf = searchParams.get('pdf');

  const [activeTab, setActiveTab] = useState('single');
  const [pdfs, setPdfs] = useState([]);
  const [pdfsLoading, setPdfsLoading] = useState(true);

  // Single
  const [selectedPdf, setSelectedPdf] = useState(preselectedPdf || '');
  // Multi
  const [selectedPdfs, setSelectedPdfs] = useState([]);
  // Interval
  const [startDt, setStartDt] = useState('');
  const [endDt, setEndDt] = useState('');

  const [generating, setGenerating] = useState(false);
  const [imageUrl, setImageUrl] = useState(null);
  const [error, setError] = useState('');
  const imageUrlRef = useRef(null);

  useEffect(() => {
    listPdfs()
      .then((res) => setPdfs(res.data.pdfs || []))
      .catch(() => {})
      .finally(() => setPdfsLoading(false));
  }, []);

  // Cleanup blob URL
  useEffect(() => {
    return () => {
      if (imageUrlRef.current) URL.revokeObjectURL(imageUrlRef.current);
    };
  }, []);

  const clearImage = () => {
    if (imageUrlRef.current) {
      URL.revokeObjectURL(imageUrlRef.current);
      imageUrlRef.current = null;
    }
    setImageUrl(null);
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    clearImage();
    setError('');
  };

  const pollImage = useCallback(async (artifactId) => {
    try {
      const res = await getImage(artifactId);
      const url = URL.createObjectURL(res.data);
      imageUrlRef.current = url;
      setImageUrl(url);
      setGenerating(false);
    } catch (err) {
      if (err.response?.status === 404 || err.response?.status === 409) {
        setTimeout(() => pollImage(artifactId), 2000);
      } else {
        setError(extractApiError(err));
        setGenerating(false);
      }
    }
  }, []);

  const handleGenerate = async () => {
    setError('');
    clearImage();
    setGenerating(true);

    try {
      let res;
      if (activeTab === 'single') {
        if (!selectedPdf) { setError('Please select a PDF'); setGenerating(false); return; }
        res = await createSingle(selectedPdf);
      } else if (activeTab === 'multi') {
        if (selectedPdfs.length < 2) { setError('Please select at least 2 PDFs'); setGenerating(false); return; }
        res = await createMulti(selectedPdfs);
      } else {
        if (!startDt || !endDt) { setError('Please select both start and end dates'); setGenerating(false); return; }
        const startIso = new Date(startDt).toISOString();
        const endIso = new Date(endDt).toISOString();
        res = await createInterval(startIso, endIso);
      }
      pollImage(res.data.id);
    } catch (err) {
      setError(extractApiError(err));
      setGenerating(false);
    }
  };

  const togglePdf = (id) => {
    setSelectedPdfs((prev) =>
      prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]
    );
  };

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Word Clouds</h1>

      {/* Tabs */}
      <div className="mb-6 flex gap-1 rounded-lg bg-gray-100 p-1">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => handleTabChange(tab.key)}
            className={`flex-1 rounded-md px-4 py-2 text-sm font-medium transition-colors
              ${activeTab === tab.key ? 'bg-white text-gray-900 shadow' : 'text-gray-500 hover:text-gray-700'}`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <ErrorBanner message={error} />

      <Card className="mb-6">
        {activeTab === 'single' && (
          <div className="space-y-4">
            <p className="text-sm text-gray-500">Select from your available documents.</p>
            {pdfsLoading ? (
              <Spinner size={20} />
            ) : pdfs.length === 0 ? (
              <EmptyState icon={Cloud} title="No PDFs available" description="Crawl a website first to discover PDFs." />
            ) : (
              <select
                value={selectedPdf}
                onChange={(e) => setSelectedPdf(e.target.value)}
                className="block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="">Select a PDF...</option>
                {pdfs.map((pdf) => (
                  <option key={pdf.id} value={pdf.id}>
                    {pdf.source_url}
                  </option>
                ))}
              </select>
            )}
            <Button onClick={handleGenerate} loading={generating} disabled={!selectedPdf}>
              <Cloud size={16} />
              Generate Word Cloud
            </Button>
          </div>
        )}

        {activeTab === 'multi' && (
          <div className="space-y-4">
            <p className="text-sm text-gray-500">
              Select 2 or more from your available documents.
            </p>
            {pdfsLoading ? (
              <Spinner size={20} />
            ) : pdfs.length === 0 ? (
              <EmptyState icon={Cloud} title="No PDFs available" description="Crawl a website first to discover PDFs." />
            ) : (
              <div className="max-h-64 space-y-2 overflow-y-auto rounded-lg border border-gray-200 p-3">
                {pdfs.map((pdf) => (
                  <label
                    key={pdf.id}
                    className={`flex cursor-pointer items-center gap-3 rounded-lg p-2 transition-colors
                      ${selectedPdfs.includes(pdf.id) ? 'bg-indigo-50' : 'hover:bg-gray-50'}`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedPdfs.includes(pdf.id)}
                      onChange={() => togglePdf(pdf.id)}
                      className="rounded text-indigo-600 focus:ring-indigo-500"
                    />
                    <span className="truncate text-sm text-gray-900">{pdf.source_url}</span>
                  </label>
                ))}
              </div>
            )}
            <div className="flex items-center gap-3">
              <Button onClick={handleGenerate} loading={generating} disabled={selectedPdfs.length < 2}>
                <Cloud size={16} />
                Generate Word Cloud
              </Button>
              {selectedPdfs.length > 0 && (
                <span className="text-sm text-gray-500">{selectedPdfs.length} selected</span>
              )}
            </div>
          </div>
        )}

        {activeTab === 'interval' && (
          <div className="space-y-4">
            <p className="text-sm text-gray-500">
              Generate a word cloud from PDFs downloaded within a date range.
            </p>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Start Date & Time</label>
                <input
                  type="datetime-local"
                  step="1"
                  value={startDt}
                  onChange={(e) => setStartDt(e.target.value)}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">End Date & Time</label>
                <input
                  type="datetime-local"
                  step="1"
                  value={endDt}
                  onChange={(e) => setEndDt(e.target.value)}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>
            </div>
            <Button onClick={handleGenerate} loading={generating} disabled={!startDt || !endDt}>
              <Cloud size={16} />
              Generate Word Cloud
            </Button>
          </div>
        )}
      </Card>

      {/* Result */}
      {(generating || imageUrl) && (
        <Card>
          <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-gray-900">
            <ImageIcon size={18} />
            Generated Word Cloud
          </h2>
          {generating && !imageUrl ? (
            <div className="flex items-center justify-center py-12">
              <Spinner size={32} />
              <span className="ml-3 text-gray-500">Generating word cloud...</span>
            </div>
          ) : (
            <div className="flex justify-center">
              <img
                src={imageUrl}
                alt="Word Cloud"
                className="max-w-full rounded-lg shadow"
              />
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
