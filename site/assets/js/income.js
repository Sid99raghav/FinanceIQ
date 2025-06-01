import { getIncomes, saveIncome, deleteIncome, updateIncome } from '/site/assets/js/backend.js';

const email = localStorage.getItem("user_email");

async function refreshIncomeList() {
    const incomes = await getIncomes(email);
    const table = document.getElementById("income-table-body");
    table.innerHTML = "";
    incomes.forEach(income => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${income.name}</td>
            <td>${income.amount}</td>
            <td>
                <button type="button" onclick="editIncome('${income.name}', ${income.amount})">Edit</button>
                <button type="button" onclick="removeIncome('${income.name}')">Delete</button>
            </td>
        `;
        table.appendChild(row);
    });
}

window.addIncome = async function() {
    const name = document.getElementById("income-name").value;
    const amount = parseFloat(document.getElementById("income-amount").value);
    await saveIncome({ email, source: name, amount });
    document.getElementById("income-form").reset();
    await refreshIncomeList();
};

window.removeIncome = async function(name) {
    await deleteIncome(email, name);
    await refreshIncomeList();
};

window.editIncome = function(name, amount) {
    document.getElementById("income-name").value = name;
    document.getElementById("income-amount").value = amount;
    document.getElementById("income-editing").value = name;
    document.getElementById("income-save-btn").textContent = "Update Income";
    document.getElementById("income-cancel-btn").style.display = "";
};

window.cancelEditIncome = function() {
    document.getElementById("income-form").reset();
    document.getElementById("income-editing").value = "";
    document.getElementById("income-save-btn").textContent = "Add Income";
    document.getElementById("income-cancel-btn").style.display = "none";
};

document.getElementById("income-form").onsubmit = async function(e) {
    e.preventDefault();
    const editing = document.getElementById("income-editing").value;
    const name = document.getElementById("income-name").value;
    const amount = parseFloat(document.getElementById("income-amount").value);
    if (editing) {
        await updateIncome(email, editing, name, amount);
        window.cancelEditIncome();
    } else {
        await saveIncome({ email, source: name, amount });
    }
    await refreshIncomeList();
};

document.getElementById("income-cancel-btn").onclick = window.cancelEditIncome;

window.editIncome = window.editIncome;
window.removeIncome = window.removeIncome;

window.onload = refreshIncomeList;