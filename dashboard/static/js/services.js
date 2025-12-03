// Services JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Real-time search
    const searchInput = document.getElementById('searchInput');
    const tableRows = document.querySelectorAll('.tenants-table tbody tr[data-order-id]');

    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            
            tableRows.forEach(row => {
                const title = (row.dataset.title || '').toLowerCase();
                const unit = (row.dataset.unit || '').toLowerCase();
                const orderNum = (row.dataset.ordernum || '').toLowerCase();
                
                const matches = title.includes(searchTerm) || 
                               unit.includes(searchTerm) || 
                               orderNum.includes(searchTerm);
                
                row.style.display = matches ? '' : 'none';
            });
        });
    }
    
    // Create Work Order Modal
    const createBtn = document.getElementById('createWorkOrderBtn');
    const createModal = document.getElementById('createWorkOrderModal');
    const createOverlay = document.getElementById('createModalOverlay');
    const closeCreate = document.getElementById('closeCreateModal');
    const cancelCreate = document.getElementById('cancelCreateBtn');
    
    if (createBtn) {
        createBtn.addEventListener('click', () => {
            createModal.classList.add('show');
        });
    }
    
    if (closeCreate) {
        closeCreate.addEventListener('click', () => {
            createModal.classList.remove('show');
        });
    }
    
    if (cancelCreate) {
        cancelCreate.addEventListener('click', () => {
            createModal.classList.remove('show');
        });
    }
    
    if (createOverlay) {
        createOverlay.addEventListener('click', () => {
            createModal.classList.remove('show');
        });
    }
    
    // View Order Modal
    const viewModal = document.getElementById('viewOrderModal');
    const viewOverlay = document.getElementById('viewOrderOverlay');
    const closeView = document.getElementById('closeViewOrder');
    const closeViewBtn = document.getElementById('closeViewOrderBtn');
    const viewButtons = document.querySelectorAll('.view-order-btn');
    
    viewButtons.forEach(button => {
        button.addEventListener('click', function() {
            const orderId = this.dataset.orderid;
            const title = this.dataset.title;
            const unit = this.dataset.unit;
            const category = this.dataset.category;
            const priority = this.dataset.priority;
            const contractor = this.dataset.contractor;
            const cost = this.dataset.cost;
            const description = this.dataset.description;
            
            document.getElementById('viewOrderId').textContent = orderId;
            document.getElementById('viewOrderTitle').textContent = title;
            document.getElementById('viewOrderUnit').textContent = unit;
            document.getElementById('viewOrderCategory').textContent = category;
            document.getElementById('viewOrderPriority').textContent = priority;
            document.getElementById('viewOrderContractor').textContent = contractor;
            document.getElementById('viewOrderCost').textContent = 'Ksh.' + parseFloat(cost).toFixed(2);
            document.getElementById('viewOrderDescription').textContent = description;
            
            viewModal.classList.add('show');
        });
    });
    
    if (closeView) {
        closeView.addEventListener('click', () => {
            viewModal.classList.remove('show');
        });
    }
    
    if (closeViewBtn) {
        closeViewBtn.addEventListener('click', () => {
            viewModal.classList.remove('show');
        });
    }
    
    if (viewOverlay) {
        viewOverlay.addEventListener('click', () => {
            viewModal.classList.remove('show');
        });
    }
    
    // Edit Order Modal
    const editModal = document.getElementById('editOrderModal');
    const editOverlay = document.getElementById('editOrderOverlay');
    const closeEdit = document.getElementById('closeEditOrder');
    const cancelEdit = document.getElementById('cancelEditBtn');
    const editForm = document.getElementById('editOrderForm');
    const editButtons = document.querySelectorAll('.edit-order-btn');
    
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const orderId = this.dataset.id;
            const title = this.dataset.title;
            const description = this.dataset.description;
            const category = this.dataset.category;
            const priority = this.dataset.priority;
            const status = this.dataset.status;
            const contractorId = this.dataset.contractorId;
            const cost = this.dataset.cost;
            
            document.getElementById('edit_order_id').value = orderId;
            document.getElementById('edit_title').value = title;
            document.getElementById('edit_description').value = description;
            document.getElementById('edit_category').value = category;
            document.getElementById('edit_priority').value = priority;
            document.getElementById('edit_status').value = status;
            document.getElementById('edit_contractor').value = contractorId;
            document.getElementById('edit_cost').value = cost;
            
            editForm.action = `/services/update/${orderId}/`;
            
            editModal.classList.add('show');
        });
    });
    
    if (closeEdit) {
        closeEdit.addEventListener('click', () => {
            editModal.classList.remove('show');
        });
    }
    
    if (cancelEdit) {
        cancelEdit.addEventListener('click', () => {
            editModal.classList.remove('show');
        });
    }
    
    if (editOverlay) {
        editOverlay.addEventListener('click', () => {
            editModal.classList.remove('show');
        });
    }
    
    // Delete Order Modal
    const deleteModal = document.getElementById('deleteOrderModal');
    const deleteOverlay = document.getElementById('deleteOrderOverlay');
    const closeDelete = document.getElementById('closeDeleteOrder');
    const cancelDelete = document.getElementById('cancelDeleteBtn');
    const confirmDelete = document.getElementById('confirmDeleteBtn');
    const deleteButtons = document.querySelectorAll('.delete-order-btn');
    
    let deleteOrderIdValue = null;
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            deleteOrderIdValue = this.dataset.id;
            const orderNum = this.dataset.orderid;
            
            document.getElementById('deleteOrderId').textContent = orderNum;
            
            deleteModal.classList.add('show');
        });
    });
    
    if (confirmDelete) {
        confirmDelete.addEventListener('click', () => {
            if (deleteOrderIdValue) {
                window.location.href = `/services/delete/${deleteOrderIdValue}/`;
            }
        });
    }
    
    if (closeDelete) {
        closeDelete.addEventListener('click', () => {
            deleteModal.classList.remove('show');
            deleteOrderIdValue = null;
        });
    }
    
    if (cancelDelete) {
        cancelDelete.addEventListener('click', () => {
            deleteModal.classList.remove('show');
            deleteOrderIdValue = null;
        });
    }
    
    if (deleteOverlay) {
        deleteOverlay.addEventListener('click', () => {
            deleteModal.classList.remove('show');
            deleteOrderIdValue = null;
        });
    }
    
    // ESC key to close modals
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            createModal?.classList.remove('show');
            viewModal?.classList.remove('show');
            editModal?.classList.remove('show');
            deleteModal?.classList.remove('show');
        }
    });
});