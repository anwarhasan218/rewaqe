// Main JavaScript file for the Azhar Student Management System

// Initialize tooltips and popovers when the document is ready
document.addEventListener('DOMContentLoaded', function() {
  // Initialize Bootstrap tooltips
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Initialize Bootstrap popovers
  var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
  var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
  });
});

// Function to confirm delete actions
function confirmDelete(event, message) {
  if (!confirm(message || 'هل أنت متأكد من رغبتك في الحذف؟')) {
    event.preventDefault();
  }
}

// Auto dismiss alerts after 5 seconds
setTimeout(function() {
  var alerts = document.querySelectorAll('.alert.alert-dismissible');
  alerts.forEach(function(alert) {
    // Create a Bootstrap alert instance and call dispose
    var bsAlert = new bootstrap.Alert(alert);
    bsAlert.close();
  });
}, 5000); 