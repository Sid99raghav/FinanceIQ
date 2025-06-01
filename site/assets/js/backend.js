function getServerUri() {
    // Get current base url
    var server_uri = window.location.origin;
    console.log(server_uri);
    
    return server_uri;
}

export async function fetchProfile() {
    try {
        const response = await fetch("/profile");
        if (response.ok) {
            return await response.json();
        } else {
            console.error("Failed to fetch profile:", response.statusText);
            return null;
        }
    } catch (error) {
        console.error("Error fetching profile:", error);
        return null;
    }
}

export async function saveProfile(profileData) {
    try {
        const response = await fetch("/profile", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(profileData),
        });

        if (response.ok) {
            return true;
        } else {
            console.error("Failed to save profile:", response.statusText);
            return false;
        }
    } catch (error) {
        console.error("Error saving profile:", error);
        return false;
    }
}

// Utility: Get email from SSO/session, or trigger SSO login if not authenticated
export async function getUserEmailOrLogin() {
    // Try to get session info
    const sessionRes = await fetch("/session", { credentials: "include" });
    if (sessionRes.ok) {
        const sessionData = await sessionRes.json();
        if (sessionData.authenticated && sessionData.user && sessionData.user.email) {
            // Store for later use
            localStorage.setItem("user_email", sessionData.user.email);
            return sessionData.user.email;
        }
    }
    // Not authenticated, redirect to SSO login
    window.location.href = "/google/login";
    return null;
}

// ASSET APIs
export async function saveAsset(data) {
    let email = data.email || localStorage.getItem("user_email");
    if (!email) email = await getUserEmailOrLogin();
    if (!email) return;
    const res = await fetch(getServerUri() + "/api/assets", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...data, email })
    });
    return await res.json();
}

export async function getAssets(email) {
    email = email || localStorage.getItem("user_email");
    if (!email) email = await getUserEmailOrLogin();
    if (!email) return [];
    const res = await fetch(getServerUri() + `/api/assets?email=${encodeURIComponent(email)}`);
    return await res.json();
}

export async function deleteAsset(email, name) {
    email = email || localStorage.getItem("user_email");
    if (!email) email = await getUserEmailOrLogin();
    if (!email) return;
    const res = await fetch(getServerUri() + "/api/assets/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, name })
    });
    return await res.json();
}

export async function updateAsset(email, oldName, newName, amount) {
    email = email || localStorage.getItem("user_email");
    if (!email) email = await getUserEmailOrLogin();
    if (!email) return;
    const res = await fetch(getServerUri() + "/api/assets/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, oldName, newName, amount })
    });
    return await res.json();
}

// INCOME APIs
export async function saveIncome(data) {
    let email = data.email || localStorage.getItem("user_email");
    if (!email) email = await getUserEmailOrLogin();
    if (!email) return;
    const res = await fetch(getServerUri() + "/api/incomes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...data, email })
    });
    return await res.json();
}

export async function getIncomes(email) {
    email = email || localStorage.getItem("user_email");
    if (!email) email = await getUserEmailOrLogin();
    if (!email) return [];
    const res = await fetch(getServerUri() + `/api/incomes?email=${encodeURIComponent(email)}`);
    return await res.json();
}

export async function deleteIncome(email, name) {
    email = email || localStorage.getItem("user_email");
    if (!email) email = await getUserEmailOrLogin();
    if (!email) return;
    const res = await fetch(getServerUri() + "/api/incomes/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, name })
    });
    return await res.json();
}

export async function updateIncome(email, oldName, newName, amount) {
    email = email || localStorage.getItem("user_email");
    if (!email) email = await getUserEmailOrLogin();
    if (!email) return;
    const res = await fetch(getServerUri() + "/api/incomes/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, oldName, newName, amount })
    });
    return await res.json();
}

// EXPENSE APIs
export async function saveExpense(data) {
    let email = data.email || localStorage.getItem("user_email");
    if (!email) email = await getUserEmailOrLogin();
    if (!email) return;
    const res = await fetch(getServerUri() + "/api/expenses", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...data, email })
    });
    return await res.json();
}

export async function getExpenses(email) {
    email = email || localStorage.getItem("user_email");
    if (!email) email = await getUserEmailOrLogin();
    if (!email) return [];
    const res = await fetch(getServerUri() + `/api/expenses?email=${encodeURIComponent(email)}`);
    return await res.json();
}

export async function deleteExpense(email, name) {
    email = email || localStorage.getItem("user_email");
    if (!email) email = await getUserEmailOrLogin();
    if (!email) return;
    const res = await fetch(getServerUri() + "/api/expenses/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, name })
    });
    return await res.json();
}

export async function updateExpense(email, oldName, newName, amount) {
    email = email || localStorage.getItem("user_email");
    if (!email) email = await getUserEmailOrLogin();
    if (!email) return;
    const res = await fetch(getServerUri() + "/api/expenses/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, oldName, newName, amount })
    });
    return await res.json();
}

// GOAL APIs
export async function saveGoal(data) {
    let email = data.email || localStorage.getItem("user_email");
    if (!email) email = await getUserEmailOrLogin();
    if (!email) return;
    const res = await fetch(getServerUri() + "/api/goals", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...data, email })
    });
    return await res.json();
}

export async function getGoals(email) {
    email = email || localStorage.getItem("user_email");
    if (!email) email = await getUserEmailOrLogin();
    if (!email) return [];
    const res = await fetch(getServerUri() + `/api/goals?email=${encodeURIComponent(email)}`);
    return await res.json();
}

export async function deleteGoal(email, name) {
    email = email || localStorage.getItem("user_email");
    if (!email) email = await getUserEmailOrLogin();
    if (!email) return;
    const res = await fetch(getServerUri() + "/api/goals/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, name })
    });
    return await res.json();
}

export async function updateGoal(email, oldName, newName, amount, years) {
    email = email || localStorage.getItem("user_email");
    if (!email) email = await getUserEmailOrLogin();
    if (!email) return;
    const res = await fetch(getServerUri() + "/api/goals/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, oldName, newName, amount, years })
    });
    return await res.json();
}

// PLAN APIs
export async function saveFinancialPlan(data) {
    let email = data.email || localStorage.getItem("user_email");
    if (!email) email = await getUserEmailOrLogin();
    if (!email) return;
    const res = await fetch(getServerUri() + "/api/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...data, email })
    });
    return await res.json();
}

export async function getFinancialPlan(email) {
    email = email || localStorage.getItem("user_email");
    if (!email) email = await getUserEmailOrLogin();
    if (!email) return {};
    const res = await fetch(getServerUri() + `/api/plan?email=${encodeURIComponent(email)}`);
    return await res.json();
}

export async function generateFinancialPlan(email) {
    email = email || localStorage.getItem("user_email");
    if (!email) email = await getUserEmailOrLogin();
    if (!email) return {};
    const res = await fetch(getServerUri() + "/api/plan/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email })
    });
    return await res.json();
}

export async function viewFinancialPlan(email) {
    email = email || localStorage.getItem("user_email");
    if (!email) email = await getUserEmailOrLogin();
    if (!email) return {};
    const res = await fetch(getServerUri() + "/api/plan/view", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email })
    });
    return await res.json();
}
