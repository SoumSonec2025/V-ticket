const API_BASE_URL = 'http://localhost:5000/api';

// QR Code Page Logic
if (document.getElementById('select-service-btn')) {
    console.log('Attaching event listener to select-service-btn');
    document.getElementById('select-service-btn').addEventListener('click', () => {
        console.log('Select service button clicked');
        try {
            window.location.href = '/visitor.html';
        } catch (error) {
            console.error('Error redirecting to visitor.html:', error);
        }
    });
    document.getElementById('scan-qr-btn').addEventListener('click', () => {
        console.log('Scan QR button clicked');
        window.location.href = '/visitor.html';
    });
    pollEstimatedWait();
}

// Visitor Interface Logic
if (document.getElementById('service-buttons')) {
    fetchServices();
    document.getElementById('get-ticket-btn').addEventListener('click', createTicket);
}

async function fetchServices() {
    try {
        console.log('Fetching services...');
        const response = await fetch(`${API_BASE_URL}/services`);
        if (!response.ok) throw new Error(`Failed to fetch services: ${response.statusText}`);
        const services = await response.json();
        console.log('Services fetched:', services);
        const serviceButtons = document.getElementById('service-buttons');
        if (!serviceButtons) throw new Error('Service buttons container not found');
        serviceButtons.innerHTML = '';
        let selectedServiceId = null;

        services.forEach(service => {
            const button = document.createElement('button');
            button.className = 'btn btn-outline-primary rounded-pill px-3 py-2';
            button.textContent = service.name;
            button.dataset.serviceId = service.id;
            button.addEventListener('click', () => {
                serviceButtons.querySelectorAll('button').forEach(btn => {
                    btn.classList.remove('btn-primary');
                    btn.classList.add('btn-outline-primary');
                });
                button.classList.remove('btn-outline-primary');
                button.classList.add('btn-primary');
                selectedServiceId = service.id;
                document.getElementById('get-ticket-btn').disabled = false;
            });
            serviceButtons.appendChild(button);
        });

        document.getElementById('get-ticket-btn').disabled = true;
    } catch (error) {
        console.error('Error fetching services:', error);
    }
}

async function createTicket() {
    const selectedServiceId = document.querySelector('#service-buttons .btn-primary')?.dataset.serviceId;
    if (!selectedServiceId) {
        alert('Please select a service first');
        return;
    }
    try {
        const response = await fetch(`${API_BASE_URL}/tickets`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ service_id: selectedServiceId })
        });
        if (!response.ok) throw new Error('Failed to create ticket');
        const ticket = await response.json();
        window.location.href = `/ticket.html?ticketId=${ticket.id}`;
    } catch (error) {
        console.error('Error creating ticket:', error);
    }
}

// Ticket Page Logic
if (document.getElementById('ticket-number')) {
    const urlParams = new URLSearchParams(window.location.search);
    const ticketId = urlParams.get('ticketId');
    fetchTicketDetails(ticketId);
    document.getElementById('cancel-ticket-btn').addEventListener('click', () => cancelTicket(ticketId));
}

async function fetchTicketDetails(ticketId) {
    try {
        const response = await fetch(`${API_BASE_URL}/tickets/${ticketId}`);
        if (!response.ok) throw new Error('Failed to fetch ticket');
        const ticket = await response.json();
        document.getElementById('service-name').textContent = ticket.service_name;
        document.getElementById('ticket-number').textContent = ticket.ticket_number;
        let waitTime = Math.ceil(ticket.estimated_wait_time);
        document.getElementById('wait-time').textContent = `${waitTime} min`;
        startCountdown(waitTime * 60);
    } catch (error) {
        console.error('Error fetching ticket details:', error);
    }
}

