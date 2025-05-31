const form = document.getElementById('income-form');
const list = document.getElementById('income-list');

async function refreshIncomeList() {
    // Get user email from backend, fallback to sid@gmail.com
    let email = "sid@gmail.com";
    try {
        const res = await fetch('/api/auth/me', {credentials: "include"});
        if (res.ok) {
            const user = await res.json();
            if (user.email) email = user.email;
        }
    } catch {}
    // Fetch incomes from backend
    const resp = await fetch(`/api/incomes?email=${encodeURIComponent(email)}`, {credentials: "include"});
    if (!resp.ok) {
        list.innerHTML = "<em>Could not load incomes.</em>";
        return;
    }
    const incomes = await resp.json();
    if (!incomes.length) {
        list.innerHTML = "<em>No incomes added yet.</em>";
        return;
    }
    list.innerHTML = "<ul>" + incomes.map(i => `<li><b>${i.source}</b>: $${i.amount.toLocaleString()}</li>`).join("") + "</ul>";
}

form.onsubmit = async function(e) {
    e.preventDefault();
    const source = form.source.value.trim();
    const amount = parseFloat(form.amount.value);
    if (!source || isNaN(amount)) {
        alert("Please enter valid income source and amount.");
        return;
    }
    // Get user email from backend, fallback to sid@gmail.com
    let email = "sid@gmail.com";
    try {
        const res = await fetch('/api/auth/me', {credentials: "include"});
        if (res.ok) {
            const user = await res.json();
            if (user.email) email = user.email;
        }
    } catch {}
    // Save to backend
    const resp = await fetch("/api/incomes", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        credentials: "include",
        body: JSON.stringify({ email, source, amount })
    });
    if (resp.ok) {
        form.reset();
        await refreshIncomeList();
    } else {
        alert("Failed to save income.");
    }
};

refreshIncomeList();