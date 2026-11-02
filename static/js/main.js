// =============================================
//  TuitionPro - Custom JavaScript
// =============================================

document.addEventListener('DOMContentLoaded', function () {

  // ---- Sidebar toggle (mobile) ----
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', function () {
      sidebar.classList.toggle('show');
    });
  }

  // ---- Mark active nav link based on current URL ----
  const currentPath = window.location.pathname;
  document.querySelectorAll('#sidebar .nav-link').forEach(function (link) {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });

  // ---- Auto-dismiss alerts after 4 seconds ----
  document.querySelectorAll('.alert.auto-dismiss').forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert.close();
    }, 4000);
  });

});
