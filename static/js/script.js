/* Custom JavaScript for Al-Azhar Student Management System */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Auto-close alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Enable tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Level-dependent course selection in forms
    var levelSelect = document.getElementById('id_level');
    var courseSelect = document.getElementById('id_course');
    
    if (levelSelect && courseSelect) {
        levelSelect.addEventListener('change', function() {
            updateCourseOptions(this.value);
        });

        // Function to update course options based on level
        function updateCourseOptions(levelId) {
            if (!levelId) return;
            
            fetch(`/api/courses/?level=${levelId}`)
                .then(response => response.json())
                .then(data => {
                    // Clear current options
                    courseSelect.innerHTML = '<option value="">---------</option>';
                    
                    // Add new options
                    data.forEach(course => {
                        var option = document.createElement('option');
                        option.value = course.id;
                        option.textContent = course.name;
                        courseSelect.appendChild(option);
                    });
                })
                .catch(error => console.error('Error fetching courses:', error));
        }
    }

    // Print functionality
    var printButton = document.getElementById('print-button');
    if (printButton) {
        printButton.addEventListener('click', function() {
            window.print();
        });
    }

    // Confirm delete modals
    var deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('هل أنت متأكد من أنك تريد حذف هذا العنصر؟')) {
                e.preventDefault();
            }
        });
    });

    // Search form auto-submit
    var searchForms = document.querySelectorAll('.search-form select');
    searchForms.forEach(function(select) {
        select.addEventListener('change', function() {
            this.form.submit();
        });
    });

    // Filter toggle on mobile
    var filterToggle = document.getElementById('filter-toggle');
    var filterContainer = document.getElementById('filter-container');
    
    if (filterToggle && filterContainer) {
        filterToggle.addEventListener('click', function() {
            filterContainer.classList.toggle('d-none');
        });
    }
}); 