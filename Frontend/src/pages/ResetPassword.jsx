import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { resetPassword } from '../api/auth';
import { extractApiError } from '../api/client';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import ErrorBanner from '../components/ui/ErrorBanner';
import { CheckCircle, AlertTriangle } from 'lucide-react';

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token') || '';
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [apiError, setApiError] = useState('');
  const [loading, setLoading] = useState(false);
  const [tokenError, setTokenError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!password) {
      setError('Password is required');
      return;
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);
    setApiError('');
    setTokenError('');
    try {
      await resetPassword({ token, new_password: password });
      setSuccess(true);
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) {
      const msg = extractApiError(err);
      const msgLower = msg.toLowerCase();
      if (msgLower.includes('expired')) {
        setTokenError('Reset link has expired. Please request a new one.');
      } else if (msgLower.includes('used') || msgLower.includes('already')) {
        setTokenError('This reset link has already been used.');
      } else if (msgLower.includes('invalid')) {
        setTokenError('Invalid reset link.');
      } else {
        setApiError(msg);
      }
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="mx-auto max-w-md pt-8">
        <Card>
          <div className="text-center">
            <AlertTriangle size={48} className="mx-auto mb-4 text-yellow-500" />
            <h2 className="text-xl font-bold text-gray-900">Missing Reset Token</h2>
            <p className="mt-2 text-sm text-gray-500">
              No reset token found. Please use the link from your email.
            </p>
            <Link to="/forgot-password" className="mt-4 inline-block text-sm font-medium text-indigo-600 hover:text-indigo-500">
              Request a new link
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  if (success) {
    return (
      <div className="mx-auto max-w-md pt-8">
        <Card>
          <div className="text-center">
            <CheckCircle size={48} className="mx-auto mb-4 text-green-500" />
            <h2 className="text-xl font-bold text-gray-900">Password Reset</h2>
            <p className="mt-2 text-sm text-gray-500">
              Your password has been reset successfully. Redirecting to sign in...
            </p>
          </div>
        </Card>
      </div>
    );
  }

  if (tokenError) {
    return (
      <div className="mx-auto max-w-md pt-8">
        <Card>
          <div className="text-center">
            <AlertTriangle size={48} className="mx-auto mb-4 text-red-500" />
            <h2 className="text-xl font-bold text-gray-900">Cannot Reset Password</h2>
            <p className="mt-2 text-sm text-gray-500">{tokenError}</p>
            <Link to="/forgot-password" className="mt-4 inline-block text-sm font-medium text-indigo-600 hover:text-indigo-500">
              Request a new link
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-md pt-8">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Reset Password</h1>
      <Card>
        <form onSubmit={handleSubmit} className="space-y-4">
          <ErrorBanner message={apiError} />
          <Input
            label="New Password"
            type="password"
            value={password}
            onChange={(e) => { setPassword(e.target.value); setError(''); }}
            error={error}
            placeholder="Min. 8 characters"
          />
          <Button type="submit" loading={loading} className="w-full">
            Reset Password
          </Button>
        </form>
      </Card>
    </div>
  );
}
