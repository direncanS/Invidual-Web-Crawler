import { Link } from 'react-router-dom';
import { Globe, FileText, Search, BarChart3, Cloud, Shield } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

const features = [
  { icon: Globe, title: 'Web Crawling', desc: 'Crawl websites up to 3 levels deep with automatic link discovery' },
  { icon: FileText, title: 'PDF Discovery', desc: 'Automatically find and download PDF documents from crawled pages' },
  { icon: BarChart3, title: 'Word Analytics', desc: 'Extract and analyze top-10 word statistics from each PDF' },
  { icon: Search, title: 'Smart Search', desc: 'Search across word statistics of all your indexed PDFs' },
  { icon: Cloud, title: 'Word Clouds', desc: 'Generate beautiful word clouds from single or multiple PDFs' },
  { icon: Shield, title: 'Secure & Personal', desc: 'Your crawl history and documents are private and persistent' },
];

export default function Landing() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <div className="bg-gradient-to-br from-indigo-600 to-purple-700 text-white">
        <div className="mx-auto max-w-7xl px-4 py-24 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="mb-6 flex justify-center">
              <Globe size={56} />
            </div>
            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
              Individual Web Crawler
            </h1>
            <p className="mx-auto mt-4 max-w-2xl text-lg text-indigo-100">
              Crawl websites, discover PDFs, analyze word frequencies, and generate
              word clouds — all from your personal dashboard.
            </p>
            <div className="mt-8 flex justify-center gap-4">
              {isAuthenticated ? (
                <Link
                  to="/dashboard"
                  className="rounded-lg bg-white px-6 py-3 text-sm font-semibold text-indigo-600 shadow hover:bg-indigo-50 transition-colors"
                >
                  Go to Dashboard
                </Link>
              ) : (
                <>
                  <Link
                    to="/register"
                    className="rounded-lg bg-white px-6 py-3 text-sm font-semibold text-indigo-600 shadow hover:bg-indigo-50 transition-colors"
                  >
                    Get Started
                  </Link>
                  <Link
                    to="/login"
                    className="rounded-lg border border-white/30 px-6 py-3 text-sm font-semibold text-white hover:bg-white/10 transition-colors"
                  >
                    Sign In
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Features */}
      <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
        <h2 className="text-center text-3xl font-bold text-gray-900">Features</h2>
        <p className="mx-auto mt-2 max-w-xl text-center text-gray-500">
          Everything you need to crawl, analyze, and visualize web content.
        </p>
        <div className="mt-12 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((f) => (
            <div key={f.title} className="rounded-xl bg-white p-6 shadow transition-shadow hover:shadow-md">
              <f.icon size={28} className="text-indigo-600" />
              <h3 className="mt-3 text-lg font-semibold text-gray-900">{f.title}</h3>
              <p className="mt-1 text-sm text-gray-500">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-gray-200 bg-white py-6 text-center text-sm text-gray-500">
        Web Crawler &copy; {new Date().getFullYear()}
      </div>
    </div>
  );
}
