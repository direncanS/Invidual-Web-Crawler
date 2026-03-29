import client from './client';

export function register(data) {
  return client.post('/auth/register', data);
}

export function login(data) {
  return client.post('/auth/login', data);
}

export function forgotPassword(data) {
  return client.post('/auth/forgot-password', data);
}

export function resetPassword(data) {
  return client.post('/auth/reset-password', data);
}
