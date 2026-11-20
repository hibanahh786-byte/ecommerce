/**
 * Mini E-Commerce System - Admin Common Layout & Controls
 */

const AdminLayout = {
  renderSidebar(activePage) {
    const sidebar = document.getElementById('admin-sidebar');
    if (!sidebar) return;

    sidebar.innerHTML = `
      <a href="dashboard.html" class="admin-sidebar-brand">
        <i class="fa-solid fa-store text-primary"></i>
        <span>ApexStore <span class="badge bg-danger small" style="font-size: 0.65rem;">ADMIN</span></span>
      </a>

      <ul class="admin-nav-list">
        <li class="admin-nav-item">
          <a href="dashboard.html" class="${activePage === 'dashboard' ? 'active' : ''}">
            <i class="fa-solid fa-gauge-high"></i>
            <span>Dashboard</span>
          </a>
        </li>
        <li class="admin-nav-item">
          <a href="categories.html" class="${activePage === 'categories' ? 'active' : ''}">
            <i class="fa-solid fa-layer-group"></i>
            <span>Categories</span>
          </a>
        </li>
        <li class="admin-nav-item">
          <a href="products.html" class="${activePage === 'products' ? 'active' : ''}">
            <i class="fa-solid fa-box-archive"></i>
            <span>Products</span>
          </a>
        </li>
        <li class="admin-nav-item">
          <a href="orders.html" class="${activePage === 'orders' ? 'active' : ''}">
            <i class="fa-solid fa-cart-flatbed"></i>
            <span>Orders</span>
          </a>
        </li>
        <li class="admin-nav-item">
          <a href="users.html" class="${activePage === 'users' ? 'active' : ''}">
            <i class="fa-solid fa-users"></i>
            <span>Users</span>
          </a>
        </li>
      </ul>

      <div class="admin-sidebar-footer">
        <a href="../index.html" class="btn btn-outline-light btn-sm w-100 mb-2 text-start">
          <i class="fa-solid fa-store me-2"></i> View Customer Store
        </a>
        <button class="btn btn-danger btn-sm w-100 text-start" onclick="Auth.logout()">
          <i class="fa-solid fa-right-from-bracket me-2"></i> Logout
        </button>
      </div>
    `;
  },

  renderTopbar(title) {
    const topbar = document.getElementById('admin-topbar');
    if (!topbar) return;

    const user = Auth.getUser() || { full_name: 'Administrator', username: 'admin' };

    topbar.innerHTML = `
      <div class="d-flex align-items-center gap-3">
        <button class="sidebar-toggle-btn" type="button" onclick="AdminLayout.toggleSidebar()">
          <i class="fa-solid fa-bars"></i>
        </button>
        <h4 class="fw-bold mb-0">${title}</h4>
      </div>

      <div class="d-flex align-items-center gap-3">
        <div class="text-end d-none d-sm-block">
          <div class="fw-bold text-dark small">${user.full_name || user.username}</div>
          <span class="badge bg-danger rounded-pill" style="font-size: 0.7rem;">Superuser / Admin</span>
        </div>
        <div class="p-2 rounded-circle bg-light border">
          <i class="fa-solid fa-user-shield text-primary fa-lg"></i>
        </div>
      </div>
    `;
  },

  toggleSidebar() {
    const sidebar = document.getElementById('admin-sidebar');
    if (sidebar) {
      sidebar.classList.toggle('show');
    }
  },

  init(activePage, title) {
    if (!Auth.requireAuth(true)) return false;
    this.renderSidebar(activePage);
    this.renderTopbar(title);
    return true;
  }
};
