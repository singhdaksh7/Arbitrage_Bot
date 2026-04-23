// Wallet Page JavaScript

const API_BASE = '/api';

function formatCurrency(value) {
    return value.toFixed(2);
}

async function loadWalletInfo() {
    try {
        const response = await fetch(`${API_BASE}/wallet`);
        const data = await response.json();
        const wallet = data.wallet;

        document.getElementById('usd-balance').textContent = formatCurrency(wallet.usd_balance);
        document.getElementById('total-value').textContent = formatCurrency(wallet.total_portfolio_value);
        document.getElementById('total-invested').textContent = formatCurrency(wallet.total_invested);
        document.getElementById('total-pnl').textContent = '$' + formatCurrency(wallet.total_profit_loss);
        document.getElementById('total-pnl').className = wallet.total_profit_loss >= 0 ? 'text-success' : 'text-danger';
        document.getElementById('roi-percent').textContent = wallet.roi_percent.toFixed(2) + '%';
        document.getElementById('roi-percent').className = wallet.roi_percent >= 0 ? 'text-success' : 'text-danger';
    } catch (error) {
        console.error('Error loading wallet:', error);
    }
}

async function resetWallet() {
    if (!confirm('Are you sure? This will reset all trades and the wallet.')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/wallet/reset`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            alert('Wallet reset successfully!');
            loadWalletInfo();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error resetting wallet');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadWalletInfo();

    const resetBtn = document.getElementById('reset-btn');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetWallet);
    }

    // Auto-refresh every 30 seconds
    setInterval(loadWalletInfo, 30000);
});