function startCountdown(seconds) {
    const countdownElement = document.getElementById('countdown');
    const interval = setInterval(() => {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        countdownElement.textContent = `Temps restant: ${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
        if (seconds <= 0) {
            clearInterval(interval);
            countdownElement.textContent = "C'est à votre tour !";
        }
        seconds--;
    }, 1000);
}

async function cancelTicket(ticketId) {
    try {
        const response = await fetch(`${API_BASE_URL}/tickets/${ticketId}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Failed to cancel ticket');
        window.location.href = '/index.html';
    } catch (error) {
        console.error('Error cancelling ticket:', error);
    }
}

async function pollEstimatedWait() {
    const interval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/queue`);
            if (!response.ok) throw new Error('Failed to fetch queue status');
            const data = await response.json();
            const avgWait = data.stats.avg_wait_time;
            document.getElementById('estimated-wait')?.textContent == `${Math.ceil(avgWait)} min`;
        } catch (error) {
            console.error('Error polling estimated wait:', error);
        }
    }, 5000);
}

// Admin Interface
if (document.getElementById('service-form')) {
    document.getElementById('service-form').addEventListener('submit', addService);
    fetchAdminServices();
    pollQueueStatusAdmin();
}

async function addService(e) {
    e.preventDefault();
    const name = document.getElementById('service-name').value.trim();
    if (!name) {
        alert('Please enter a service name');
        return;
    }
    try {
        console.log('Adding service:', name);
        const response = await fetch(`${API_BASE_URL}/services`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': 'admin-key'
            },
            body: JSON.stringify({ name })
        });
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Failed to add service: ${response.status} - ${errorText}`);
        }
        const result = await response.json();
        console.log('Service added successfully:', result);
        document.getElementById('service-form').reset();
        fetchAdminServices();
    } catch (error) {
        console.error('Error adding service:', error);
        alert('Failed to add service. Check console for details.');
    }
}

async function fetchAdminServices() {
    try {
        const response = await fetch(`${API_BASE_URL}/services`);
        if (!response.ok) throw new Error('Failed to fetch services');
        const services = await response.json();
        console.log('Admin services fetched:', services);
        const list = document.getElementById('service-list');
        list.innerHTML = '';
        services.forEach(service => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.innerHTML = `${service.name} <button class="btn btn-sm btn-danger rounded-pill" onclick="deleteService(${service.id})">Delete</button>`;
            list.appendChild(li);
        });
    } catch (error) {
        console.error('Error fetching services:', error);
    }
}

async function deleteService(serviceId) {
    try {
        const response = await fetch(`${API_BASE_URL}/services/${serviceId}`, {
            method: 'DELETE',
            headers: { 'X-API-Key': 'admin-key' }
        });
        if (!response.ok) throw new Error('Failed to delete service');
        fetchAdminServices();
    } catch (error) {
        console.error('Error deleting service:', error);
    }
}

async function pollQueueStatusAdmin() {
    const table = document.getElementById('queue-table');
    const totalTickets = document.getElementById('total-tickets');
    const avgWaitTime = document.getElementById('avg-wait-time');
    const waitTimeChart = document.getElementById('waitTimeChart')?.getContext('2d');
    const serviceDistributionChart = document.getElementById('serviceDistributionChart')?.getContext('2d');

    if (!waitTimeChart || !serviceDistributionChart) {
        console.error('Chart canvases not found');
        return;
    }

    let waitTimeData = {
        labels: [],
        datasets: [{
            label: 'Average Wait Time (min)',
            data: [],
            borderColor: 'rgba(75, 192, 192, 1)',
            fill: false
        }]
    };

    let serviceDistData = {
        labels: [],
        datasets: [{
            data: [],
            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
        }]
    };

    const waitTimeChartInstance = new Chart(waitTimeChart, {
        type: 'line',
        data: waitTimeData,
        options: { responsive: true, scales: { y: { beginAtZero: true } } }
    });

    const serviceDistChartInstance = new Chart(serviceDistributionChart, {
        type: 'pie',
        data: serviceDistData,
        options: { responsive: true }
    });

    setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/queue`);
            if (!response.ok) throw new Error('Failed to fetch queue status');
            const data = await response.json();
            table.innerHTML = '';
            data.tickets.forEach(ticket => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${ticket.ticket_number}</td>
                    <td>${ticket.service_name}</td>
                    <td>${ticket.status}</td>
                    <td>${ticket.estimated_wait_time}</td>
                `;
                table.appendChild(row);
            });
            totalTickets.textContent = data.stats.total_tickets;
            avgWaitTime.textContent = data.stats.avg_wait_time;

            waitTimeData.labels.push(new Date().toLocaleTimeString());
            waitTimeData.datasets[0].data.push(data.stats.avg_wait_time);
            if (waitTimeData.labels.length > 10) {
                waitTimeData.labels.shift();
                waitTimeData.datasets[0].data.shift();
            }
            waitTimeChartInstance.update(); // Correct function call

            const serviceCounts = {};
            data.tickets.forEach(ticket => {
                serviceCounts[ticket.service_name] = (serviceCounts[ticket.service_name] || 0) + 1;
            });
            serviceDistData.labels = Object.keys(serviceCounts);
            serviceDistData.datasets[0].data = Object.values(serviceCounts);
            serviceDistChartInstance.update(); // Correct function call
        } catch (error) {
            console.error('Error polling queue status:', error);
        }
    }, 5000);
}