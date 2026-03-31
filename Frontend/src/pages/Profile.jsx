import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { updateMe } from '../api/profile';
import { extractApiError } from '../api/client';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import ErrorBanner from '../components/ui/ErrorBanner';
import { User } from 'lucide-react';

export default function Profile() {
  const { user, updateUser } = useAuth();
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({ nickname: user?.nickname || '', email: user?.email || '' });
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const validate = () => {
    const e = {};
    if (!form.nickname.trim()) e.nickname = 'Nickname is required';
    if (!form.email.trim()) e.email = 'Email is required';
    return e;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const v = validate();
    setErrors(v);
    if (Object.keys(v).length) return;

    setLoading(true);
    setApiError('');
    setSuccess(false);
    try {
      const res = await updateMe(form);
      updateUser(res.data);
      setSuccess(true);
      setEditing(false);
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

  const startEditing = () => {
    setForm({ nickname: user?.nickname || '', email: user?.email || '' });
    setEditing(true);
    setSuccess(false);
    setErrors({});
    setApiError('');
  };

  const cancel = () => {
    setEditing(false);
    setErrors({});
    setApiError('');
  };

  const update = (field) => (e) => {
    setForm({ ...form, [field]: e.target.value });
    setErrors({ ...errors, [field]: undefined });
  };

  return (
    <div className="mx-auto max-w-lg">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Profile</h1>
      <Card>
        <div className="mb-6 flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-indigo-100">
            <User size={32} className="text-indigo-600" />
          </div>
          <div>
            <p className="text-lg font-semibold text-gray-900">{user?.nickname}</p>
            <p className="text-sm text-gray-500">{user?.email}</p>
          </div>
        </div>

        {success && (
          <div className="mb-4 rounded-lg bg-green-50 border border-green-200 px-4 py-3 text-sm text-green-700">
            Profile updated successfully.
          </div>
        )}

        {editing ? (
          <form onSubmit={handleSubmit} className="space-y-4">
            <ErrorBanner message={apiError} />
            <Input
              label="Nickname"
              value={form.nickname}
              onChange={update('nickname')}
              error={errors.nickname}
            />
            <Input
              label="Email"
              type="email"
              value={form.email}
              onChange={update('email')}
              error={errors.email}
            />
            <div className="flex gap-3">
              <Button type="submit" loading={loading}>Save Changes</Button>
              <Button type="button" variant="secondary" onClick={cancel}>Cancel</Button>
            </div>
          </form>
        ) : (
          <Button onClick={startEditing}>Edit Profile</Button>
        )}
      </Card>
    </div>
  );
}
