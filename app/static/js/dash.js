document.addEventListener('DOMContentLoaded', function() {
    function loadEvents() {
        return fetch('/api/events')
            .then(response => response.json())
            .catch(error => {
                console.error('Error fetching events:', error);
                return [];
            });
    }

    // function loadQuote() {
    //     return fetch('https://api.quotable.io/random')
    //         .then(response => response.json())
    //         .then(data => {
    //             document.getElementById('quote').textContent = data.content + " — " + data.author;
    //         })
    //         .catch(error => {
    //             console.error('Error fetching quote:', error);
    //             document.getElementById('quote').textContent = "Failed to load quote.";
    //         });
    // }

    function loadQuotesFromJSON() {
        return fetch('static/quotes.json')
            .then(response => response.json())
            .catch(error => {
                console.error('Error loading quotes:', error);
                return [];
            });
    }

    function loadQuote() {
        loadQuotesFromJSON()
            .then(quotes => {
                if (quotes.length > 0) {
                    const randomIndex = Math.floor(Math.random() * quotes.length);
                    const quote = quotes[randomIndex];
                    document.getElementById('quote').textContent = `${quote.content} — ${quote.author}`;
                } else {
                    document.getElementById('quote').textContent = "No quote found.";
                }
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
                    info.event.remove();

                    fetch(`/api/events/${info.event.id}`, {
                        method: 'DELETE',
                        headers: { 'Content-Type': 'application/json' }
                    })
                    .then(response => response.json())
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

    function updateSavingsData(amount) {
        const data = { type: 'savings', amount };

        return fetch('/api/financial', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .catch(error => console.error('Error updating savings data:', error));
    }


    function updateExpenseData(amount, category) {
        const data = { amount, category };

        return fetch('/api/expenses', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .catch(error => console.error('Error adding expense:', error));
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
            if (!data || data.earnings === undefined || data.expenses === undefined || data.savings === undefined || data.budgetGoals === undefined) {
                throw new Error('Incomplete financial data received');
            }
            document.getElementById('earnings').textContent = `KSH${data.earnings}`;
            document.getElementById('expenses').textContent = `KSH${data.expenses}`;
            document.getElementById('savings').textContent = `KSH${data.savings}`;
            document.getElementById('budgetGoals').textContent = `KSH${data.budgetGoals}`;
            document.getElementById('availableBalance').textContent = `KSH${data.availableBalance}`;
            
            if (data.expenses > data.budgetGoals) {
                document.getElementById('expenses').style.color = 'red';
            } else {
                document.getElementById('expenses').style.color = 'green';
            }
        } catch (error) {
            console.error('Error rendering financial data:', error);
            throw error;
        }
    }

    function renderFinancialChart(data) {
        console.log('Data received in renderFinancialChart:', data);
        if (!data) {
            throw new Error('No data received for financial chart');
        }
        const ctx = document.getElementById('financialChart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Expenses', 'Earnings'],
                datasets: [{
                    data: [data.expenses, data.earnings],
                    backgroundColor: [
                        '#F7DCA7',
                        '#427D9D'
                    ],
                    borderColor: [
                        '#F7DCA7',
                        '#427D9D'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            font: {
                                size: 14,
                                family: 'Montserrat',
                                weight: 'bold'
                            },
                            color: '#333'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Expenses vs Earnings',
                        font: {
                            size: 18,
                            family: 'Montserrat',
                            weight: 'bold'
                        },
                        color: '#333'
                    }
                }
            }
        });
    }

    function renderExpenseCategoryChart(data) {
        console.log('Data received in renderExpenseCategoryChart:', data);
        if (!data || !data.expenseCategories) {
            throw new Error('No data received for expense category chart');
        }
        const ctx = document.getElementById('expenseCategoryChart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(data.expenseCategories),
                datasets: [{
                    data: Object.values(data.expenseCategories),
                    backgroundColor: [
                        '#F7DCA7',
                        '#B4B8A5',
                        '#427D9D',
                        '#A1C398',
                        '#EEEEEE'
                    ],
                    borderColor: [
                        '#F7DCA7',
                        '#B4B8A5',
                        '#427D9D',
                        '#A1C398',
                        '#EEEEEE'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            font: {
                                size: 14,
                                family: 'Montserrat',
                                weight: 'bold'
                            },
                            color: '#333'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Expenses by Category',
                        font: {
                            size: 18,
                            family: 'Montserrat',
                            weight: 'bold'
                        },
                        color: '#333'
                    }
                }
            }
        });
    }

    document.getElementById('earningsForm').addEventListener('submit', function(event) {
        event.preventDefault();
        const amount = parseFloat(document.getElementById('earningsAmount').value) || 0;
        updateFinancialData('earnings', amount)
            .then(fetchFinancialData)
            .then(data => {
                renderFinancialData(data);
                renderFinancialChart(data);
                renderExpenseCategoryChart(data);
            });
    });

    document.getElementById('expensesForm').addEventListener('submit', function(event) {
        event.preventDefault();
        const amount = parseFloat(document.getElementById('expensesAmount').value) || 0;
        const category = document.getElementById('expensesCategory').value;
        updateExpenseData(amount, category)
            .then(fetchFinancialData)
            .then(data => {
                renderFinancialData(data);
                renderFinancialChart(data);
                renderExpenseCategoryChart(data);
            });
    });

    document.getElementById('budgetForm').addEventListener('submit', function(event) {
        event.preventDefault();
        const amount = parseFloat(document.getElementById('budgetAmount').value) || 0;
        updateFinancialData('budgetGoals', amount)
            .then(fetchFinancialData)
            .then(data => {
                renderFinancialData(data);
                renderFinancialChart(data);
                renderExpenseCategoryChart(data);
            });
    });

    document.getElementById('savingsForm').addEventListener('submit', function(event) {
        event.preventDefault();
        const amount = parseFloat(document.getElementById('savingsAmount').value) || 0;
        updateSavingsData(amount)
            .then(fetchFinancialData)
            .then(data => {
                renderFinancialData(data);
                renderFinancialChart(data);
                renderExpenseCategoryChart(data);
            });
    });

    loadQuote();
    setInterval(loadQuote, 120000); // Reload quote every 2 minutes

    loadEvents()
        .then(events => {
            renderCalendar(events);
            return fetchFinancialData();
        })
        .then(data => {
            renderFinancialData(data);
            renderFinancialChart(data);
            renderExpenseCategoryChart(data);
        })
        .catch(error => console.error('Error rendering initial data:', error));
});
