import client from './client';

export function getMe() {
  return client.get('/me');
}

export function updateMe(data) {
  return client.put('/me', data);
}
