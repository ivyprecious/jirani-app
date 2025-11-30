// ========================================
// SUBCONTRACTORS.JS - Modal & Interactions
// ========================================

console.log('Subcontractors JS loaded!');

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing subcontractors page...');

    // ========================================
    // CATEGORY FILTER FUNCTION
    // ========================================
    window.filterByCategory = function(category) {
        const urlParams = new URLSearchParams(window.location.search);
        const currentStatus = urlParams.get('status') || 'all';
        window.location.href = `?status=${currentStatus}&category=${category}`;
    };

    // ========================================
    // SEARCH FUNCTIONALITY
    // ========================================
    const searchInput = document.getElementById('searchInput');
    const searchForm = document.getElementById('searchForm');

    if (searchInput && searchForm) {
        console.log('Search elements found');
        
        // Submit search on Enter key
        searchInput.addEventListener('keyup', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                searchForm.submit();
            }
        });

        // Also allow clicking search icon
        const searchIcon = searchForm.querySelector('.fa-search');
        if (searchIcon) {
            searchIcon.style.cursor = 'pointer';
            searchIcon.addEventListener('click', function() {
                searchForm.submit();
            });
        }
    } else {
        console.log('Search elements not found');
    }

    // ========================================
    // ADD SUBCONTRACTOR MODAL
    // ========================================
    const addBtn = document.getElementById('addSubcontractorBtn');
    const addModal = document.getElementById('addSubcontractorModal');
    const addModalOverlay = document.getElementById('modalOverlay');
    const closeAddModal = document.getElementById('closeModal');
    const cancelAddBtn = document.getElementById('cancelBtn');

    console.log('Add button:', addBtn);
    console.log('Add modal:', addModal);

    if (addBtn && addModal) {
        addBtn.addEventListener('click', function() {
            console.log('Add button clicked');
            addModal.classList.add('show');
        });
    }

    if (closeAddModal && addModal) {
        closeAddModal.addEventListener('click', function() {
            console.log('Close add modal');
            addModal.classList.remove('show');
        });
    }

    if (cancelAddBtn && addModal) {
        cancelAddBtn.addEventListener('click', function() {
            console.log('Cancel add button clicked');
            addModal.classList.remove('show');
        });
    }

    if (addModalOverlay && addModal) {
        addModalOverlay.addEventListener('click', function() {
            console.log('Modal overlay clicked');
            addModal.classList.remove('show');
        });
    }

    // ========================================
    // VIEW CONTRACTOR MODAL
    // ========================================
    const viewModal = document.getElementById('viewContractorModal');
    const viewModalOverlay = document.getElementById('viewModalOverlay');
    const closeViewModal = document.getElementById('closeViewModal');
    const closeViewModalBtn = document.getElementById('closeViewModalBtn');

    console.log('View modal:', viewModal);

    // Get all view buttons
    const viewButtons = document.querySelectorAll('.view-contractor-btn');
    console.log('Found', viewButtons.length, 'view buttons');

    viewButtons.forEach(button => {
        button.addEventListener('click', function() {
            console.log('View button clicked');
            
            const row = this.closest('tr');
            
            // Extract data from data attributes
            const name = row.dataset.name;
            const email = row.dataset.email;
            const company = row.dataset.company;
            const category = row.querySelector('.category-badge').textContent.trim();
            const phone = row.dataset.phone;
            const rating = row.dataset.rating;
            const workOrders = row.dataset.workOrders;
            const status = row.querySelector('.status-badge').textContent.trim();
            const notes = row.dataset.notes || 'No additional notes';
            
            // Populate modal
            document.getElementById('detailName').textContent = name;
            document.getElementById('detailEmail').textContent = email;
            document.getElementById('detailCompany').textContent = company;
            document.getElementById('detailCategory').textContent = category;
            document.getElementById('detailPhone').textContent = phone;
            document.getElementById('detailRating').textContent = rating + ' / 5.0';
            document.getElementById('detailWorkOrders').textContent = workOrders;
            document.getElementById('detailStatus').textContent = status;
            document.getElementById('detailNotes').textContent = notes;
            
            // Show modal
            viewModal.classList.add('show');
        });
    });

    if (closeViewModal && viewModal) {
        closeViewModal.addEventListener('click', function() {
            viewModal.classList.remove('show');
        });
    }

    if (closeViewModalBtn && viewModal) {
        closeViewModalBtn.addEventListener('click', function() {
            viewModal.classList.remove('show');
        });
    }

    if (viewModalOverlay && viewModal) {
        viewModalOverlay.addEventListener('click', function() {
            viewModal.classList.remove('show');
        });
    }

    // ========================================
    // EDIT CONTRACTOR MODAL
    // ========================================
    const editModal = document.getElementById('editContractorModal');
    const editModalOverlay = document.getElementById('editModalOverlay');
    const closeEditModal = document.getElementById('closeEditModal');
    const cancelEditBtn = document.getElementById('cancelEditBtn');
    const editForm = document.getElementById('editContractorForm');

    console.log('Edit modal:', editModal);

    // Get all edit buttons
    const editButtons = document.querySelectorAll('.edit-contractor-btn');
    console.log('Found', editButtons.length, 'edit buttons');

    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            console.log('Edit button clicked');
            
            const row = this.closest('tr');
            const contractorId = row.dataset.contractorId;
            
            // Extract data from data attributes
            const name = row.dataset.name;
            const email = row.dataset.email;
            const company = row.dataset.company;
            const phone = row.dataset.phone;
            const category = row.dataset.category;
            const status = row.dataset.status;
            const notes = row.dataset.notes || '';
            
            // Populate edit form
            document.getElementById('edit_contractor_id').value = contractorId;
            document.getElementById('edit_name').value = name;
            document.getElementById('edit_company_name').value = company;
            document.getElementById('edit_category').value = category;
            document.getElementById('edit_phone').value = phone;
            document.getElementById('edit_email').value = email;
            document.getElementById('edit_status').value = status;
            document.getElementById('edit_notes').value = notes;
            
            // Update form action
            editForm.action = `/subcontractors/edit/${contractorId}/`;
            
            // Show modal
            editModal.classList.add('show');
        });
    });

    if (closeEditModal && editModal) {
        closeEditModal.addEventListener('click', function() {
            editModal.classList.remove('show');
        });
    }

    if (cancelEditBtn && editModal) {
        cancelEditBtn.addEventListener('click', function() {
            editModal.classList.remove('show');
        });
    }

    if (editModalOverlay && editModal) {
        editModalOverlay.addEventListener('click', function() {
            editModal.classList.remove('show');
        });
    }

    // ========================================
    // DELETE CONTRACTOR MODAL
    // ========================================
    const deleteModal = document.getElementById('deleteConfirmModal');
    const deleteModalOverlay = document.getElementById('deleteModalOverlay');
    const closeDeleteModal = document.getElementById('closeDeleteModal');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');

    console.log('Delete modal:', deleteModal);

    let deleteContractorId = null;

    // Get all delete buttons
    const deleteButtons = document.querySelectorAll('.delete-contractor-btn');
    console.log('Found', deleteButtons.length, 'delete buttons');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            console.log('Delete button clicked');
            
            const row = this.closest('tr');
            deleteContractorId = row.dataset.contractorId;
            const name = row.dataset.name;
            
            // Populate delete modal
            document.getElementById('deleteContractorName').textContent = name;
            
            // Show modal
            deleteModal.classList.add('show');
        });
    });

    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', function() {
            console.log('Confirm delete clicked for ID:', deleteContractorId);
            if (deleteContractorId) {
                // Redirect to delete URL
                window.location.href = `/subcontractors/delete/${deleteContractorId}/`;
            }
        });
    }

    if (closeDeleteModal && deleteModal) {
        closeDeleteModal.addEventListener('click', function() {
            deleteModal.classList.remove('show');
            deleteContractorId = null;
        });
    }

    if (cancelDeleteBtn && deleteModal) {
        cancelDeleteBtn.addEventListener('click', function() {
            deleteModal.classList.remove('show');
            deleteContractorId = null;
        });
    }

    if (deleteModalOverlay && deleteModal) {
        deleteModalOverlay.addEventListener('click', function() {
            deleteModal.classList.remove('show');
            deleteContractorId = null;
        });
    }

    // ========================================
    // CLOSE ALL MODALS ON ESC KEY
    // ========================================
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (addModal) addModal.classList.remove('show');
            if (viewModal) viewModal.classList.remove('show');
            if (editModal) editModal.classList.remove('show');
            if (deleteModal) deleteModal.classList.remove('show');
        }
    });
    // ========================================
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (addModal) addModal.classList.remove('active');
            if (viewModal) viewModal.classList.remove('active');
            if (editModal) editModal.classList.remove('active');
            if (deleteModal) deleteModal.classList.remove('active');
        }
    });

    console.log('Subcontractors page initialized successfully!');
});