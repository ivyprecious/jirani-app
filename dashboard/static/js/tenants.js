// Tenants Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Modal elements
    const addTenantBtn = document.getElementById('addTenantBtn');
    const modal = document.getElementById('addTenantModal');
    const modalOverlay = document.getElementById('modalOverlay');
    const closeModal = document.getElementById('closeModal');
    const cancelBtn = document.getElementById('cancelBtn');
    
    // Open modal
    if (addTenantBtn) {
        addTenantBtn.addEventListener('click', function() {
            modal.classList.add('show');
            document.body.style.overflow = 'hidden'; // Prevent background scroll
        });
    }
    
    // Close modal function
    function closeModalFunc() {
        modal.classList.remove('show');
        document.body.style.overflow = 'auto';
    }
    
    // Close modal on X button
    if (closeModal) {
        closeModal.addEventListener('click', closeModalFunc);
    }
    
    // Close modal on Cancel button
    if (cancelBtn) {
        cancelBtn.addEventListener('click', closeModalFunc);
    }
    
    // Close modal on overlay click
    if (modalOverlay) {
        modalOverlay.addEventListener('click', closeModalFunc);
    }
    
    // Close modal on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.classList.contains('show')) {
            closeModalFunc();
        }
    });
    
    // Form validation
    const form = document.querySelector('.modal-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const phone = document.getElementById('phone').value;
            const unitNumber = document.getElementById('unit_number').value;
            const rent = document.getElementById('monthly_rent').value;
            
            // Validate phone format
            if (!phone.startsWith('+254')) {
                alert('Phone number must start with +254');
                e.preventDefault();
                return false;
            }
            
            // Validate unit number
            if (unitNumber.trim() === '') {
                alert('Please enter a unit number');
                e.preventDefault();
                return false;
            }
            
            // Validate rent
            if (parseFloat(rent) <= 0) {
                alert('Rent must be greater than 0');
                e.preventDefault();
                return false;
            }
            
            return true;
        });
    }
    
    console.log('Tenants page JavaScript loaded!');

    // Auto-hide messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.animation = 'fadeOut 0.5s ease forwards';
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });
    
    console.log('Tenants page JavaScript loaded!');

    // Real-time search functionality
    const searchInput = document.querySelector('.search-form input[name="search"]');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const tableRows = document.querySelectorAll('.tenants-table tbody tr');
            
            tableRows.forEach(row => {
                const tenantName = row.querySelector('.tenant-name')?.textContent.toLowerCase() || '';
                const tenantEmail = row.querySelector('.tenant-email')?.textContent.toLowerCase() || '';
                const unitNumber = row.querySelector('.unit-badge')?.textContent.toLowerCase() || '';
                const phoneNumber = row.querySelectorAll('td')[2]?.textContent.toLowerCase() || '';
                
                // Check if search term matches any field
                if (tenantName.includes(searchTerm) || 
                    tenantEmail.includes(searchTerm) || 
                    unitNumber.includes(searchTerm) || 
                    phoneNumber.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
            
            // Show "No results" message if all hidden
            const visibleRows = Array.from(tableRows).filter(row => row.style.display !== 'none');
            if (visibleRows.length === 0 && searchTerm !== '') {
                // Add "no results" row if it doesn't exist
                let noResultsRow = document.querySelector('.no-results-row');
                if (!noResultsRow) {
                    noResultsRow = document.createElement('tr');
                    noResultsRow.className = 'no-results-row';
                    noResultsRow.innerHTML = `
                        <td colspan="7" style="text-align: center; padding: 40px; color: #6b7280;">
                            <i class="fas fa-search" style="font-size: 48px; margin-bottom: 16px; opacity: 0.3;"></i>
                            <div>No tenants found matching "${searchTerm}"</div>
                        </td>
                    `;
                    document.querySelector('.tenants-table tbody').appendChild(noResultsRow);
                }
            } else {
                // Remove "no results" row if it exists
                const noResultsRow = document.querySelector('.no-results-row');
                if (noResultsRow) {
                    noResultsRow.remove();
                }
            }
        });
    }
    
    console.log('Tenants page JavaScript loaded!');

    // View Tenant Details
    const viewButtons = document.querySelectorAll('.btn-icon[title="View Details"]');
    const viewModal = document.getElementById('viewTenantModal');
    const viewModalOverlay = document.getElementById('viewModalOverlay');
    const closeViewModal = document.getElementById('closeViewModal');
    const closeViewModalBtn = document.getElementById('closeViewModalBtn');
    
    viewButtons.forEach(button => {
        button.addEventListener('click', function() {
            const row = this.closest('tr');
            
            // Extract data from the row
            const name = row.querySelector('.tenant-name').textContent;
            const email = row.querySelector('.tenant-email').textContent;
            const unit = row.querySelector('.unit-badge').textContent;
            const phone = row.querySelectorAll('td')[2].textContent;
            const moveIn = row.querySelectorAll('td')[3].textContent;
            const rent = row.querySelectorAll('td')[4].textContent;
            const status = row.querySelector('.status-badge').textContent.trim();
            
            // Populate modal
            document.getElementById('detailName').textContent = name;
            document.getElementById('detailEmail').textContent = email;
            document.getElementById('detailUnit').textContent = unit;
            document.getElementById('detailPhone').textContent = phone;
            document.getElementById('detailMoveIn').textContent = moveIn;
            document.getElementById('detailRent').textContent = rent;
            document.getElementById('detailStatus').textContent = status;
            
            // Show modal
            viewModal.classList.add('show');
            document.body.style.overflow = 'hidden';
        });
    });
    
    function closeViewModalFunc() {
        viewModal.classList.remove('show');
        document.body.style.overflow = 'auto';
    }
    
    if (closeViewModal) {
        closeViewModal.addEventListener('click', closeViewModalFunc);
    }
    
    if (closeViewModalBtn) {
        closeViewModalBtn.addEventListener('click', closeViewModalFunc);
    }
    
    if (viewModalOverlay) {
        viewModalOverlay.addEventListener('click', closeViewModalFunc);
    }
    
    // Edit Button
    const editButtons = document.querySelectorAll('.btn-icon[title="Edit"]');
    const editModal = document.getElementById('editTenantModal');
    const editModalOverlay = document.getElementById('editModalOverlay');
    const closeEditModal = document.getElementById('closeEditModal');
    const cancelEditBtn = document.getElementById('cancelEditBtn');
    const editForm = document.getElementById('editTenantForm');
    
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const row = this.closest('tr');
            const residentId = row.getAttribute('data-resident-id');
            
            // Extract current data from the row
            const name = row.querySelector('.tenant-name').textContent.trim().split(' ');
            const firstName = name[0];
            const lastName = name.slice(1).join(' ');
            const email = row.querySelector('.tenant-email').textContent.trim();
            const unit = row.querySelector('.unit-badge').textContent.trim();
            const phone = row.querySelectorAll('td')[2].textContent.trim();
            const moveIn = row.querySelectorAll('td')[3].getAttribute('data-date') || row.querySelectorAll('td')[3].textContent;
            const rent = row.querySelectorAll('td')[4].textContent.trim().replace('Ksh.', '').replace(',', '');
            const statusBadge = row.querySelector('.status-badge');
            let status = 'active';
            if (statusBadge.classList.contains('pending')) status = 'pending';
            if (statusBadge.classList.contains('moved-out')) status = 'moved_out';
            
            // Populate form
            document.getElementById('edit_resident_id').value = residentId;
            document.getElementById('edit_first_name').value = firstName;
            document.getElementById('edit_last_name').value = lastName;
            document.getElementById('edit_email').value = email;
            document.getElementById('edit_phone').value = phone;
            document.getElementById('edit_unit_number').value = unit;
            document.getElementById('edit_monthly_rent').value = rent;
            
            // Format date for input (convert "Jan 20, 2024" to "2024-01-20")
            const dateStr = row.querySelectorAll('td')[3].textContent.trim();
            const date = new Date(dateStr);
            const formattedDate = date.toISOString().split('T')[0];
            document.getElementById('edit_move_in_date').value = formattedDate;
            
            document.getElementById('edit_status').value = status;
            
            // Update form action
            editForm.action = `/tenants/edit/${residentId}/`;
            
            // Show modal
            editModal.classList.add('show');
            document.body.style.overflow = 'hidden';
        });
    });
    
    function closeEditModalFunc() {
        editModal.classList.remove('show');
        document.body.style.overflow = 'auto';
    }
    
    if (closeEditModal) {
        closeEditModal.addEventListener('click', closeEditModalFunc);
    }
    
    if (cancelEditBtn) {
        cancelEditBtn.addEventListener('click', closeEditModalFunc);
    }
    
    if (editModalOverlay) {
        editModalOverlay.addEventListener('click', closeEditModalFunc);
    }
    
    // Message Button (placeholder)
    const messageButtons = document.querySelectorAll('.btn-icon[title="Message"]');
    messageButtons.forEach(button => {
        button.addEventListener('click', function() {
            const row = this.closest('tr');
            const name = row.querySelector('.tenant-name').textContent;
            const email = row.querySelector('.tenant-email').textContent;
            alert(`Send message to ${name} (${email})\n\nEmail/SMS functionality coming soon!`);
        });
    });
    
    console.log('Tenants page JavaScript loaded!');
