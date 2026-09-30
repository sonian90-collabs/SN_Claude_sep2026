// Grab the page elements we need to work with.
const rowsBody = document.getElementById("rows");
const startInput = document.getElementById("start-balance");
const startCell = document.getElementById("start-balance-cell");
const addButton = document.getElementById("add-row");
const totalSpentEl = document.getElementById("total-spent");
const remainingEl = document.getElementById("remaining");

// Where the browser remembers your data between visits.
const STORAGE_KEY = "expense-tracker";

// Add one expense row (row 2, 3, 4...) to the table.
function addExpenseRow(amount = "", name = "") {
  const tr = document.createElement("tr");
  tr.className = "expense-row";
  tr.innerHTML = `
    <td class="row-num"></td>
    <td><input class="amount" type="number" min="0" step="0.01" placeholder="0.00"></td>
    <td><input class="name" type="text" placeholder="e.g. Groceries"></td>
    <td class="money balance"></td>
    <td><button class="delete" title="Delete row">x</button></td>
  `;
  tr.querySelector(".amount").value = amount;
  tr.querySelector(".name").value = name;

  // Remove this row when its delete button is clicked.
  tr.querySelector(".delete").addEventListener("click", () => {
    tr.remove();
    update();
  });

  rowsBody.appendChild(tr);
  return tr;
}

// Recalculate every balance, then save.
function update() {
  let balance = Number(startInput.value) || 0;
  let totalSpent = 0;
  startCell.textContent = balance.toFixed(2);

  const expenseRows = rowsBody.querySelectorAll(".expense-row");
  expenseRows.forEach((tr, index) => {
    const amount = Number(tr.querySelector(".amount").value) || 0;
    balance -= amount;
    totalSpent += amount;

    tr.querySelector(".row-num").textContent = index + 2;
    const balanceCell = tr.querySelector(".balance");
    balanceCell.textContent = balance.toFixed(2);
    balanceCell.classList.toggle("negative", balance < 0);
  });

  totalSpentEl.textContent = totalSpent.toFixed(2);
  remainingEl.textContent = balance.toFixed(2);
  remainingEl.classList.toggle("negative", balance < 0);

  save();
}

// Save the starting balance and all expenses in the browser.
function save() {
  const expenses = [...rowsBody.querySelectorAll(".expense-row")].map((tr) => ({
    amount: tr.querySelector(".amount").value,
    name: tr.querySelector(".name").value,
  }));
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ start: startInput.value, expenses }));
  } catch (e) {
    // Storage can be blocked (e.g. private browsing); the page still works.
  }
}

// Load saved data, or start with one empty expense row.
function load() {
  let data = null;
  try {
    data = JSON.parse(localStorage.getItem(STORAGE_KEY));
  } catch (e) {
    data = null;
  }

  if (data) {
    startInput.value = data.start;
    data.expenses.forEach((exp) => addExpenseRow(exp.amount, exp.name));
  }
  if (rowsBody.querySelectorAll(".expense-row").length === 0) {
    addExpenseRow();
  }
  update();
}

// Any typing in the table recalculates the balances.
rowsBody.addEventListener("input", update);

addButton.addEventListener("click", () => {
  const tr = addExpenseRow();
  tr.querySelector(".amount").focus();
  update();
});

load();
