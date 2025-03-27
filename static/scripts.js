// static/scripts.js
async function addTransaction(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const response = await fetch('/add', {
        method: 'POST',
        body: formData
    });
    if (response.ok) {
        updateBalanceAndCategories();
        event.target.reset();
    }
}

async function updateBalanceAndCategories() {
    const response = await fetch('/data');
    const data = await response.json();
    document.getElementById('balance').innerText = `Balance: ${data.balance.toFixed(2)} BDT`;
    const categoryList = document.getElementById('category-list');
    categoryList.innerHTML = '';
    data.categories.forEach(category => {
        const li = document.createElement('li');
        li.className = 'list-group-item';
        li.innerText = category;
        categoryList.appendChild(li);
    });
}

document.addEventListener('DOMContentLoaded', updateBalanceAndCategories);

