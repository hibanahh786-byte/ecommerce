/**
 * Mini E-Commerce System - Core API Client & Utilities
 */

const API_CONFIG = {
  // If running directly on the Django server, use relative path; otherwise localhost:8000
  BASE_URL: (window.location.port === '8000' || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') && window.location.protocol.startsWith('http')
    ? `${window.location.origin}/api`
    : 'http://127.0.0.1:8000/api',
  MEDIA_FALLBACK: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80'
};

/**
 * Toast Notification Dispatcher
 */
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const icons = {
    success: 'fa-check-circle',
    error: 'fa-circle-exclamation',
    warning: 'fa-triangle-exclamation',
    info: 'fa-circle-info'
  };

  const toast = document.createElement('div');
  toast.className = `custom-toast toast-${type}`;
  toast.innerHTML = `
    <i class="fa-solid ${icons[type] || icons.info} fa-lg"></i>
    <div style="flex: 1;">
      <div style="font-weight: 600; font-size: 0.92rem;">${type.toUpperCase()}</div>
      <div style="font-size: 0.85rem; opacity: 0.95;">${message}</div>
    </div>
    <button type="button" style="background: none; border: none; color: #fff; cursor: pointer;" onclick="this.parentElement.remove()">
      <i class="fa-solid fa-xmark"></i>
    </button>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    if (toast.parentElement) {
      toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      setTimeout(() => toast.remove(), 300);
    }
  }, 4500);
}

/**
 * Format currency in Indian Rupees
 */
function formatPrice(amount) {
  const num = Number(amount) || 0;
  return '₹' + num.toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

/**
 * Format ISO datetime string
 */
function formatDate(dateStr) {
  if (!dateStr) return '-';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

/**
 * Generic Fetch Wrapper with Automatic Auth & Token Refresh
 */
async function apiRequest(endpoint, options = {}) {
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const url = `${API_CONFIG.BASE_URL}${cleanEndpoint}`;

  const defaultHeaders = {};
  const token = localStorage.getItem('access_token');
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }

  // Handle FormData vs JSON
  let body = options.body;
  if (body && !(body instanceof FormData) && typeof body === 'object') {
    defaultHeaders['Content-Type'] = 'application/json';
    body = JSON.stringify(body);
  }

  const fetchOptions = {
    method: options.method || 'GET',
    headers: {
      ...defaultHeaders,
      ...(options.headers || {})
    },
    body
  };

  try {
    let response = await fetch(url, fetchOptions);

    // If 401 Unauthorized, try token refresh
    if (response.status === 401 && localStorage.getItem('refresh_token')) {
      const refreshed = await tryRefreshToken();
      if (refreshed) {
        // Retry original request with new token
        fetchOptions.headers['Authorization'] = `Bearer ${localStorage.getItem('access_token')}`;
        response = await fetch(url, fetchOptions);
      } else {
        // Refresh failed, session expired
        handleSessionExpired();
        throw new Error('Session expired. Please log in again.');
      }
    }

    // Parse JSON or return empty if 204
    if (response.status === 204) {
      return { ok: true, data: null };
    }

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      let errorMsg = 'An unexpected error occurred.';
      if (typeof data === 'object') {
        if (data.detail) errorMsg = data.detail;
        else if (data.error) errorMsg = data.error;
        else if (data.message) errorMsg = data.message;
        else {
          // Join validation error fields
          const messages = Object.entries(data)
            .map(([field, err]) => `${field}: ${Array.isArray(err) ? err.join(' ') : err}`);
          if (messages.length > 0) errorMsg = messages.join('\n');
        }
      }
      const error = new Error(errorMsg);
      error.status = response.status;
      error.data = data;
      throw error;
    }

    return { ok: true, data };
  } catch (err) {
    console.error(`API Error on ${url}:`, err);
    throw err;
  }
}

/**
 * Token Refresh Logic
 */
async function tryRefreshToken() {
  const refresh = localStorage.getItem('refresh_token');
  if (!refresh) return false;

  try {
    const res = await fetch(`${API_CONFIG.BASE_URL}/auth/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh })
    });

    if (res.ok) {
      const data = await res.json();
      localStorage.setItem('access_token', data.access);
      if (data.refresh) {
        localStorage.setItem('refresh_token', data.refresh);
      }
      return true;
    }
    return false;
  } catch {
    return false;
  }
}

/**
 * Handle expired session
 */
function handleSessionExpired() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
  
  // If not already on login or public pages, redirect
  const currentPath = window.location.pathname;
  if (!currentPath.includes('login.html') && !currentPath.includes('register.html') && !currentPath.endsWith('index.html')) {
    window.location.href = getRootPath() + 'login.html';
  }
}

/**
 * Helper to compute root relative path for nested admin pages
 */
function getRootPath() {
  const path = window.location.pathname;
  if (path.includes('/admin/')) {
    return '../';
  }
  return '';
}
