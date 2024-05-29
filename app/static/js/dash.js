document.addEventListener('DOMContentLoaded', function() {
    // Function to load events from the server
    function loadEvents() {
        return fetch('/api/events')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to load events');
                }
                return response.json();
            })
            .catch(error => {
                console.error('Error fetching events:', error);
                return [];
            });
    }

    // Initialize FullCalendar with events from the server
    loadEvents().then(events => {
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

                    // Save event to the server
                    fetch('/api/events', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(eventData)
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Failed to save event');
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log(data.message);
                    })
                    .catch(error => {
                        console.error('Error saving event:', error);
                    });
                }
            },
            eventClick: function(info) {
                if (confirm('Are you sure you want to delete this event?')) {
                    info.event.remove();

                    // Delete event from the server
                    fetch(`/api/events/${info.event.id}`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Failed to delete event');
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log(data.message);
                    })
                    .catch(error => {
                        console.error('Error deleting event:', error);
                    });
                }
            } 
        });
        calendar.render();
    });
});

// Fetch and display a random quote
function fetchQuote() {
    fetch('https://api.quotable.io/random?tags=finance|inspirational')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch quote');
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('quote').textContent = `"${data.content}" - ${data.author}`;
        })
        .catch(error => {
            console.error('Error fetching the quote:', error);
            document.getElementById('quote').textContent = "Stay positive and keep tracking your finances!";
        });
}

// Fetch the initial quote
fetchQuote();

// Fetch a new quote every 1 minute (60000 milliseconds)
setInterval(fetchQuote, 60000);
