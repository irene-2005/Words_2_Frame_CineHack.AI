const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000';

const defaultHeaders = {
  Accept: 'application/json',
};

async function parseError(response) {
  const contentType = response.headers.get('Content-Type') || '';
  if (contentType.includes('application/json')) {
    try {
      const body = await response.json();
      return body.detail || body.message || JSON.stringify(body);
    } catch (err) {
      return response.statusText || 'Unknown error';
    }
  }
  try {
    return await response.text();
  } catch (err) {
    return response.statusText || 'Unknown error';
  }
}

async function handleResponse(response) {
  if (response.ok) {
    const noContent = response.status === 204;
    if (noContent) return null;
    const contentType = response.headers.get('Content-Type') || '';
    if (contentType.includes('application/json')) {
      return response.json();
    }
    return response.text();
  }
  const errorMessage = await parseError(response);
  const error = new Error(errorMessage || `Request failed with status ${response.status}`);
  error.status = response.status;
  throw error;
}

function buildAuthHeaders(token, extra = {}) {
  const headers = { ...defaultHeaders, ...extra };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

export async function uploadScript(projectId, file, token) {
  if (!file) {
    throw new Error('No file provided for upload');
  }
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/projects/${projectId}/upload_script`, {
    method: 'POST',
    headers: buildAuthHeaders(token),
    body: formData,
  });

  return handleResponse(response);
}

export async function analyzeScript(projectId, filename, token) {
  const response = await fetch(`${API_BASE_URL}/projects/${projectId}/analyze_script`, {
    method: 'POST',
    headers: buildAuthHeaders(token, { 'Content-Type': 'application/json' }),
    body: JSON.stringify({ filename }),
  });

  return handleResponse(response);
}

export async function fetchProjectSnapshot(projectId, token) {
  const response = await fetch(`${API_BASE_URL}/projects/${projectId}/snapshot`, {
    method: 'GET',
    headers: buildAuthHeaders(token),
  });

  return handleResponse(response);
}

export async function listProjects(token) {
  const response = await fetch(`${API_BASE_URL}/projects/`, {
    method: 'GET',
    headers: buildAuthHeaders(token),
  });

  return handleResponse(response);
}

export async function fetchDefaultProject(token) {
  const response = await fetch(`${API_BASE_URL}/projects/default`, {
    method: 'GET',
    headers: buildAuthHeaders(token),
  });

  return handleResponse(response);
}

export async function createProject(payload, token) {
  const response = await fetch(`${API_BASE_URL}/projects/`, {
    method: 'POST',
    headers: buildAuthHeaders(token, { 'Content-Type': 'application/json' }),
    body: JSON.stringify(payload),
  });

  return handleResponse(response);
}

export async function fetchProjectReports(projectId, token) {
  if (!projectId) {
    throw new Error('Project ID is required to fetch reports');
  }

  const response = await fetch(`${API_BASE_URL}/projects/${projectId}/reports`, {
    method: 'GET',
    headers: buildAuthHeaders(token),
  });

  return handleResponse(response);
}
