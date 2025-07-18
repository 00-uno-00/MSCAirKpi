document.addEventListener('DOMContentLoaded', function () {
    if (!window.homeBtnListenerAttached) {
        //TODO trigger automatic operations on flightcycle update
        let unsavedChanges = false;
        const aircraftsDropdown = document.getElementById('aircraft'); // replace with your dropdown's actual id
        const aircraftOptions = Array.from(aircraftsDropdown.options).map(option => option.value);
        aircraftsDropdown.addEventListener('change', (event) => {
            const selectedAircraft = event.target.value;
            fetch(`/module/1/ac_data?aircraft=${selectedAircraft}`)
                .then(response => response.text())
                .then(html => {
                    const tableContainer = document.getElementById('main-table');
                    tableContainer.innerHTML = html;
                    if (typeof formatEntries === 'function') formatEntries();
                    if (typeof formatYearFinals === 'function') formatYearFinals();
                })

        });

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
                const url = `/module/1/get_table?start_date=${startDate}&end_date=${endDate}`;
                const res = await fetch(url);
                if (!res.ok) throw new Error('Network response was not ok');
                const html = await res.text();
                // Clear container and create iframe
                table_container.innerHTML = html;
                if (typeof formatEntries === 'function') formatEntries();
                if (typeof formatYearFinals === 'function') formatYearFinals();
            } catch (e) {
                table_container.innerHTML = 'Failed to load table.';
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
                const url = `/module/1/get_table?start_date=${startDate}&end_date=${endDate}`;
                const res = await fetch(url);
                if (!res.ok) throw new Error('Network response was not ok');
                const html = await res.text();
                // Clear container and create iframe
                table_container.innerHTML = html;
                if (typeof formatEntries === 'function') formatEntries();
                if (typeof formatYearFinals === 'function') formatYearFinals();
            } catch (e) {
                table_container.innerHTML = 'Failed to load table.';
                console.error(e);
            }
        };

        const submitButton = document.getElementById('submitButton');
        submitButton.addEventListener('click', (event) => {
            const form = document.getElementById('data_form');
            const inputs = form.querySelectorAll('input[type="text"]');
            let hasEmptyInput = false;
            let invalidInputs = [];

            // Validate inputs as before
            inputs.forEach(input => {
                if (input.value.trim() === '') {
                    hasEmptyInput = true;
                }
                if (input.value.trim() !== ''  && ((isNaN(input.value) || input.value < 0) && !input.value.includes(':'))) {
                    invalidInputs.push(input.id);
                }
            });

            if (hasEmptyInput) {
                event.preventDefault();
                alert('Please fill in all fields before submitting.');
                return;
            } else if (invalidInputs.length > 0) {
                event.preventDefault();
                alert('Please enter valid numbers for: ' + invalidInputs.join(', '));
                return;
            } else if (inputs.length === 0) {
                alert('No data to submit.');
                event.preventDefault();
                return;
            }
            if (!confirm('Are you sure you want to submit?')) {
                event.preventDefault();
                return;
            }

            // Build the list of SPI objects per aircraft
            event.preventDefault(); // We'll handle the submit via fetch
            const aircraftsDropdown = document.getElementById('aircraft');
            const aircraftOptions = Array.from(aircraftsDropdown.options).map(option => option.value);
            let dataList = [];

            for (const aircraft of aircraftOptions) {
                // Find all inputs for this aircraft (assuming input names/ids contain aircraft)
                const aircraftInputs = Array.from(inputs).filter(input => input.id.includes(`(${aircraft})`));
                if (aircraftInputs.length === 0) continue;
                let spiObj = { aircraft };
                aircraftInputs.forEach(input => {
                    // Use input.name as key, or input.id if name is not set
                    const key = input.id;
                    spiObj[key] = input.value;//TODO remove cuz not used
                });
                dataList.push(spiObj);
            }
            console.log('Data to submit:', dataList);

            // POST the dataList as JSON
            fetch('/module/1/submit_spis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(dataList)
            })
            .then(response => {
                if (!response.ok) throw new Error('Submission failed');
                return response.json();
            })
            .then(data => {
                alert('Submission successful!');
                // Optionally redirect or update UI
            })
            .catch(error => {
                alert('Error submitting data: ' + error.message);
            });
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

        for (aircraft of aircraftOptions) {
            //add event listeners so that we can give a preview of the auto values
            const fhrs_c = document.getElementById(`Flight hours per cycle -(${aircraft})-`);
            const fhrs = document.getElementById(`Flight time -(${aircraft})- block hours (HH:MM) - COM flights only`);
            const fcs = document.getElementById(`Flight cycles -(${aircraft})- COM flights only`);

            if (fhrs && fcs && fhrs_c) {
                fhrs.addEventListener('input', () => {
                    if (fhrs.value && fcs.value) {
                        const [hours, minutes] = fhrs.value.split(':').map(Number);
                        const totalMinutes = hours * 60 + minutes;
                        const cycleHours = totalMinutes / parseFloat(fcs.value);
                        const cycleHrs = Math.floor(cycleHours / 60);
                        const cycleMins = Math.round(cycleHours % 60);
                        fhrs_c.innerHTML = `${cycleHrs}:${cycleMins.toString().padStart(2, '0')}`; // format as HH:MM
                    } else {
                        fhrs_c.innerHTML = '';
                    }
                });

                fcs.addEventListener('input', () => {
                    if (fhrs.value && fcs.value) {
                        const [hours, minutes] = fhrs.value.split(':').map(Number);
                        const totalMinutes = hours * 60 + minutes;
                        const cycleHours = totalMinutes / parseFloat(fcs.value);
                        const cycleHrs = Math.floor(cycleHours / 60);
                        const cycleMins = Math.round(cycleHours % 60);
                        fhrs_c.innerHTML = `${cycleHrs}:${cycleMins.toString().padStart(2, '0')}`; // format as HH:MM
                    } else {
                        fhrs_c.innerHTML = '';
                    }
                });
            }
            const AC_utilization = document.getElementById(`Aircraft daily utilization per month -(${aircraft})-`);
            if (AC_utilization && fhrs && fcs) {
                fcs.addEventListener('input', () => {
                    if (fhrs.value && fcs.value) {
                        const [hours, minutes] = fhrs.value.split(':').map(Number);
                        const totalMinutes = hours * 60 + minutes;
                        //number of days in the month
                        const daysInMonth = new Date(new Date().getFullYear(), new Date().getMonth(), 0).getDate();
                        const dailyTotMins = Math.floor(totalMinutes / daysInMonth);
                        const dailyMins = dailyTotMins % 60;
                        // Update the innerHTML of AC_utilization
                        AC_utilization.innerHTML = `${Math.floor(dailyTotMins / 60)}:${dailyMins.toString().padStart(2, '0')}`; // format as HH:MM
                    } else {
                        AC_utilization.innerHTML = '';
                    }
                });

            fhrs.addEventListener('input', () => {
                if (fhrs.value && fcs.value) {
                    const [hours, minutes] = fhrs.value.split(':').map(Number);
                    const totalMinutes = hours * 60 + minutes;
                    //number of days in the month
                    const daysInMonth = new Date(new Date().getFullYear(), new Date().getMonth(), 0).getDate();
                    const dailyTotMins = Math.floor(totalMinutes / daysInMonth);
                    const dailyMins = dailyTotMins % 60;
                    // Update the innerHTML of AC_utilization
                    AC_utilization.innerHTML = `${Math.floor(dailyTotMins / 60)}:${dailyMins.toString().padStart(2, '0')}`; // format as HH:MM
                } else {
                    AC_utilization.innerHTML = '';
                }
            });
                
            }
        }

        //get all elements that have aircraft inside, get the value of inputs and save name value passed as path
        document.getElementById('data_form').addEventListener('blur', async function (event) {
            if (event.target.matches('input[type="text"]')) {
                const entry = document.getElementById(event.target.id);
                if (!entry) return; // If the entry is not found, exit
                const formData = new FormData();
                formData.append(entry.name, entry.value);

                const res = await fetch(`/module/1/save/${event.target.id}`, {
                    method: 'POST',
                    body: formData
                });

                if (!res.ok) {
                    console.error('Failed to save data');
                } else {
                    unsavedChanges = false;
                    console.log('Data saved successfully');
                }
            }
        }, true); // Use capture phase for blur

        //get all from list, add specific listener based on list to preview auto values
        
        //select inputs in pairs that contain the same aircraft id


        
        window.homeBtnListenerAttached = true; // Flag to prevent multiple attachments
    }
});