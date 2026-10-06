/**
 * AttendX Pro - Frontend Interactive Logic
 * Handles modals, notifications, table filtering, and dynamic interactions
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log('AttendX Pro System Initialized.');
    
    // Auto-dismiss alert notifications after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.4s ease';
            setTimeout(() => alert.remove(), 400);
        }, 5000);
    });
});

/**
 * Toggle modal visibility by element ID
 * @param {string} modalId - The ID of the modal container
 */
function toggleModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.toggle('active');
    }
}

/**
 * Quick search filter for data tables
 * @param {string} inputId - ID of the search text input
 * @param {string} tableId - ID of the HTML table
 */
function filterTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    if (!input || !table) return;

    const filter = input.value.toLowerCase();
    const rows = table.getElementsByTagName('tr');

    for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        const cells = row.getElementsByTagName('td');
        let match = false;
        
        for (let j = 0; j < cells.length; j++) {
            if (cells[j] && cells[j].innerText.toLowerCase().includes(filter)) {
                match = true;
                break;
            }
        }
        
        row.style.display = match ? '' : 'none';
    }
}
