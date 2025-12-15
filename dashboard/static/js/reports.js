document.addEventListener('DOMContentLoaded', function() {
    
    // ========================================
    // TAB SWITCHING
    // ========================================
    
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            
            // Remove active class from all tabs
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            document.getElementById(tabName).classList.add('active');
        });
    });

    // ========================================
    // FINANCIAL CHARTS
    // ========================================
    
    // Payment Trends Chart (Line Chart)
    const paymentTrendsCtx = document.getElementById('paymentTrendsChart');
    if (paymentTrendsCtx) {
        new Chart(paymentTrendsCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [{
                    label: 'Collected',
                    data: [450000, 480000, 470000, 520000, 510000, 540000, 550000, 560000, 580000, 590000, 600000, 610000],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Expected',
                    data: [600000, 600000, 600000, 600000, 600000, 600000, 600000, 600000, 600000, 600000, 600000, 600000],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    borderDash: [5, 5],
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': Ksh.' + context.parsed.y.toLocaleString();
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return 'Ksh.' + (value / 1000) + 'k';
                            }
                        }
                    }
                }
            }
        });
    }

    // Payment Status Chart (Doughnut Chart)
    const paymentStatusCtx = document.getElementById('paymentStatusChart');
    if (paymentStatusCtx) {
        new Chart(paymentStatusCtx, {
            type: 'doughnut',
            data: {
                labels: ['Paid', 'Partial', 'Pending', 'Overdue'],
                datasets: [{
                    data: [85, 5, 6, 4],
                    backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    // ========================================
    // OCCUPANCY CHARTS
    // ========================================
    
    // Occupancy Trends Chart (Area Chart)
    const occupancyTrendsCtx = document.getElementById('occupancyTrendsChart');
    if (occupancyTrendsCtx) {
        new Chart(occupancyTrendsCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [{
                    label: 'Occupancy Rate %',
                    data: [75, 78, 82, 85, 87, 90, 92, 88, 90, 91, 93, 95],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.2)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    // Unit Types Chart (Bar Chart)
    const unitTypesCtx = document.getElementById('unitTypesChart');
    if (unitTypesCtx) {
        new Chart(unitTypesCtx, {
            type: 'bar',
            data: {
                labels: ['Studio', '1 Bedroom', '2 Bedroom', '3 Bedroom'],
                datasets: [{
                    label: 'Total Units',
                    data: [80, 80, 80, 80],
                    backgroundColor: '#e5e7eb'
                }, {
                    label: 'Occupied',
                    data: [70, 75, 72, 78],
                    backgroundColor: '#10b981'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // ========================================
    // MAINTENANCE CHARTS
    // ========================================
    
    // Maintenance Category Chart (Bar Chart)
    const maintenanceCategoryCtx = document.getElementById('maintenanceCategoryChart');
    if (maintenanceCategoryCtx) {
        new Chart(maintenanceCategoryCtx, {
            type: 'bar',
            data: {
                labels: ['Plumbing', 'Electrical', 'HVAC', 'Cleaning', 'Security', 'Landscaping', 'Painting', 'Other'],
                datasets: [{
                    label: 'Work Orders',
                    data: [25, 18, 12, 30, 8, 15, 10, 20],
                    backgroundColor: [
                        '#3b82f6',
                        '#f59e0b',
                        '#8b5cf6',
                        '#14b8a6',
                        '#ef4444',
                        '#10b981',
                        '#ec4899',
                        '#6b7280'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Maintenance Cost Chart (Line Chart)
    const maintenanceCostCtx = document.getElementById('maintenanceCostChart');
    if (maintenanceCostCtx) {
        new Chart(maintenanceCostCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [{
                    label: 'Maintenance Cost',
                    data: [45000, 52000, 48000, 55000, 50000, 58000, 54000, 60000, 56000, 62000, 59000, 65000],
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return 'Cost: Ksh.' + context.parsed.y.toLocaleString();
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return 'Ksh.' + (value / 1000) + 'k';
                            }
                        }
                    }
                }
            }
        });
    }

    // ========================================
    // EXPORT FUNCTIONS
    // ========================================
    
    window.exportReport = function(format) {
        const activeTab = document.querySelector('.tab-btn.active').getAttribute('data-tab');
        alert(`Exporting ${activeTab} report as ${format.toUpperCase()}...\n\nThis feature will be implemented with backend integration.`);
        // TODO: Implement actual export functionality
        // window.location.href = `/reports/export/${activeTab}/${format}/`;
    };

    window.exportTenantReport = function() {
        alert('Exporting tenant reports...\n\nThis feature will be implemented with backend integration.');
        // TODO: Implement actual export functionality
        // window.location.href = '/reports/export/tenants/excel/';
    };

    // ========================================
    // TENANT SEARCH
    // ========================================
    
    const tenantSearch = document.getElementById('tenantSearch');
    if (tenantSearch) {
        tenantSearch.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const tableRows = document.querySelectorAll('#tenants .data-table tbody tr');
            
            tableRows.forEach(row => {
                const tenantName = row.querySelector('.tenant-name')?.textContent.toLowerCase() || '';
                const tenantEmail = row.querySelector('.tenant-email')?.textContent.toLowerCase() || '';
                const unitNumber = row.querySelector('.unit-badge')?.textContent.toLowerCase() || '';
                
                if (tenantName.includes(searchTerm) || 
                    tenantEmail.includes(searchTerm) || 
                    unitNumber.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    console.log('Reports page loaded successfully!');
});