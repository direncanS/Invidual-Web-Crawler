import { useState } from 'react';
import { Link } from 'react-router-dom';
import { forgotPassword } from '../api/auth';
import { extractApiError } from '../api/client';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import ErrorBanner from '../components/ui/ErrorBanner';
import { Mail } from 'lucide-react';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [apiError, setApiError] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim()) {
      setError('Email is required');
      return;
    }
    setLoading(true);
    setApiError('');
    try {
      await forgotPassword({ email });
      setSent(true);
    } catch (err) {
      setApiError(extractApiError(err));
    } finally {
      setLoading(false);
    }
  };

  if (sent) {
    return (
      <div className="mx-auto max-w-md pt-8">
        <Card>
          <div className="text-center">
            <Mail size={48} className="mx-auto mb-4 text-indigo-600" />
            <h2 className="text-xl font-bold text-gray-900">Check Your Email</h2>
            <p className="mt-2 text-sm text-gray-500">
              If an account with that email exists, we've sent a password reset link.
              The link expires in 60 seconds.
            </p>
            <p className="mt-4 text-sm text-gray-500">
              Using MailHog?{' '}
              <a
                href="http://localhost:8025"
                target="_blank"
                rel="noopener noreferrer"
                className="font-medium text-indigo-600 hover:text-indigo-500"
              >
                Open MailHog
              </a>
            </p>
            <Link to="/login" className="mt-4 inline-block text-sm font-medium text-indigo-600 hover:text-indigo-500">
              Back to Sign In
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-md pt-8">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Forgot Password</h1>
      <Card>
        <form onSubmit={handleSubmit} className="space-y-4">
          <ErrorBanner message={apiError} />
          <p className="text-sm text-gray-500">
            Enter your email address and we'll send you a reset link.
          </p>
          <Input
            label="Email"
            type="email"
            value={email}
            onChange={(e) => { setEmail(e.target.value); setError(''); }}
            error={error}
            placeholder="john@example.com"
          />
          <Button type="submit" loading={loading} className="w-full">
            Send Reset Link
          </Button>
        </form>
        <p className="mt-4 text-center text-sm text-gray-500">
          <Link to="/login" className="font-medium text-indigo-600 hover:text-indigo-500">
            Back to Sign In
          </Link>
        </p>
      </Card>
    </div>
  );
}
