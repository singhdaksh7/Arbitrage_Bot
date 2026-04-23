// Trades Page JavaScript

const API_BASE = '/api';

async function loadAllTrades() {
    try {
        const response = await fetch(`${API_BASE}/trades?limit=200`);
        const data = await response.json();

        const tbody = document.getElementById('trades-table');
        tbody.innerHTML = '';

        if (data.trades.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted py-3">No trades yet</td></tr>';
            return;
        }

        data.trades.forEach(trade => {
            const date = new Date(trade.created_at);
            const typeClass = trade.type === 'BUY' ? 'bg-info' : 'bg-success';
            const pnlClass = trade.profit_loss_percent >= 0 ? 'text-success' : 'text-danger';

            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${date.toLocaleString()}</td>
                <td><span class="badge ${typeClass}">${trade.type}</span></td>
                <td>${trade.trading_pair}</td>
                <td>${trade.exchange}</td>
                <td>${trade.quantity.toFixed(6)}</td>
                <td>$${trade.price.toFixed(4)}</td>
                <td>$${trade.total_cost.toFixed(2)}</td>
                <td>$${trade.fee.toFixed(4)}</td>
                <td>
                    ${trade.profit_loss_percent !== 0 ? 
                        `<span class="${pnlClass}">${trade.profit_loss_percent.toFixed(2)}%</span>` : 
                        '--'}
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading trades:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadAllTrades();

    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadAllTrades);
    }

    // Auto-refresh every 30 seconds
    setInterval(loadAllTrades, 30000);
});
