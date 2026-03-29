import client from './client';

export function listPdfs() {
  return client.get('/pdfs/');
}

export function getPdf(pdfId) {
  return client.get(`/pdfs/${pdfId}`);
}

export function downloadPdf(pdfId) {
  return client.get(`/pdfs/${pdfId}/download`, { responseType: 'blob' });
}

export function getTopWords(pdfId) {
  return client.get(`/pdfs/${pdfId}/stats/top-words`);
}
