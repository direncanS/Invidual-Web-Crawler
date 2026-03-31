import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { login as loginApi } from '../api/auth';
import { getMe } from '../api/profile';
import { extractApiError } from '../api/client';
import { useAuth } from '../hooks/useAuth';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import ErrorBanner from '../components/ui/ErrorBanner';

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const [form, setForm] = useState({ email_or_nickname: '', password: '' });
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState('');
  const [loading, setLoading] = useState(false);
  const registered = location.state?.registered;

  const validate = () => {
    const e = {};
    if (!form.email_or_nickname.trim()) e.email_or_nickname = 'Email or nickname is required';
    if (!form.password) e.password = 'Password is required';
    return e;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const v = validate();
    setErrors(v);
    if (Object.keys(v).length) return;

    setLoading(true);
    setApiError('');
    try {
      const res = await loginApi(form);
      const token = res.data.access_token;
      localStorage.setItem('access_token', token);
      const userRes = await getMe();
      login(token, userRes.data);
      navigate('/dashboard');
    } catch (err) {
      setApiError(extractApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const update = (field) => (e) => {
    setForm({ ...form, [field]: e.target.value });
    setErrors({ ...errors, [field]: undefined });
  };

  return (
    <div className="mx-auto max-w-md pt-8">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Sign In</h1>
      <Card>
        <form onSubmit={handleSubmit} className="space-y-4">
          {registered && (
            <div className="rounded-lg bg-green-50 border border-green-200 px-4 py-3 text-sm text-green-700">
              Account created successfully. Please sign in.
            </div>
          )}
          <ErrorBanner message={apiError} />
          <Input
            label="Email or Nickname"
            value={form.email_or_nickname}
            onChange={update('email_or_nickname')}
            error={errors.email_or_nickname}
            placeholder="john@example.com"
          />
          <Input
            label="Password"
            type="password"
            value={form.password}
            onChange={update('password')}
            error={errors.password}
            placeholder="Your password"
          />
          <Button type="submit" loading={loading} className="w-full">
            Sign In
          </Button>
        </form>
        <div className="mt-4 flex justify-between text-sm">
          <Link to="/forgot-password" className="font-medium text-indigo-600 hover:text-indigo-500">
            Forgot password?
          </Link>
          <Link to="/register" className="font-medium text-indigo-600 hover:text-indigo-500">
            Create account
          </Link>
        </div>
      </Card>
    </div>
  );
}
