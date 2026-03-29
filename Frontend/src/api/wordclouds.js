import client from './client';

export function createSingle(pdfId) {
  return client.post('/wordclouds/single', { pdf_id: pdfId });
}

export function createMulti(pdfIds) {
  return client.post('/wordclouds/multi', { pdf_ids: pdfIds });
}

export function createInterval(startDatetime, endDatetime) {
  return client.post('/wordclouds/interval', {
    start_datetime: startDatetime,
    end_datetime: endDatetime,
  });
}

export function getImage(artifactId) {
  return client.get(`/wordclouds/${artifactId}/image`, { responseType: 'blob' });
}
