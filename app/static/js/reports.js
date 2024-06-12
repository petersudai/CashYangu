document.addEventListener('DOMContentLoaded', function() {
    const reportsContainer = document.getElementById('reports-container');

    reportsContainer.addEventListener('click', function(event) {
        if (event.target.classList.contains('delete-button')) {
            const row = event.target.closest('tr');
            const id = row.getAttribute('data-id');

            if (confirm('Are you sure you want to delete this transaction?')) {
                fetch(`/api/financial/${id}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message === 'Financial data deleted successfully') {
                        row.remove();
                        fetchFinancialData().then(data => {
                            renderFinancialData(data);
                            renderFinancialChart(data);
                            renderExpenseCategoryChart(data);
                        });
                    } else {
                        alert('Failed to delete transaction');
                    }
                })
                .catch(error => console.error('Error deleting transaction:', error));
            }
        }
    });

    document.getElementById('downloadReportBtn').addEventListener('click', function() {
        fetch('/api/financial_report')
            .then(response => response.json())
            .then(data => {
                const csvContent = generateCSV(data);
                downloadCSV(csvContent, 'financial_report.csv');
            })
            .catch(error => console.error('Error fetching financial data:', error));
    });

    document.getElementById('deleteAllBtn').addEventListener('click', function() {
        if (confirm('Are you sure you want to delete all transactions? This action cannot be undone.')) {
            fetch('/api/financial/all', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.message === 'All financial data deleted successfully') {
                    const rows = document.querySelectorAll('#reports-container tr');
                    rows.forEach(row => row.remove());
                    fetchFinancialData().then(data => {
                        renderFinancialData(data);
                        renderFinancialChart(data);
                        renderExpenseCategoryChart(data);
                    });
                } else {
                    alert('Failed to delete all transactions');
                }
            })
            .catch(error => console.error('Error deleting all transactions:', error));
        }
    });

    function generateCSV(data) {
        const header = ["Date", "Type", "Amount", "Category"];
        const rows = data.map(item => [
            item.date,
            item.type,
            item.amount,
            item.category || ''
        ]);

        const csvContent = [header, ...rows].map(e => e.join(",")).join("\n");
        return csvContent;
    }

    function downloadCSV(csvContent, fileName) {
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', fileName);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }

    function fetchFinancialData() {
        return fetch('/api/financial')
            .then(response => response.json())
            .then(data => {
                console.log('Fetched financial data:', data);
                return data;
            })
            .catch(error => {
                console.error('Error fetching financial data:', error);
                throw error;
            });
    }
});
