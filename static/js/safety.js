document.addEventListener('DOMContentLoaded', function () {
    const openBtn = document.getElementById('openBtn');
    const modal = document.getElementById('modal');
    const closeBtn = document.getElementById('closeBtn');
    const graphContainer = document.getElementById('graph-container');
    const sticky = document.getElementsByClassName('sticky-col');
    let unsavedChanges = false;

    openBtn.onclick = async () => {
        for (let i = 0; i < sticky.length; i++) {
            sticky[i].style.zIndex = 0;
        }
        modal.style.display = 'block';
        graphContainer.innerHTML = 'Loading...';

        try {
            const res = await fetch('/module/3/graphs');
            if (!res.ok) throw new Error('Network response was not ok');
            const html = await res.text();
            // Clear container and create iframe
            graphContainer.innerHTML = '';
            const iframe = document.createElement('iframe');
            iframe.style.width = '100%';
            iframe.style.height = '80vh';
            iframe.style.border = 'none';
            iframe.srcdoc = html;  // Insert full HTML as iframe content
            graphContainer.appendChild(iframe);
        } catch (e) {
            graphContainer.innerHTML = 'Failed to load graph.';
            console.error(e);
        }
    };
    closeBtn.onclick = () => {
        modal.style.display = 'none';
        graphContainer.innerHTML = '';  // clear graph HTML on close (optional)
    };

    window.onclick = (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
            graphContainer.innerHTML = '';
        }
    }

    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    startDateInput.onchange = async () => {
        const table_container = document.getElementById('main-table');
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        if (startDate > endDate) {
            alert('Start date cannot be after end date.');
            endDateInput.value = '';
        }

        //perform unsaved changes check
        const form = document.getElementById('data_form');
        const inputs = form.querySelectorAll('input[type="text"]');
        inputs.forEach(input => {
            if (input.value.trim() !== '') {
                unsavedChanges = true;
            }
        });

        //perform get request to update the table
        try {
            const url = `/module/3/get_table?start_date=${startDate}&end_date=${endDate}`;
            const res = await fetch(url);
            if (!res.ok) throw new Error('Network response was not ok');
            const html = await res.text();
            // Clear container and create iframe
            table_container.innerHTML = html;
        } catch (e) {
            table_container.innerHTML = 'Failed to load graph.';
            console.error(e);
        }
    };

    endDateInput.onchange = async () => {
        const table_container = document.getElementById('main-table');
        const startDate = new Date(startDateInput.value);
        const endDate = new Date(endDateInput.value);
        if (startDate > endDate) {
            alert('Start date cannot be after end date.');
            endDateInput.value = '';
        }

        //perform unsaved changes check
        const form = document.getElementById('data_form');
        const inputs = form.querySelectorAll('input[type="text"]');
        inputs.forEach(input => {
            if (input.value.trim() !== '') {
                unsavedChanges = true;
            }
        });

        //perform get request to update the table
        try {
            const res = await fetch('/module/3/get_table');
            if (!res.ok) throw new Error('Network response was not ok');
            const html = await res.text();
            // Clear container and create iframe
            table_container.innerHTML = html;
        } catch (e) {
            table_container.innerHTML = 'Failed to load graph.';
            console.error(e);
        }
    };

    const submitButton = document.getElementById('submitButton');
    submitButton.addEventListener('click', (event) => {
        const form = document.getElementById('data_form');
        const inputs = form.querySelectorAll('input[type="text"]');
        let hasEmptyInput = false;
        let invalidInputs = [];

        inputs.forEach(input => {
            if (input.value.trim() === '') {
                hasEmptyInput = true;
            }
            if (input.value.trim() !== '' && (isNaN(input.value) || parseInt(input.value) < 0)) {
                invalidInputs.push(input.id);
            }
        });

        if (hasEmptyInput) {
            event.preventDefault();
            alert('Please fill in all fields before submitting.');
        } else if (invalidInputs.length > 0) {
            event.preventDefault();
            alert('Please enter valid numbers for: ' + invalidInputs.join(', '));
        } else if (inputs.length === 0) {
            alert('No data to submit.');
            event.preventDefault();
        }
        else {
            if (!confirm('Are you sure you want to submit?')) {
                event.preventDefault();
            }
        }
    });

    const homeBtn = document.getElementById('homeBtn');
    homeBtn.addEventListener('click', () => {
        const form = document.getElementById('data_form');
        const inputs = form.querySelectorAll('input[type="text"]');
        inputs.forEach(input => {
            if (input.value.trim() !== '') {
                unsavedChanges = true;
            }
        });

        if (unsavedChanges) {
            if (!confirm('You have unsaved changes. Are you sure you want to go home?')) {
                return;
            }
        }
        window.location.href = '/';
    });

    
    const inputs = document.querySelectorAll('input[type="text"]');
    inputs.forEach(input => {
        input.onblur = async () => {
            const form = document.getElementById('data_form');
            const formData = new FormData(form);

            const res = await fetch('/module/3/save', {
                method: 'POST',
                body: formData
            });

            if (!res.ok) {
                console.error('Failed to save data');
            } else {
                unsavedChanges = false; // Reset unsaved changes flag after successful save
                console.log('Data saved successfully');
            }
        }
    });

});