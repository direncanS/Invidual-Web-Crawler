import client from './client';

export function createJob(data) {
  return client.post('/crawl/jobs', data);
}

export function listJobs() {
  return client.get('/crawl/jobs');
}

export function getJob(jobId) {
  return client.get(`/crawl/jobs/${jobId}`);
}

export function getJobPages(jobId) {
  return client.get(`/crawl/jobs/${jobId}/pages`);
}

export function getJobPdfs(jobId) {
  return client.get(`/crawl/jobs/${jobId}/pdfs`);
}
