document.addEventListener('DOMContentLoaded', function() {
    console.log('Parking page JavaScript loaded!');
    
    // ===============================================
    // REAL-TIME SEARCH FUNCTIONALITY
    // ===============================================
    const searchInput = document.querySelector('.search-form input[name="search"]');
    
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase().trim();
            const parkingCards = document.querySelectorAll('.parking-slot-card');
            
            let visibleCount = 0;
            
            parkingCards.forEach(card => {
                // Get slot number
                const slotNumber = card.querySelector('.slot-number')?.textContent.toLowerCase() || '';
                
                // Get tenant name (if exists)
                const tenantNameElement = card.querySelector('.slot-info-item strong');
                const tenantName = tenantNameElement?.textContent.toLowerCase() || '';
                
                // Get unit number (if exists)
                const slotInfoItems = card.querySelectorAll('.slot-info-item');
                let unitNumber = '';
                slotInfoItems.forEach(item => {
                    const itemText = item.textContent.toLowerCase();
                    if (itemText.includes('unit')) {
                        unitNumber = itemText;
                    }
                });
                
                // Combine all searchable text
                const searchableText = `${slotNumber} ${tenantName} ${unitNumber}`;
                
                // Show or hide based on search
                if (searchableText.includes(searchTerm)) {
                    card.style.display = 'block';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });
            
            // Handle "No results" message
            const parkingGrid = document.querySelector('.parking-grid');
            let noResultsDiv = document.querySelector('.no-results-parking');
            
            if (visibleCount === 0 && parkingCards.length > 0 && searchTerm !== '') {
                if (!noResultsDiv) {
                    noResultsDiv = document.createElement('div');
                    noResultsDiv.className = 'no-results-parking tenants-table-container';
                    noResultsDiv.style.cssText = 'text-align: center; padding: 60px 24px; margin-top: 20px; grid-column: 1 / -1;';
                    noResultsDiv.innerHTML = `
                        <i class="fas fa-search" style="font-size: 64px; color: #d1d5db; margin-bottom: 16px; display: block;"></i>
                        <h3 style="font-size: 20px; color: #6b7280; margin-bottom: 8px;">No Parking Slots Found</h3>
                        <p style="color: #9ca3af; margin: 0;">No results for "${searchTerm}". Try a different search term.</p>
                    `;
                    parkingGrid.appendChild(noResultsDiv);
                } else {
                    noResultsDiv.style.display = 'block';
                    noResultsDiv.querySelector('p').textContent = `No results for "${searchTerm}". Try a different search term.`;
                }
            } else if (noResultsDiv) {
                noResultsDiv.style.display = 'none';
            }
        });
        
        // Clear search on Escape key
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                searchInput.value = '';
                searchInput.dispatchEvent(new Event('input'));
            }
        });
    }
    
    // ===============================================
    // ASSIGN PARKING MODAL
    // ===============================================
    const assignBtn = document.getElementById('assignParkingBtn');
    const assignModal = document.getElementById('assignParkingModal');
    const assignModalOverlay = document.getElementById('assignModalOverlay');
    const closeAssignModal = document.getElementById('closeAssignModal');
    const cancelAssignBtn = document.getElementById('cancelAssignBtn');
    
    function openAssignModal() {
        if (assignModal) {
            assignModal.classList.add('show');
            document.body.style.overflow = 'hidden';
        }
    }
    
    function closeAssignModalFunc() {
        if (assignModal) {
            assignModal.classList.remove('show');
            document.body.style.overflow = 'auto';
            // Reset form
            const form = assignModal.querySelector('form');
            if (form) form.reset();
            const preview = document.getElementById('assignmentPreview');
            if (preview) preview.style.display = 'none';
        }
    }
    
    if (assignBtn) {
        assignBtn.addEventListener('click', openAssignModal);
    }
    
    if (closeAssignModal) {
        closeAssignModal.addEventListener('click', closeAssignModalFunc);
    }
    
    if (cancelAssignBtn) {
        cancelAssignBtn.addEventListener('click', closeAssignModalFunc);
    }
    
    if (assignModalOverlay) {
        assignModalOverlay.addEventListener('click', closeAssignModalFunc);
    }
    
    // Close modal on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && assignModal && assignModal.classList.contains('show')) {
            closeAssignModalFunc();
        }
    });
    
    // ===============================================
    // ASSIGNMENT PREVIEW
    // ===============================================
    const residentSelect = document.getElementById('resident_id');
    const slotSelect = document.getElementById('slot_number');
    
    function updateAssignmentPreview() {
        const preview = document.getElementById('assignmentPreview');
        const previewText = document.getElementById('previewText');
        
        if (!residentSelect || !slotSelect || !preview || !previewText) return;
        
        const selectedResident = residentSelect.options[residentSelect.selectedIndex];
        const selectedSlot = slotSelect.value;
        
        if (selectedResident.value && selectedSlot) {
            const tenantName = selectedResident.text.split(' - ')[0];
            const unit = selectedResident.getAttribute('data-unit');
            preview.style.display = 'block';
            previewText.textContent = `Assigning ${selectedSlot} to ${tenantName} (Unit ${unit})`;
        } else {
            preview.style.display = 'none';
        }
    }
    
    if (residentSelect) {
        residentSelect.addEventListener('change', updateAssignmentPreview);
    }
    
    if (slotSelect) {
        slotSelect.addEventListener('change', updateAssignmentPreview);
    }
});

// ===============================================
// UNASSIGN PARKING (Global function with custom dialog)
// ===============================================
function unassignParking(slotId, slotNumber) {
    // Create custom confirm dialog
    const overlay = document.createElement('div');
    overlay.className = 'custom-confirm-overlay';
    
    overlay.innerHTML = `
        <div class="custom-confirm-dialog">
            <div class="custom-confirm-header">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Confirm Unassign</h3>
            </div>
            <div class="custom-confirm-body">
                <p>Are you sure you want to unassign <strong>${slotNumber}</strong>?</p>
                <p class="warning-text">This will make the slot available for other tenants.</p>
            </div>
            <div class="custom-confirm-actions">
                <button class="btn-secondary" onclick="this.closest('.custom-confirm-overlay').remove()">Cancel</button>
                <button class="btn-danger" onclick="window.location.href='/parking/unassign/${slotId}/'">
                    <i class="fas fa-times"></i> Unassign Slot
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    // Close on overlay click
    overlay.addEventListener('click', function(e) {
        if (e.target === overlay) {
            overlay.remove();
        }
    });
}