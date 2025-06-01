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

// Stat cards
document.querySelectorAll('.stat-card').forEach(card => {
    card.addEventListener('click', function () {
        const title = this.querySelector('.stat-title')?.textContent || 'Stat Card';
        // Route to relevant page based on card title
        if (title.includes("Income")) {
            window.location.href = "/site/income.html";
        } else if (title.includes("Assets")) {
            window.location.href = "/site/assets.html";
        } else if (title.includes("Expenses")) {
            window.location.href = "/site/expenses.html";
        } else if (title.includes("Goals")) {
            window.location.href = "/site/goals.html";
        } else {
            // fallback: stay on dashboard
            window.location.href = "/site/index.html";
        }
    });
});

// Activity section
const activitySection = document.querySelector('.activity-section');
if (activitySection) {
    activitySection.addEventListener('click', () => {
        window.location.href = "/site/expenses.html";
    });
}

// Latest Budgets section
const latestBudgets = document.querySelector('.latest-budgets');
if (latestBudgets) {
    latestBudgets.addEventListener('click', () => {
        window.location.href = "/site/expenses.html";
    });
}