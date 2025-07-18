document.addEventListener('DOMContentLoaded', function () {
    formatEntries();
    formatYearFinals();
});

// scale from rgba(0, 255, 0, 0.4) to rgba(255, 0, 0, 0.4)
function colorLess(value, target, equal = false) {
    if (!Array.isArray(target)) {
        if (value < target) {
            return 'rgba(0, 255, 0, 0.4)';
        } else if (value > target) {
            return 'rgba(255, 0, 0, 0.4)';
        }
        if (equal) {
            return 'rgba(255, 255, 0, 0.4)'; // equal to target
        } else {
            return 'rgba(255, 128, 0, 0.4)'; // not equal to target
        }
    } else {
        colorlist = ['rgba(0, 255, 0, 0.4)', 'rgba(255, 255, 0, 0.4)', 'rgba(255, 128, 0, 0.4)', 'rgba(255, 0, 0, 0.4)'];
        for (let i = 0; i < target.length; i++) {
            if (value < target[i]) {
                return colorlist[i];
            }
        }
    }
}

function colorGreater(value, target, equal = false) {
    if (!Array.isArray(target)) {
        if (value > target) {
            return 'rgba(0, 255, 0, 0.4)';
        } else if (value < target) {
            return 'rgba(255, 0, 0, 0.4)';
        }
        if (equal) {
            return 'rgba(255, 255, 0, 0.4)'; // equal to target
        } else {
            return 'rgba(255, 128, 0, 0.4)'; // not equal to target
        }
    } else {
        colorlist = ['rgba(0, 255, 0, 0.4)','rgba(255, 255, 0, 0.4)','rgba(255, 128, 0, 0.4)','rgba(255, 0, 0, 0.4)'];
        for (let i = 0; i < target.length; i++) {
            if (value > target[i]) {
                return colorlist[i];
            }
        }
        return 'rgba(255, 0, 0, 0.4)'; // if no condition met, return red
    }
}

// format the table
function formatEntries() {
    const table = document.getElementById('myTable');
    const rows = table.getElementsByTagName('tr');
    const cookiesNames = getCookies();
    for (let i = 1; i < rows.length; i++) { // skip header row
        const cells = rows[i].getElementsByTagName('td');
        if (cells.length > 0) {
            let targetCell = cells[cells.length - 2]; //the second last cell = target
            targetValue = targetCell.textContent;
            sign = targetValue.slice(0, 1); // get the sign
            targetValue = targetValue.slice(1); // remove the sign
            try {
                targetValue = parseFloat(targetValue);
            } catch (error) {
                console.error('Error parsing target value:', error);
                targetValue = targetValue.slice(0, -1); // remove '%' if present
                targetValue = parseFloat(targetValue);
            }
            let descriptionCell = cells[0];
            if (cookiesNames.some(obj => obj.id === parseInt(rows[i].attributes.name.textContent))) {
                retrievedValue = eatCookie(`id_${rows[i].attributes.name.textContent}`);
                if (retrievedValue) {
                    retrievedValue = retrievedValue.replace(/\\054/g, ',');
                    retrievedValue = retrievedValue.slice(1, -1);
                    targetValue = retrievedValue.split(',').map(Number);
                }
            }
            for (let j = 1; j < cells.length - 5; j++) { // color only monthly entries
                const valueCell = cells[j];
                let value = valueCell.textContent;
                if (value === '-') {
                    value = 0; // treat '-' as 0
                }
                value = parseFloat(value);

                // Set background color based on the target
                if (!isNaN(value) && targetValue !== null) {//frontend made me lose my hair
                    switch (sign) {
                        case '≥':
                            valueCell.style.backgroundColor = colorGreater(value, targetValue, true);
                            break;
                        case '≤':
                            valueCell.style.backgroundColor = colorLess(value, targetValue, true);
                            break;
                        case '>':
                            valueCell.style.backgroundColor = colorGreater(value, targetValue);
                            break;
                        case '<':
                            if (cookiesNames && retrievedValue) {
                                valueCell.style.backgroundColor = colorLess(value, targetValue);
                            } else {
                                valueCell.style.backgroundColor = colorLess(value, targetValue);
                            }
                            break;
                        default:
                            break;
                    }
                }
            }

        }
    }
}

function formatYearFinals() {
    const table = document.getElementById('myTable');
    const rows = table.getElementsByTagName('tr');
    const cookiesNames = getCookies();
    for (let i = 1; i < rows.length; i++) { // skip header row
       const cells = rows[i].getElementsByTagName('td');
       if (cells.length > 0) {
            let targetCell = cells[cells.length - 2]; //the second last cell = target
            targetValue = targetCell.textContent;
            sign = targetValue.slice(0, 1); // get the sign
            targetValue = targetValue.slice(1); // remove the sign
            try {
                targetValue = parseFloat(targetValue);
            } catch (error) {
                console.error('Error parsing target value:', error);
                targetValue = targetValue.slice(0, -1); // remove '%' if present
                targetValue = parseFloat(targetValue);
            }
            
            for (let j = cells.length - 5; j < cells.length - 2; j++) { // color only monthly entries
                const valueCell = cells[j];
                let value = valueCell.textContent;
                if (value === '-') {
                    value = 0; // treat '-' as 0
                }
                value = parseFloat(value);

                // Set background color based on the target
                if (!isNaN(value) && targetValue !== null) {//frontend made me lose my hair
                    switch (sign) {
                        case '≥':
                            valueCell.style.backgroundColor = colorGreater(value, targetValue, true);
                            break;
                        case '≤':
                            valueCell.style.backgroundColor = colorLess(value, targetValue, true);
                            break;
                        case '>':
                            valueCell.style.backgroundColor = colorGreater(value, targetValue);
                            break;
                        case '<':
                            valueCell.style.backgroundColor = colorLess(value, targetValue);
                            break;
                        default:
                            break;
                    }
                }
            }

        }
    }

}

function getCookies() {
    // reads the cookie wich contains the targets for each entry type
    const value = `; ${document.cookie}`;
    const parts = value.split(';');
    for (i = 0; i < parts.length; i++) {
        if (parts[i].startsWith(' spis=')) {
            let cleaned = parts[i].replace(' spis=', '');
            cleaned = cleaned.replace(/\\054/g, ',');
            try {
                cleaned = cleaned.replace(/\\/g, '');
                cleaned = cleaned.slice(2, -2);

                if (!cleaned.startsWith('[')) {
                    cleaned = `[${cleaned}]`;
                }
                try {
                    return JSON.parse(cleaned);
                } catch (e) {
                    console.error('Error parsing JSON from cookie:', e);
                }
                return JSON.parse(cleaned);
            } catch (e) {
                console.error('Error parsing JSON from cookie:', e);
            }
        }
    }
    return null;
}

function eatCookie(name) {
    // returns value of the cookie and deletes it
    const value = `; ${document.cookie}`;
    const parts = value.split(';');
    for (let i = 0; i < parts.length; i++) {
        if (parts[i].trim().startsWith(`${name}=`)) {
            const cookieValue = parts[i].split('=')[1];
            document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
            return cookieValue;
        }
    }
    return null; // Cookie not found
}