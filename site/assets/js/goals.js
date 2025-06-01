import { getGoals, saveGoal, deleteGoal, updateGoal } from '/site/assets/js/backend.js';

const email = localStorage.getItem("user_email");

async function refreshGoalList() {
    const goals = await getGoals(email);
    const table = document.getElementById("goal-table-body");
    table.innerHTML = "";
    goals.forEach(goal => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${goal.name}</td>
            <td>${goal.amount}</td>
            <td>${goal.years}</td>
            <td>
                <button type="button" onclick="editGoal('${goal.name}', ${goal.amount}, ${goal.years})">Edit</button>
                <button type="button" onclick="removeGoal('${goal.name}')">Delete</button>
            </td>
        `;
        table.appendChild(row);
    });
}

window.addGoal = async function() {
    const name = document.getElementById("goal-name").value;
    const amount = parseFloat(document.getElementById("goal-amount").value);
    const years = parseInt(document.getElementById("goal-years").value);
    await saveGoal({ email, name, amount, years });
    document.getElementById("goal-form").reset();
    await refreshGoalList();
};

window.removeGoal = async function(name) {
    await deleteGoal(email, name);
    await refreshGoalList();
};

window.editGoal = function(name, amount, years) {
    document.getElementById("goal-name").value = name;
    document.getElementById("goal-amount").value = amount;
    document.getElementById("goal-years").value = years;
    document.getElementById("goal-editing").value = name;
    document.getElementById("goal-save-btn").textContent = "Update Goal";
    document.getElementById("goal-cancel-btn").style.display = "";
};

window.cancelEditGoal = function() {
    document.getElementById("goal-form").reset();
    document.getElementById("goal-editing").value = "";
    document.getElementById("goal-save-btn").textContent = "Add Goal";
    document.getElementById("goal-cancel-btn").style.display = "none";
};

document.getElementById("goal-form").onsubmit = async function(e) {
    e.preventDefault();
    const editing = document.getElementById("goal-editing").value;
    const name = document.getElementById("goal-name").value;
    const amount = parseFloat(document.getElementById("goal-amount").value);
    const years = parseInt(document.getElementById("goal-years").value);
    if (editing) {
        await updateGoal(email, editing, name, amount, years);
        window.cancelEditGoal();
    } else {
        await saveGoal({ email, name, amount, years });
    }
    await refreshGoalList();
};

document.getElementById("goal-cancel-btn").onclick = window.cancelEditGoal;

window.editGoal = window.editGoal;
window.removeGoal = window.removeGoal;

window.onload = refreshGoalList;
