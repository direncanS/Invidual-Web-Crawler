import client from './client';

export function searchTopWords(word) {
  return client.get('/search/top-words', { params: { word } });
}
