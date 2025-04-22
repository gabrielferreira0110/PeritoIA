/**
 * Perito IA - Main JavaScript File
 */

document.addEventListener('DOMContentLoaded', function() {
    // Automatically dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-danger)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Activate tooltips everywhere
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            
            // Only apply smooth scrolling to anchors that point to an element on the page
            if (targetId !== '#' && document.querySelector(targetId)) {
                e.preventDefault();
                
                document.querySelector(targetId).scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Enable form validation styles
    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Show confirmation for delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm(this.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });

    // Add dynamic behavior to textareas to adjust height based on content
    const autoResizeTextareas = document.querySelectorAll('textarea[data-auto-resize]');
    autoResizeTextareas.forEach(textarea => {
        function resizeTextarea() {
            textarea.style.height = 'auto';
            textarea.style.height = (textarea.scrollHeight) + 'px';
        }
        
        // Resize on input
        textarea.addEventListener('input', resizeTextarea);
        
        // Initial resize
        resizeTextarea();
    });

    // Handle collapsible sections
    const collapsibleHeaders = document.querySelectorAll('[data-toggle="collapse"]');
    collapsibleHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const target = document.querySelector(targetId);
            
            if (target) {
                if (target.classList.contains('show')) {
                    target.classList.remove('show');
                    this.setAttribute('aria-expanded', 'false');
                } else {
                    target.classList.add('show');
                    this.setAttribute('aria-expanded', 'true');
                }
            }
        });
    });

    // Initialize current date for date fields
    const today = new Date();
    const formattedDate = today.toISOString().substring(0, 10);
    document.querySelectorAll('input[type="date"][data-default-today="true"]').forEach(input => {
        input.value = formattedDate;
    });

    // Save text fields to local storage temporarily as backup
    const autosaveFields = document.querySelectorAll('[data-autosave]');
    autosaveFields.forEach(field => {
        const storageKey = field.dataset.autosave;
        
        // Restore from localStorage if exists
        const savedValue = localStorage.getItem(storageKey);
        if (savedValue) {
            field.value = savedValue;
        }
        
        // Save to localStorage on input
        field.addEventListener('input', function() {
            localStorage.setItem(storageKey, this.value);
        });
    });

    // Clear autosave data when forms are submitted
    document.querySelectorAll('form[data-clear-autosave="true"]').forEach(form => {
        form.addEventListener('submit', function() {
            document.querySelectorAll('[data-autosave]').forEach(field => {
                localStorage.removeItem(field.dataset.autosave);
            });
        });
    });

    // Handle back button warning if there are unsaved changes
    const unsavedChangesWarning = document.querySelector('[data-unsaved-warning]');
    if (unsavedChangesWarning) {
        let formChanged = false;
        
        document.querySelectorAll('form input, form textarea, form select').forEach(field => {
            field.addEventListener('change', function() {
                formChanged = true;
            });
        });
        
        window.addEventListener('beforeunload', function(e) {
            if (formChanged) {
                e.preventDefault();
                e.returnValue = 'Existem alterações não salvas. Tem certeza que deseja sair desta página?';
                return e.returnValue;
            }
        });
        
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function() {
                formChanged = false;
            });
        });
    }

    // Handle file input visual enhancement
    document.querySelectorAll('.custom-file-input').forEach(fileInput => {
        fileInput.addEventListener('change', function() {
            const fileName = this.files[0] ? this.files[0].name : 'Nenhum arquivo selecionado';
            this.nextElementSibling.textContent = fileName;
        });
    });
});

/**
 * Format date string to Brazilian format
 * @param {string} dateStr - Date string in ISO format
 * @returns {string} Formatted date string (DD/MM/YYYY)
 */
function formatDate(dateStr) {
    if (!dateStr) return '';
    
    const date = new Date(dateStr);
    return date.toLocaleDateString('pt-BR');
}

/**
 * Format datetime string to Brazilian format with time
 * @param {string} dateStr - Datetime string in ISO format
 * @returns {string} Formatted datetime string (DD/MM/YYYY HH:mm)
 */
function formatDateTime(dateStr) {
    if (!dateStr) return '';
    
    const date = new Date(dateStr);
    return date.toLocaleDateString('pt-BR') + ' ' + date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

/**
 * Show a temporary notification message
 * @param {string} message - Message to display
 * @param {string} type - Alert type (success, danger, warning, info)
 * @param {number} duration - Duration in milliseconds
 */
function showNotification(message, type = 'info', duration = 3000) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.maxWidth = '400px';
    notification.style.boxShadow = '0 0.5rem 1rem rgba(0, 0, 0, 0.15)';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to document
    document.body.appendChild(notification);
    
    // Remove after duration
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(notification);
        bsAlert.close();
    }, duration);
}
