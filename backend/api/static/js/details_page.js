(function () {
    const links = document.querySelectorAll('.aside-panel .nav-link');
    const panels = document.querySelectorAll('.detail-section');

    function showPanel(id) {
        panels.forEach(p => p.id === id
            ? p.classList.remove('d-none')
            : p.classList.add   ('d-none'));
    }

    function linking() {
        links.forEach(link =>{
            link.addEventListener('click', e => {
                e.preventDefault();
                // toggle active class on links
                links.forEach(l => l.classList.remove('active'));
                link.classList.add('active');

                // show corresponding panel
                const target = link.dataset.target;
                showPanel(target);
            });
        });
    }

    function init() {
        linking();
    }

    // run init() once the DOM is ready
    if(document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();