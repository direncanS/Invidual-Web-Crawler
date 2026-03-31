import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { register } from '../api/auth';
import { extractApiError } from '../api/client';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import ErrorBanner from '../components/ui/ErrorBanner';

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ nickname: '', email: '', password: '' });
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState('');
  const [loading, setLoading] = useState(false);

  const validate = () => {
    const e = {};
    if (!form.nickname.trim()) e.nickname = 'Nickname is required';
    if (!form.email.trim()) e.email = 'Email is required';
    if (!form.password) e.password = 'Password is required';
    else if (form.password.length < 8) e.password = 'Password must be at least 8 characters';
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
      await register(form);
      navigate('/login', { state: { registered: true } });
    } catch (err) {
      const msg = extractApiError(err);
      if (msg.toLowerCase().includes('nickname')) {
        setErrors({ nickname: 'This nickname is already taken' });
      } else if (msg.toLowerCase().includes('email')) {
        setErrors({ email: 'This email is already in use' });
      } else {
        setApiError(msg);
      }
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
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Create Account</h1>
      <Card>
        <form onSubmit={handleSubmit} className="space-y-4">
          <ErrorBanner message={apiError} />
          <Input
            label="Nickname"
            value={form.nickname}
            onChange={update('nickname')}
            error={errors.nickname}
            placeholder="johndoe"
          />
          <Input
            label="Email"
            type="email"
            value={form.email}
            onChange={update('email')}
            error={errors.email}
            placeholder="john@example.com"
          />
          <Input
            label="Password"
            type="password"
            value={form.password}
            onChange={update('password')}
            error={errors.password}
            placeholder="Min. 8 characters"
          />
          <Button type="submit" loading={loading} className="w-full">
            Register
          </Button>
        </form>
        <p className="mt-4 text-center text-sm text-gray-500">
          Already have an account?{' '}
          <Link to="/login" className="font-medium text-indigo-600 hover:text-indigo-500">
            Sign in
          </Link>
        </p>
      </Card>
    </div>
  );
}
