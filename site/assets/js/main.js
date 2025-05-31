// Sidebar navigation links
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        this.classList.add('active');
        alert(`Sidebar: ${this.textContent.trim()} clicked`);
    });
});

// Profile section
const profileSection = document.querySelector('.profile-section');
if (profileSection) {
    profileSection.addEventListener('click', () => {
        alert('Profile section clicked!');
    });
}

// User avatar in main content
const userAvatar = document.querySelector('.user-avatar');
if (userAvatar) {
    userAvatar.addEventListener('click', () => {
        alert('User avatar clicked!');
    });
}

// AI Assistant section
const aiSection = document.querySelector('.ai-section');
if (aiSection) {
    aiSection.addEventListener('click', () => {
        alert('AI Assistant section clicked!');
    });
}

// Stat cards
document.querySelectorAll('.stat-card').forEach(card => {
    card.addEventListener('click', function () {
        const title = this.querySelector('.stat-title')?.textContent || 'Stat Card';
        alert(`${title} card clicked!`);
    });
});

// Activity section
const activitySection = document.querySelector('.activity-section');
if (activitySection) {
    activitySection.addEventListener('click', () => {
        alert('Activity section clicked!');
    });
}

// Latest Budgets section
const latestBudgets = document.querySelector('.latest-budgets');
if (latestBudgets) {
    latestBudgets.addEventListener('click', () => {
        alert('Latest Budgets section clicked!');
    });
}