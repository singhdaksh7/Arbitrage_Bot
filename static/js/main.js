// Main Dashboard JavaScript

const API_BASE = '/api';

// Update interval (seconds)
const UPDATE_INTERVAL = 30;

// Format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

// Format percentage
function formatPercent(value) {
    const sign = value >= 0 ? '+' : '';
    const className = value >= 0 ? 'text-success' : 'text-danger';
    return `<span class="${className}">${sign}${value.toFixed(2)}%</span>`;
}

// Update dashboard stats
async function updateDashboard() {
    try {
        const response = await fetch(`${API_BASE}/wallet`);
        const data = await response.json();
        const wallet = data.wallet;

        document.getElementById('wallet-balance').textContent = formatCurrency(wallet.usd_balance).replace('$', '');
        document.getElementById('total-pnl').textContent = formatCurrency(wallet.total_profit_loss);
        document.getElementById('total-pnl').className = wallet.total_profit_loss >= 0 ? 'text-success' : 'text-danger';
        document.getElementById('total-pnl-percent').textContent = wallet.roi_percent.toFixed(2) + '%';
        document.getElementById('total-pnl-percent').className = wallet.roi_percent >= 0 ? 'text-success' : 'text-danger';

        // Update timestamp
        const now = new Date();
        document.getElementById('last-update').textContent = now.toLocaleTimeString();
    } catch (error) {
        console.error('Error updating dashboard:', error);
    }
}

// Load opportunities
async function loadOpportunities() {
    try {
        const response = await fetch(`${API_BASE}/opportunities?limit=5&active_only=true`);
        const data = await response.json();

        document.getElementById('active-opportunities').textContent = data.count;

        const tbody = document.getElementById('opportunities-table-body');
        tbody.innerHTML = '';

        if (data.opportunities.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-3">No opportunities detected</td></tr>';
            return;
        }

        data.opportunities.forEach(opp => {
            const profitClass = opp.profit_percent >= 2 ? 'text-success' : 'text-warning';
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${opp.trading_pair}</strong></td>
                <td>${opp.buy_exchange}</td>
                <td>$${opp.buy_price.toFixed(2)}</td>
                <td>${opp.sell_exchange}</td>
                <td>$${opp.sell_price.toFixed(2)}</td>
                <td><span class="${profitClass}">${opp.profit_percent.toFixed(2)}%</span></td>
                <td>
                    <button class="btn btn-sm btn-success" onclick="executeOpportunity(${opp.id})">
                        <i class="bi bi-play-fill"></i> Execute
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading opportunities:', error);
    }
}

// Load trades
async function loadTrades() {
    try {
        const response = await fetch(`${API_BASE}/trades?limit=10`);
        const data = await response.json();

        document.getElementById('total-trades').textContent = data.count;

        const tbody = document.getElementById('trades-table-body');
        tbody.innerHTML = '';

        if (data.trades.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-3">No trades yet</td></tr>';
            return;
        }

        data.trades.forEach(trade => {
            const date = new Date(trade.created_at);
            const typeClass = trade.type === 'BUY' ? 'badge-info' : 'badge-success';
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${date.toLocaleString()}</td>
                <td><span class="badge ${typeClass}">${trade.type}</span></td>
                <td>${trade.trading_pair}</td>
                <td>${trade.exchange}</td>
                <td>${trade.quantity.toFixed(4)}</td>
                <td>$${trade.price.toFixed(2)}</td>
                <td>$${trade.total_cost.toFixed(2)}</td>
                <td>$${trade.fee.toFixed(4)}</td>
                <td>${trade.profit_loss_percent ? formatPercent(trade.profit_loss_percent) : '--'}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading trades:', error);
    }
}

// Execute opportunity
async function executeOpportunity(opportunityId) {
    if (!confirm('Execute this trade? (This is a simulated trade)')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/trades/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ opportunity_id: opportunityId })
        });

        const data = await response.json();

        if (data.success) {
            alert(`Trade executed!\nProfit: $${data.profit_loss.toFixed(2)} (${data.profit_loss_percent.toFixed(2)}%)`);
            updateDashboard();
            loadOpportunities();
            loadTrades();
        } else {
            alert('Error executing trade: ' + data.error);
        }
    } catch (error) {
        console.error('Error executing trade:', error);
        alert('Error executing trade');
    }
}

// Scan for opportunities
async function scanOpportunities() {
    const btn = document.getElementById('scan-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-mini"></span> Scanning...';
    btn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/opportunities/scan`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            alert(`Found ${data.detected} opportunities!\nSaved: ${data.saved}`);
            updateDashboard();
            loadOpportunities();
        } else {
            alert('Error scanning opportunities: ' + data.error);
        }
    } catch (error) {
        console.error('Error scanning:', error);
        alert('Error scanning for opportunities');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    updateDashboard();
    loadOpportunities();
    loadTrades();

    // Add scan button listener
    const scanBtn = document.getElementById('scan-btn');
    if (scanBtn) {
        scanBtn.addEventListener('click', scanOpportunities);
    }

    // Auto-refresh
    setInterval(() => {
        updateDashboard();
        loadOpportunities();
        loadTrades();
    }, UPDATE_INTERVAL * 1000);
});
