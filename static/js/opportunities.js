// Opportunities Page JavaScript

const API_BASE = '/api';

function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

async function loadAllOpportunities() {
    try {
        const response = await fetch(`${API_BASE}/opportunities?limit=100`);
        const data = await response.json();

        const tbody = document.getElementById('opps-table');
        tbody.innerHTML = '';

        if (data.opportunities.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted py-3">No opportunities found</td></tr>';
            return;
        }

        data.opportunities.forEach(opp => {
            const statusClass = opp.is_executed ? 'badge-secondary' : 'badge-warning';
            const statusText = opp.is_executed ? 'Executed' : 'Active';
            const profitClass = opp.profit_percent >= 2 ? 'text-success' : 'text-warning';

            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${opp.trading_pair}</strong></td>
                <td>${opp.buy_exchange}</td>
                <td>$${opp.buy_price.toFixed(4)}</td>
                <td>${opp.sell_exchange}</td>
                <td>$${opp.sell_price.toFixed(4)}</td>
                <td>${opp.price_difference_percent.toFixed(2)}%</td>
                <td><span class="${profitClass}">${opp.profit_percent.toFixed(2)}%</span></td>
                <td><span class="badge ${statusClass}">${statusText}</span></td>
                <td>
                    <button class="btn btn-sm btn-success" onclick="executeOpportunity(${opp.id})">
                        Execute
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading opportunities:', error);
    }
}

async function executeOpportunity(opportunityId) {
    if (!confirm('Execute this trade?')) return;

    try {
        const response = await fetch(`${API_BASE}/trades/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ opportunity_id: opportunityId })
        });

        const data = await response.json();

        if (data.success) {
            alert(`Trade executed!\nProfit: $${data.profit_loss.toFixed(2)} (${data.profit_loss_percent.toFixed(2)}%)`);
            loadAllOpportunities();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error executing trade');
    }
}

async function scanNow() {
    const btn = document.getElementById('scan-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Scanning...';
    btn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/opportunities/scan`, {
            method: 'POST'
        });

        const data = await response.json();
        alert(`Found ${data.detected} opportunities!`);
        loadAllOpportunities();
    } catch (error) {
        alert('Error scanning');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadAllOpportunities();

    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadAllOpportunities);
    }

    const scanBtn = document.getElementById('scan-btn');
    if (scanBtn) {
        scanBtn.addEventListener('click', scanNow);
    }

    // Auto-refresh every 30 seconds
    setInterval(loadAllOpportunities, 30000);
});
