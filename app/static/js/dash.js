document.addEventListener('DOMContentLoaded', function() {
    function loadEvents() {
        return fetch('/api/events')
            .then(response => response.json())
            .catch(error => {
                console.error('Error fetching events:', error);
                return [];
            });
    }

    function loadQuote() {
        return fetch('https://api.quotable.io/random')
            .then(response => response.json())
            .then(data => {
                document.getElementById('quote').textContent = data.content + " — " + data.author;
            })
            .catch(error => {
                console.error('Error fetching quote:', error);
                document.getElementById('quote').textContent = "Failed to load quote.";
            });
    }

    function renderCalendar(events) {
        const calendarEl = document.getElementById('calendar');
        const calendar = new FullCalendar.Calendar(calendarEl, {
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay'
            },
            editable: true,
            events: events,
            dateClick: function(info) {
                var title = prompt('Event Title:');
                if (title) {
                    var eventData = {
                        title: title,
                        start: info.dateStr,
                        allDay: true
                    };
                    calendar.addEvent(eventData);

                    fetch('/api/events', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(eventData)
                    })
                    .then(response => response.json())
                    .catch(error => {
                        console.error('Error saving event:', error);
                    });
                }
            },
            eventClick: function(info) {
                if (confirm("Do you want to delete this event?")) {
                    fetch(`/api/events/${info.event.id}`, {
                        method: 'DELETE',
                        headers: { 'Content-Type': 'application/json' }
                    })
                    .then(response => response.json())
                    .then(() => {
                        info.event.remove();
                    })
                    .catch(error => {
                        console.error('Error deleting event:', error);
                    });
                }
            }
        });
        calendar.render();
    }

    function updateFinancialData(type, amount) {
        const data = { type, amount };

        return fetch('/api/financial', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .catch(error => console.error('Error updating financial data:', error));
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

    function renderFinancialData(data) {
        try {
            // Check if data contains the expected properties
            if (!data) {
                throw new Error('Incomplete financial data received');
            }
    
            document.getElementById('earnings').textContent = `$${data.earnings}`;
            document.getElementById('expenses').textContent = `$${data.expenses}`;
            document.getElementById('savings').textContent = `$${data.savings}`;
            document.getElementById('budgetGoals').textContent = `$${data.budgetGoals}`;
    
            // Display target values and compare them with actual values
            const earningsElement = document.getElementById('earnings');
            const expensesElement = document.getElementById('expenses');
            const savingsElement = document.getElementById('savings');
            const budgetGoalsElement = document.getElementById('budgetGoals');
    
            const earningsTarget = data.earningsTarget || 0;
            const expensesTarget = data.expensesTarget || 0;
            const savingsTarget = data.savingsTarget || 0;
            const budgetGoalsTarget = data.budgetGoalsTarget || 0;
    
            // Add target values to the display
            document.getElementById('earnings-target').textContent = `$${earningsTarget}`;
            document.getElementById('expenses-target').textContent = `$${expensesTarget}`;
            document.getElementById('savings-target').textContent = `$${savingsTarget}`;
            document.getElementById('budgetGoals-target').textContent = `$${budgetGoalsTarget}`;
    
            // Compare actual values with targets
            if (data.earnings < earningsTarget) {
                earningsElement.style.color = 'red';
            } else {
                earningsElement.style.color = 'green';
            }
    
            if (data.expenses > expensesTarget) {
                expensesElement.style.color = 'red';
            } else {
                expensesElement.style.color = 'green';
            }
    
            if (data.savings < savingsTarget) {
                savingsElement.style.color = 'red';
            } else {
                savingsElement.style.color = 'green';
            }
    
            if (data.budgetGoals < budgetGoalsTarget) {
                budgetGoalsElement.style.color = 'red';
            } else {
                budgetGoalsElement.style.color = 'green';
            }
    
        } catch (error) {
            console.error('Error rendering financial data:', error);
            throw error; // Rethrow the error to propagate it down the promise chain
        }
    }
    

    function renderFinancialChart(data) {
        try {
            console.log('Data received in renderFinancialChart:', data);

            if (!data) {
                throw new Error('No financial data received for chart rendering');
            }

            const ctx = document.getElementById('financialChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Earnings', 'Expenses', 'Savings', 'Budget Goals'],
                    datasets: [{
                        label: 'Financial Overview',
                        data: [data.earnings, data.expenses, data.savings, data.budgetGoals],
                        backgroundColor: [
                            'rgba(75, 192, 192, 0.2)',
                            'rgba(255, 99, 132, 0.2)',
                            'rgba(54, 162, 235, 0.2)',
                            'rgba(255, 206, 86, 0.2)'
                        ],
                        borderColor: [
                            'rgba(75, 192, 192, 1)',
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error rendering financial chart:', error);
        }
    }

    document.getElementById('earningsForm').addEventListener('submit', function(event) {
        event.preventDefault();
        const amount = parseFloat(document.getElementById('earningsAmount').value);
        const target = parseFloat(document.getElementById('earningsTargetAmount').value);
        updateFinancialData('earnings', amount, target).then(fetchFinancialData).then(renderFinancialData).then(renderFinancialChart);
    });
    
    document.getElementById('expensesForm').addEventListener('submit', function(event) {
        event.preventDefault();
        const amount = parseFloat(document.getElementById('expensesAmount').value);
        const target = parseFloat(document.getElementById('expensesTargetAmount').value);
        updateFinancialData('expenses', amount, target).then(fetchFinancialData).then(renderFinancialData).then(renderFinancialChart);
    });
    
    document.getElementById('savingsForm').addEventListener('submit', function(event) {
        event.preventDefault();
        const amount = parseFloat(document.getElementById('savingsAmount').value);
        const target = parseFloat(document.getElementById('savingsTargetAmount').value);
        updateFinancialData('savings', amount, target).then(fetchFinancialData).then(renderFinancialData).then(renderFinancialChart);
    });
    
    document.getElementById('budgetForm').addEventListener('submit', function(event) {
        event.preventDefault();
        const amount = parseFloat(document.getElementById('budgetAmount').value);
        const target = parseFloat(document.getElementById('budgetTargetAmount').value);
        updateFinancialData('budgetGoals', amount, target).then(fetchFinancialData).then(renderFinancialData).then(renderFinancialChart);
    });
    
    function updateFinancialData(type, amount, target) {
        const data = { type, amount, target };
    
        return fetch('/api/financial', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .catch(error => console.error('Error updating financial data:', error));
    }
    

    loadEvents().then(renderCalendar);
    loadQuote();

    fetchFinancialData()
        .then(data => {
            renderFinancialData(data);
            renderFinancialChart(data);
        })
        .catch(error => console.error('Error rendering financial chart:', error));
});
