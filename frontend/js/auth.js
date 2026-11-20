/**
 * Mini E-Commerce System - Authentication & Session Management
 */

const Auth = {
  getUser() {
    try {
      const u = localStorage.getItem('user');
      return u ? JSON.parse(u) : null;
    } catch {
      return null;
    }
  },

  getToken() {
    return localStorage.getItem('access_token');
  },

  getRefreshToken() {
    return localStorage.getItem('refresh_token');
  },

  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  },

  isAdmin() {
    const user = this.getUser();
    return user && (user.role === 'ADMIN' || user.is_admin || user.is_staff);
  },

  async login(username_or_email, password) {
    try {
      const res = await apiRequest('/auth/login/', {
        method: 'POST',
        body: { username_or_email, password }
      });

      if (res.ok) {
        localStorage.setItem('access_token', res.data.access);
        localStorage.setItem('refresh_token', res.data.refresh);
        localStorage.setItem('user', JSON.stringify(res.data.user));
        return { success: true, user: res.data.user };
      }
    } catch (err) {
      return { success: false, error: err.message };
    }
  },

  async register(data) {
    try {
      const res = await apiRequest('/auth/register/', {
        method: 'POST',
        body: data
      });
      return { success: true, message: res.data.message };
    } catch (err) {
      return { success: false, error: err.message };
    }
  },

  async logout() {
    const refresh = this.getRefreshToken();
    try {
      if (refresh) {
        await apiRequest('/auth/logout/', {
          method: 'POST',
          body: { refresh }
        });
      }
    } catch (e) {
      console.warn("Logout API notice:", e);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      const root = getRootPath();
      window.location.href = `${root}login.html`;
    }
  },

  requireAuth(adminOnly = false) {
    const root = getRootPath();
    if (!this.isAuthenticated()) {
      showToast("Please log in to continue.", "warning");
      setTimeout(() => {
        window.location.href = `${root}login.html?redirect=${encodeURIComponent(window.location.href)}`;
      }, 500);
      return false;
    }

    if (adminOnly && !this.isAdmin()) {
      showToast("Access denied: Administrator privileges required.", "error");
      setTimeout(() => {
        window.location.href = `${root}index.html`;
      }, 800);
      return false;
    }

    return true;
  },

  initNavbar() {
    const authNav = document.getElementById('navbar-auth-section');
    if (!authNav) return;

    const root = getRootPath();
    const user = this.getUser();

    if (this.isAuthenticated() && user) {
      const isAdminUser = this.isAdmin();
      authNav.innerHTML = `
        <div class="dropdown">
          <button class="btn btn-outline-primary dropdown-toggle d-flex align-items-center gap-2" type="button" data-bs-toggle="dropdown" aria-expanded="false">
            <i class="fa-solid fa-circle-user fa-lg"></i>
            <span>${user.full_name || user.username}</span>
            <span class="badge ${isAdminUser ? 'bg-danger' : 'bg-primary'} ms-1" style="font-size: 0.7rem;">${user.role}</span>
          </button>
          <ul class="dropdown-menu dropdown-menu-end shadow-sm">
            <li><span class="dropdown-item-text text-muted small"><i class="fa-regular fa-envelope me-1"></i> ${user.email}</span></li>
            <li><hr class="dropdown-divider"></li>
            ${isAdminUser ? `<li><a class="dropdown-item text-primary fw-semibold" href="${root}admin/dashboard.html"><i class="fa-solid fa-gauge-high me-2"></i> Admin Dashboard</a></li>` : ''}
            <li><a class="dropdown-item" href="${root}my-orders.html"><i class="fa-solid fa-box-open me-2"></i> My Orders</a></li>
            <li><a class="dropdown-item" href="${root}profile.html"><i class="fa-regular fa-id-badge me-2"></i> My Profile</a></li>
            <li><hr class="dropdown-divider"></li>
            <li><button class="dropdown-item text-danger" onclick="Auth.logout()"><i class="fa-solid fa-right-from-bracket me-2"></i> Logout</button></li>
          </ul>
        </div>
      `;
    } else {
      authNav.innerHTML = `
        <div class="d-flex align-items-center gap-2">
          <a href="${root}login.html" class="btn btn-outline-primary btn-sm"><i class="fa-solid fa-right-to-bracket me-1"></i> Login</a>
          <a href="${root}register.html" class="btn btn-primary btn-sm"><i class="fa-solid fa-user-plus me-1"></i> Register</a>
        </div>
      `;
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  Auth.initNavbar();
});
