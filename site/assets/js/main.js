import { getUserEmailOrLogin } from './backend.js';

// Redirect to login page if not authenticated
async function ensureAuthenticated() {
    try {
        const res = await fetch('/session', { credentials: "include" });
        if (res.ok) {
            const data = await res.json();
            if (!data.authenticated) {
                window.location.href = "/site/login.html";
            }
        } else {
            window.location.href = "/site/login.html";
        }
    } catch {
        window.location.href = "/site/login.html";
    }
}
await ensureAuthenticated();

// Profile section
const profileSection = document.querySelector('.profile-section');
if (profileSection) {
    profileSection.addEventListener('click', () => {
        alert('Profile section clicked!');
    });
}

// Avatar section logic
const userAvatar = document.querySelector('.user-avatar');
const userEmailSpan = document.getElementById('user-email');
const logoutBtn = document.getElementById('logout-btn');
const avatarDialog = document.getElementById('avatar-dialog');
const avatarDialogAvatar = document.getElementById('avatar-dialog-avatar');
const avatarDialogEmail = document.getElementById('avatar-dialog-email');
const avatarLogoutBtn = document.getElementById('avatar-logout-btn');

// Helper to set avatar image or initials
function setAvatar(el, user) {
    if (!el) return;
    if (user.picture) {
        el.innerHTML = `<img src="${user.picture}" alt="avatar" style="width:100%;height:100%;border-radius:50%;">`;
    } else if (user.email) {
        el.textContent = user.email[0].toUpperCase();
    } else {
        el.textContent = "👤";
    }
}

// Fetch user session once and update all avatar-related UI
let cachedUser = null;
function updateAvatarUI() {
    if (cachedUser) {
        setAvatar(userAvatar, cachedUser);
        setAvatar(avatarDialogAvatar, cachedUser);
        if (avatarDialogEmail) avatarDialogEmail.textContent = cachedUser.email || "";
        if (userEmailSpan) userEmailSpan.textContent = cachedUser.email || "";
        return;
    }
    fetch('/session', { credentials: "include" })
        .then(res => res.ok ? res.json() : {})
        .then(data => {
            if (data && data.user) {
                cachedUser = data.user;
                setAvatar(userAvatar, cachedUser);
                setAvatar(avatarDialogAvatar, cachedUser);
                if (avatarDialogEmail) avatarDialogEmail.textContent = cachedUser.email || "";
                if (userEmailSpan) userEmailSpan.textContent = cachedUser.email || "";
            }
        })
        .catch(console.error);
}
updateAvatarUI();

// Show/hide dialog on avatar click
if (userAvatar && avatarDialog) {
    userAvatar.addEventListener('click', (e) => {
        e.stopPropagation();
        updateAvatarUI();
        avatarDialog.style.display = avatarDialog.style.display === "none" ? "block" : "none";
    });
    document.addEventListener('click', (e) => {
        if (avatarDialog.style.display === "block" && !avatarDialog.contains(e.target) && e.target !== userAvatar) {
            avatarDialog.style.display = "none";
        }
    });
}

// Logout button
/*if (logoutBtn) {
    logoutBtn.onclick = () => {
        fetch('/google/logout', { credentials: "include" })
            .then(() => {
                window.location.href = "/site/login.html";
            })
            .catch(() => {
                window.location.href = "/site/login.html";
            });
    };
}*/

// Logout button in dialog
if (avatarLogoutBtn) {
    avatarLogoutBtn.onclick = () => {
        fetch('/google/logout', { credentials: "include" })
            .then(() => {
                window.location.href = "/site/login.html";
            })
            .catch(() => {
                window.location.href = "/site/login.html";
            });
    };
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