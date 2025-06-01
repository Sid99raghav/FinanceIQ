// SSO logic
let userEmail = null;

function updateUI() {
    document.getElementById('login-btn').style.display = userEmail ? 'none' : 'inline-block';
    document.getElementById('logout-btn').style.display = userEmail ? 'inline-block' : 'none';
    document.getElementById('user-email').textContent = userEmail ? userEmail : '';
}

// Remove any client-side Google sign-in logic and use server-side SSO endpoints

// Replace signInWithGoogle with a redirect to the backend SSO endpoint
function signInWithGoogle() {
    window.location.href = "/google/login";
}

// Update login/logout button handlers to use server-side SSO
const loginBtn = document.getElementById('login-btn');
if (loginBtn) {
    loginBtn.onclick = function() {
        signInWithGoogle();
    };
}
const logoutBtn = document.getElementById('logout-btn');
if (logoutBtn) {
    logoutBtn.onclick = function() {
        window.location.href = '/logout';
    };
}

// Update user email display after SSO
async function updateUserEmailUI() {
    try {
        const response = await fetch('/session');
        if (response.ok) {
            const data = await response.json();
            userEmail = data.user ? data.user.email : null;
        } else {
            userEmail = null;
        }
    } catch (e) {
        userEmail = null;
    }
    updateUI();
}

// Call on page load
updateUserEmailUI();

// Utility to get user email (returns promise)
async function getUserEmail() {
    try {
        const res = await fetch('/api/auth/me', {credentials: "include"});
        if (res.ok) {
            const data = await res.json();
            return data.email || "sid@gmail.com";
        }
    } catch (e) {}
    return "sid@gmail.com";
}

// Save asset/income/expense to backend
async function saveFinancialItem(type, item) {
    const email = await getUserEmail();
    if (!email) return;
    await fetch(`/api/${type}`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        credentials: "include",
        body: JSON.stringify({ email, ...item })
    });
}

// Load asset/income/expense list from backend
async function loadFinancialItems(type) {
    const email = await getUserEmail();
    if (!email) return [];
    const res = await fetch(`/api/${type}?email=${encodeURIComponent(email)}`, {
        credentials: "include"
    });
    if (res.ok) {
        return await res.json();
    }
    return [];
}

// Example usage:
// await saveFinancialItem('assets', { name: 'Bank', amount: 1000 });
// const assets = await loadFinancialItems('assets');

// Example: Save asset from UI form (call this on form submit)
async function saveAssetFromForm(name, amount) {
    const email = await getUserEmail();
    if (!email) {
        alert("User email not found.");
        return;
    }
    const resp = await fetch("/api/assets", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        credentials: "include",
        body: JSON.stringify({ email, name, amount })
    });
    if (resp.ok) {
        alert("Asset saved!");
    } else {
        alert("Failed to save asset.");
    }
}

// Save income to backend
async function saveIncomeToBackend(source, amount) {
    const email = await getUserEmail();
    if (!email) {
        alert("User email not found.");
        return false;
    }
    const resp = await fetch("/api/incomes", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        credentials: "include",
        body: JSON.stringify({ email, source, amount })
    });
    return resp.ok;
}

// Attach asset form handler if present
const assetForm = document.getElementById('assets-form');
if (assetForm) {
    assetForm.onsubmit = async function(e) {
        e.preventDefault();
        const name = assetForm.name.value.trim();
        const amount = parseFloat(assetForm.amount.value);
        if (!name || isNaN(amount)) {
            alert("Please enter valid asset name and amount.");
            return;
        }
        await saveAssetFromForm(name, amount);
        assetForm.reset();
    };
}

// Attach income form handler if present
const incomeForm = document.getElementById('income-form');
if (incomeForm) {
    incomeForm.onsubmit = async function(e) {
        e.preventDefault();
        const source = incomeForm.source.value.trim();
        const amount = parseFloat(incomeForm.amount.value);
        if (!source || isNaN(amount)) {
            alert("Please enter valid income source and amount.");
            return;
        }
        await saveIncomeToBackend(source, amount);
        incomeForm.reset();
    };
}

// Attach expenses form handler if present
const expensesForm = document.getElementById('expenses-form');
if (expensesForm) {
    expensesForm.onsubmit = async function(e) {
        e.preventDefault();
        const name = expensesForm.name.value.trim();
        const amount = parseFloat(expensesForm.amount.value);
        if (!name || isNaN(amount)) {
            alert("Please enter valid expense name and amount.");
            return;
        }
        const email = await getUserEmail();
        if (!email) {
            alert("User email not found.");
            return;
        }
        const resp = await fetch("/api/expenses", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            credentials: "include",
            body: JSON.stringify({ email, name, amount })
        });
        if (resp.ok) {
            alert("Expense saved!");
        } else {
            alert("Failed to save expense.");
        }
        expensesForm.reset();
    };
}

// Remove or comment out any <script> ... </script> tags if you copied this file from an HTML file.
// This file should only contain JavaScript code, not HTML tags.

//# sourceMappingURL=main.js.map