// Delete Button with Custom Modal
    const deleteButtons = document.querySelectorAll('.btn-icon.btn-delete');
    const deleteModal = document.getElementById('deleteConfirmModal');
    const deleteModalOverlay = document.getElementById('deleteModalOverlay');
    const closeDeleteModal = document.getElementById('closeDeleteModal');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    let deleteResidentId = null;
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const row = this.closest('tr');
            deleteResidentId = row.getAttribute('data-resident-id');
            const name = row.querySelector('.tenant-name').textContent.trim();
            
            // Set tenant name in modal
            document.getElementById('deleteTenantName').textContent = name;
            
            // Show modal
            deleteModal.classList.add('show');
            document.body.style.overflow = 'hidden';
        });
    });
    
    function closeDeleteModalFunc() {
        deleteModal.classList.remove('show');
        document.body.style.overflow = 'auto';
        deleteResidentId = null;
    }
    
    if (closeDeleteModal) {
        closeDeleteModal.addEventListener('click', closeDeleteModalFunc);
    }
    
    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', closeDeleteModalFunc);
    }
    
    if (deleteModalOverlay) {
        deleteModalOverlay.addEventListener('click', closeDeleteModalFunc);
    }
    
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', function() {
            if (deleteResidentId) {
                window.location.href = `/tenants/delete/${deleteResidentId}/`;
            }
        });
    }
    
    console.log('Tenants page JavaScript loaded!');
});