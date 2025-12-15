// Building Page JavaScript
// Save as: static/js/building.js

document.addEventListener('DOMContentLoaded', function() {
    
    // ========================================
    // MODAL FUNCTIONS
    // ========================================
    
    function openModal(modalId) {
        document.getElementById(modalId).classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    function closeModal(modalId) {
        document.getElementById(modalId).classList.remove('show');
        document.body.style.overflow = '';
    }
    
    window.openModal = openModal;
    window.closeModal = closeModal;

    // ========================================
    // CREATE MODAL
    // ========================================
    
    window.openCreateModal = function() {
        openModal('createModal');
    };

    // ========================================
    // EDIT MODAL
    // ========================================
    
    window.openEditModal = function(id, unitNumber, unitType, floor, sizeSqm, rentAmount, status, description) {
        document.getElementById('editForm').action = '/building/update/' + id + '/';
        document.getElementById('edit_unit_number').value = unitNumber;
        document.getElementById('edit_unit_type').value = unitType;
        document.getElementById('edit_floor').value = floor;
        document.getElementById('edit_size_sqm').value = sizeSqm;
        document.getElementById('edit_rent_amount').value = rentAmount;
        document.getElementById('edit_status').value = status;
        document.getElementById('edit_description').value = description;
        openModal('editModal');
    };

    window.openEditModalFromData = function(button) {
        var id = button.getAttribute('data-unit-id');
        var unitNumber = button.getAttribute('data-unit-number');
        var unitType = button.getAttribute('data-unit-type');
        var floor = button.getAttribute('data-floor');
        var sizeSqm = button.getAttribute('data-size');
        var rentAmount = button.getAttribute('data-rent');
        var status = button.getAttribute('data-status');
        var description = button.getAttribute('data-description');
        
        window.openEditModal(id, unitNumber, unitType, floor, sizeSqm, rentAmount, status, description);
    };

    // ========================================
    // ASSIGN TENANT MODAL
    // ========================================
    
    window.openAssignModal = function(unitId, unitNumber, currentResidentId) {
        document.getElementById('assignForm').action = '/building/assign/' + unitId + '/';
        document.getElementById('assign_unit_number').value = 'Unit ' + unitNumber;
        
        var residentSelect = document.getElementById('assign_resident_id');
        if (currentResidentId) {
            residentSelect.value = currentResidentId;
        } else {
            residentSelect.value = '';
        }
        
        openModal('assignModal');
    };

    window.openAssignModalFromData = function(button) {
        var unitId = button.getAttribute('data-unit-id');
        var unitNumber = button.getAttribute('data-unit-number');
        var residentId = button.getAttribute('data-resident-id') || null;
        
        window.openAssignModal(unitId, unitNumber, residentId);
    };

    // ========================================
    // DELETE UNIT WITH CUSTOM MODAL
    // ========================================
    
    window.deleteUnit = function(unitId, unitNumber) {
        // Create custom styled confirmation modal
        const confirmOverlay = document.createElement('div');
        confirmOverlay.className = 'custom-confirm-overlay';
        confirmOverlay.innerHTML = `
            <div class="custom-confirm-dialog">
                <div class="custom-confirm-header">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Confirm Delete</h3>
                </div>
                <div class="custom-confirm-body">
                    <p>Are you sure you want to delete <strong>Unit ${unitNumber}</strong>?</p>
                    <p class="warning-text">This action cannot be undone.</p>
                </div>
                <div class="custom-confirm-actions">
                    <button type="button" class="btn-secondary" onclick="this.closest('.custom-confirm-overlay').remove()">
                        Cancel
                    </button>
                    <button type="button" class="btn-danger" 
                            onclick="window.location.href='/building/delete/${unitId}/'">
                        <i class="fas fa-trash"></i> Delete Unit
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(confirmOverlay);
        
        // Close on overlay click
        confirmOverlay.addEventListener('click', function(e) {
            if (e.target === confirmOverlay) {
                confirmOverlay.remove();
            }
        });
        
        // Close on Escape key
        const escapeHandler = function(e) {
            if (e.key === 'Escape') {
                confirmOverlay.remove();
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);
    };

    // ========================================
    // CLOSE MODALS ON OVERLAY CLICK OR ESCAPE
    // ========================================
    
    window.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal-overlay')) {
            var modal = e.target.closest('.modal');
            if (modal) {
                closeModal(modal.id);
            }
        }
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            var modals = document.querySelectorAll('.modal.show');
            modals.forEach(function(modal) {
                closeModal(modal.id);
            });
        }
    });

    // ========================================
    // REAL-TIME SEARCH
    // ========================================
    
    const searchInput = document.querySelector('.search-form input[name="search"]');
    const unitCards = document.querySelectorAll('.parking-slot-card');
    
    if (searchInput && unitCards.length > 0) {
        // Debounce function
        function debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
        
        // Search function
        function performSearch() {
            const searchTerm = searchInput.value.toLowerCase().trim();
            let visibleCount = 0;
            
            unitCards.forEach(card => {
                // Get all searchable text from the card
                const unitNumber = card.querySelector('.slot-number')?.textContent.toLowerCase() || '';
                const unitType = card.querySelector('.slot-info-item:nth-child(1) span')?.textContent.toLowerCase() || '';
                const floor = card.querySelector('.slot-info-item:nth-child(2) span')?.textContent.toLowerCase() || '';
                const rent = card.querySelector('.slot-info-item:nth-child(4) span')?.textContent.toLowerCase() || '';
                const status = card.querySelector('.slot-status-badge')?.textContent.toLowerCase() || '';
                
                // Get tenant info if exists
                const tenantName = card.querySelector('.slot-info-item:nth-last-child(2) span')?.textContent.toLowerCase() || '';
                const tenantPhone = card.querySelector('.slot-info-item:last-child span')?.textContent.toLowerCase() || '';
                
                // Combine all searchable fields
                const searchableText = `${unitNumber} ${unitType} ${floor} ${rent} ${status} ${tenantName} ${tenantPhone}`;
                
                // Show/hide based on search match
                if (searchTerm === '' || searchableText.includes(searchTerm)) {
                    card.style.display = '';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });
            
            // Show/hide "no results" message
            let noResultsEl = document.getElementById('noResultsMessage');
            
            if (visibleCount === 0) {
                if (!noResultsEl) {
                    const container = document.querySelector('.parking-grid');
                    if (container) {
                        noResultsEl = document.createElement('div');
                        noResultsEl.id = 'noResultsMessage';
                        noResultsEl.style.cssText = 'text-align: center; padding: 60px 24px; grid-column: 1 / -1;';
                        noResultsEl.innerHTML = `
                            <i class="fas fa-search" style="font-size: 64px; color: #d1d5db; margin-bottom: 16px;"></i>
                            <h3 style="font-size: 20px; color: #6b7280; margin-bottom: 8px;">No Units Found</h3>
                            <p style="color: #9ca3af;">Try adjusting your search terms.</p>
                        `;
                        container.appendChild(noResultsEl);
                    }
                } else {
                    noResultsEl.style.display = 'block';
                }
            } else {
                if (noResultsEl) {
                    noResultsEl.style.display = 'none';
                }
            }
        }
        
        // Attach debounced search to input
        searchInput.addEventListener('input', debounce(performSearch, 300));
        
        // Prevent form submission and perform search instead
        const searchForm = searchInput.closest('.search-form');
        if (searchForm) {
            searchForm.addEventListener('submit', function(e) {
                e.preventDefault();
                performSearch();
            });
        }
        
        // Run search on page load if there's a value
        if (searchInput.value) {
            performSearch();
        }
    }

    // ========================================
    // AUTO-HIDE SUCCESS/ERROR MESSAGES
    // ========================================
    
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.animation = 'fadeOut 0.5s ease forwards';
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });

    console.log('Building page JavaScript loaded!');
});