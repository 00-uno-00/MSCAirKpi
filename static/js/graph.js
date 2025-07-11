document.addEventListener('DOMContentLoaded', function () {
    const openBtn = document.getElementById('openBtn');
    const modal = document.getElementById('modal');
    const closeBtn = document.getElementById('closeBtn');
    const graphContainer = document.getElementById('graph-container');
    const sticky = document.getElementsByClassName('sticky-col');
    let unsavedChanges = false;
    if (!window.homeBtnListenerAttached) {
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
    }
});