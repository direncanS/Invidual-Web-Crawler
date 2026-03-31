import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createJob } from '../api/crawl';
import { extractApiError } from '../api/client';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import ErrorBanner from '../components/ui/ErrorBanner';

const depthDescriptions = {
  1: 'Only the given URL',
  2: 'Given URL + same-domain links found on it',
  3: 'Same-domain + external-domain links (external links not expanded further)',
};

export default function NewCrawl() {
  const navigate = useNavigate();
  const [url, setUrl] = useState('');
  const [depth, setDepth] = useState(2);
  const [urlError, setUrlError] = useState('');
  const [apiError, setApiError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url.trim()) {
      setUrlError('URL is required');
      return;
    }

    setLoading(true);
    setApiError('');
    try {
      const res = await createJob({ start_url: url, depth });
      navigate(`/jobs/${res.data.id}`);
    } catch (err) {
      setApiError(extractApiError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-lg">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">New Crawl</h1>
      <Card>
        <form onSubmit={handleSubmit} className="space-y-5">
          <ErrorBanner message={apiError} />
          <Input
            label="Start URL"
            value={url}
            onChange={(e) => { setUrl(e.target.value); setUrlError(''); }}
            error={urlError}
            placeholder="http://example.com"
          />

          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">Crawl Depth</label>
            <div className="space-y-2">
              {[1, 2, 3].map((d) => (
                <label
                  key={d}
                  className={`flex cursor-pointer items-start gap-3 rounded-lg border p-3 transition-colors
                    ${depth === d ? 'border-indigo-500 bg-indigo-50' : 'border-gray-200 hover:bg-gray-50'}`}
                >
                  <input
                    type="radio"
                    name="depth"
                    value={d}
                    checked={depth === d}
                    onChange={() => setDepth(d)}
                    className="mt-0.5 text-indigo-600 focus:ring-indigo-500"
                  />
                  <div>
                    <span className="text-sm font-medium text-gray-900">Depth {d}</span>
                    <p className="text-xs text-gray-500">{depthDescriptions[d]}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <Button type="submit" loading={loading} className="w-full">
            Start Crawl
          </Button>
        </form>
      </Card>
    </div>
  );
}
