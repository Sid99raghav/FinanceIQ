document.getElementById('sidebar').innerHTML = `
<aside class="sidebar">
    <div class="logo-section">
        <div class="logo">💹</div>
        <span class="logo-text">FinanceIQ</span>
    </div>
    <nav>
        <ul class="nav-menu">
            <li class="nav-item"><a href="/site/index.html" class="nav-link"><div class="nav-icon">🏠</div>Dashboard</a></li>
            <li class="nav-item"><a href="/site/income.html" class="nav-link"><div class="nav-icon">🪙</div>Incomes</a></li>
            <li class="nav-item"><a href="/site/assets.html" class="nav-link"><div class="nav-icon">💹</div>Assets</a></li>
            <li class="nav-item"><a href="/site/expenses.html" class="nav-link"><div class="nav-icon">💸</div>Expenses</a></li>
            <li class="nav-item"><a href="/site/goals.html" class="nav-link"><div class="nav-icon">📈</div>Goals</a></li>
        </ul>
    </nav>
   
</aside>
`;

// Highlight the active link based on current page
const links = document.querySelectorAll('.nav-link');
links.forEach(link => {
    if (window.location.pathname.endsWith(link.getAttribute('href'))) {
        link.classList.add('active');
    } else {
        link.classList.remove('active');
    }
});
