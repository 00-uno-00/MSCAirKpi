function showgraphs() {
    fetch('/module/3/graphs')
        .then(response => response.text())
        .then(html => {
            const plotContainer = document.getElementById('plot-container');
            plotContainer.innerHTML = html;
            plotContainer.style.display = 'block';
        })
        .catch(error => console.error('Error fetching graph:', error));
}