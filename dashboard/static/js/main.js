// Main JavaScript for Jirani App Dashboard

document.addEventListener('DOMContentLoaded', function() {
    
    // Smooth scroll for navigation
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Active nav link highlighting
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // User dropdown toggle
const userProfileBtn = document.getElementById('userProfileBtn');
const dropdownMenu = document.getElementById('dropdownMenu');

if (userProfileBtn && dropdownMenu) {
    // Toggle dropdown
    userProfileBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        dropdownMenu.classList.toggle('show');
        userProfileBtn.classList.toggle('active');
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!userProfileBtn.contains(e.target) && !dropdownMenu.contains(e.target)) {
            dropdownMenu.classList.remove('show');
            userProfileBtn.classList.remove('active');
        }
    });
    
    // Close dropdown when clicking a link
    const dropdownItems = dropdownMenu.querySelectorAll('.dropdown-item');
    dropdownItems.forEach(item => {
        item.addEventListener('click', function() {
            dropdownMenu.classList.remove('show');
            userProfileBtn.classList.remove('active');
        });
    });
}
    
    // Search functionality
    const searchInput = document.querySelector('.search-box input');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const contacts = document.querySelectorAll('.contact-item');
            
            contacts.forEach(contact => {
                const name = contact.querySelector('.contact-name').textContent.toLowerCase();
                const message = contact.querySelector('.contact-message').textContent.toLowerCase();
                
                if (name.includes(searchTerm) || message.includes(searchTerm)) {
                    contact.style.display = 'flex';
                } else {
                    contact.style.display = 'none';
                }
            });
        });
    }
    
    // Notification bell animation
    const notificationBell = document.querySelector('.fa-bell');
    if (notificationBell) {
        notificationBell.addEventListener('click', function() {
            this.classList.add('ring');
            setTimeout(() => {
                this.classList.remove('ring');
            }, 1000);
        });
    }
    
    // Dynamic chart animation
    const bars = document.querySelectorAll('.bar');
    bars.forEach((bar, index) => {
        setTimeout(() => {
            bar.style.opacity = '0';
            bar.style.transform = 'scaleY(0)';
            bar.style.transition = 'all 0.5s ease';
            
            setTimeout(() => {
                bar.style.opacity = '1';
                bar.style.transform = 'scaleY(1)';
            }, 50);
        }, index * 100);
    });
    
    // Month selector
    const monthBtn = document.querySelector('.month-btn');
    if (monthBtn) {
        monthBtn.addEventListener('click', function() {
            console.log('Month selector clicked');
        });
    }
    
    console.log('Jirani App Dashboard loaded successfully!');
});

// Add CSS for bell ring animation
const style = document.createElement('style');
style.textContent = `
    @keyframes ring {
        0%, 100% { transform: rotate(0deg); }
        10%, 30%, 50%, 70%, 90% { transform: rotate(-10deg); }
        20%, 40%, 60%, 80% { transform: rotate(10deg); }
    }
    
    .fa-bell.ring {
        animation: ring 1s ease-in-out;
    }
`;
document.head.appendChild(style);