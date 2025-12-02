// Rent Collection JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Real-time search
    const searchInput = document.getElementById('searchInput');
    const tableRows = document.querySelectorAll('.tenants-table tbody tr[data-payment-id]');

    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            
            tableRows.forEach(row => {
                const tenant = (row.dataset.tenant || '').toLowerCase();
                const unit = (row.dataset.unit || '').toLowerCase();
                const month = row.dataset.monthName;
                const phone = (row.dataset.phone || '').toLowerCase();
                
                const matches = tenant.includes(searchTerm) || 
                               unit.includes(searchTerm) || 
                               month.includes(searchTerm) ||
                               phone.includes(searchTerm);
                
                row.style.display = matches ? '' : 'none';
            });
        });
    }
    
    // Record Payment Modal
    const recordPaymentModal = document.getElementById('recordPaymentModal');
    const paymentModalOverlay = document.getElementById('paymentModalOverlay');
    const closePaymentModal = document.getElementById('closePaymentModal');
    const cancelPaymentBtn = document.getElementById('cancelPaymentBtn');
    const recordPaymentForm = document.getElementById('recordPaymentForm');
    const recordPaymentButtons = document.querySelectorAll('.record-payment-btn');
    
    // Set today's date as default
    const today = new Date().toISOString().split('T')[0];
    if (document.getElementById('payment_date')) {
        document.getElementById('payment_date').value = today;
    }
    
    recordPaymentButtons.forEach(button => {
        button.addEventListener('click', function() {
            const paymentId = this.dataset.id;
            const tenant = this.dataset.tenant;
            const unit = this.dataset.unit;
            const month = this.dataset.month;
            const due = this.dataset.due;
            const paid = this.dataset.paid;
            const balance = this.dataset.balance;
            
            // Populate modal
            document.getElementById('paymentTenant').textContent = tenant;
            document.getElementById('paymentUnit').textContent = unit;
            document.getElementById('paymentMonth').textContent = month;
            document.getElementById('paymentDue').textContent = parseFloat(due).toFixed(0);
            document.getElementById('paymentPaid').textContent = parseFloat(paid).toFixed(0);
            document.getElementById('paymentBalance').textContent = parseFloat(balance).toFixed(0);
            
            // Set default amount to balance
            document.getElementById('amount_paid').value = parseFloat(balance).toFixed(0);
            
            // Update form action
            recordPaymentForm.action = `/rent/record/${paymentId}/`;
            
            // Show modal
            recordPaymentModal.classList.add('show');
        });
    });
    
    if (closePaymentModal) {
        closePaymentModal.addEventListener('click', () => {
            recordPaymentModal.classList.remove('show');
        });
    }
    
    if (cancelPaymentBtn) {
        cancelPaymentBtn.addEventListener('click', () => {
            recordPaymentModal.classList.remove('show');
        });
    }
    
    if (paymentModalOverlay) {
        paymentModalOverlay.addEventListener('click', () => {
            recordPaymentModal.classList.remove('show');
        });
    }
    
    // Generate Invoices
    const generateInvoicesBtn = document.getElementById('generateInvoicesBtn');
    
    if (generateInvoicesBtn) {
        generateInvoicesBtn.addEventListener('click', function() {
            const nextMonth = new Date();
            nextMonth.setMonth(nextMonth.getMonth() + 1);
            const monthName = nextMonth.toLocaleString('default', { month: 'long', year: 'numeric' });
            
            if (confirm(`Generate rent invoices for ${monthName}?`)) {
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '/rent/generate/';
                
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrfmiddlewaretoken';
                csrfInput.value = csrfToken;
                form.appendChild(csrfInput);
                
                document.body.appendChild(form);
                form.submit();
            }
        });
    }
    
    // ESC key to close modal
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            recordPaymentModal?.classList.remove('show');
        }
    });
});