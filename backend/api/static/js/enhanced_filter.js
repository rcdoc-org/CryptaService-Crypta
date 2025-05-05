(function() {
    // read config values injected into the page
    const csrfToken         = document.querySelector('meta[name="csrf-token"]').content;
    const filterURL         = document.querySelector('meta[name="filter-url"]').content;
    const filterSidebar     = document.getElementById('filterSidebar');
    const baseRadios        = document.getElementsByName('baseToggle');
    const columnForm        = document.getElementById('columnForm');
    const applyBtn          = document.getElementById('applyColumnsBtn');
    
    let currentColumns      = [];   // will hold {title, field}[]

    let table;                      // Tabulator Instance

    // 1) Gather which filters are check + which base (person/location) is selected.
    function gatherFilters() {
        const checked = Array.from(
            filterSidebar.querySelectorAll('input.filter-checkbox:checked')
            ).map(chk => chk.value);
        const base = Array.from(baseRadios).find(r => r.checked).value;
        return { base, filters: checked };
    }

    // 2) Replace the sidebar HTML wholesale with the server-rendered version
    function renderFilters(html) {
        filterSidebar.innerHTML = html;
    }

    // 3) Render 'active' filter badges at the top, with an X to remove each one.
    function renderActiveFilters(data) {
        const container = document.getElementById('activeFilters');
        container.innerHTML = '';

        data.filters.forEach(f => {
            const [field, value] = f.split(':', 2);
            // find the checkbox so we can read it's data-display
            // Uses a friendly label
            const cb = filterSidebar.querySelector(`input[value="${field}:${value}"]`);
            const label = cb?.dataset.display ?? field;

            const badge = document.createElement('span');
            badge.className = 'badge bg-secondary me-1';
            badge.textContent = `${label}: ${value}`;

            const x = document.createElement('i');
            x.className = 'fas fa-times ms-1';
            x.style.cursor = 'pointer';
            x.addEventListener('click', () => {
                cb.checked = false;         // uncheck it
                updateView();               // and re-fetch/update everything
            });

            badge.appendChild(x);
            container.appendChild(badge);
        });
    }

    // 4) Core Function: gather filters, show badges, POST to Django, then update sidebar
    // and table
    function updateView() {
        const data = gatherFilters();
        renderActiveFilters(data);

        fetch(filterURL, {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(payload => {
            // 1) Update the side bar
            renderFilters(payload.filters_html);

            // 2) Initialize or update Tabulator
            if (!table) {
            table = new Tabulator('#data-grid', {
                layout: 'fitColumns',
                data: payload.grid.data,
                columns: payload.grid.columns,
                placeholder: 'No Data Available',
            });
            } else {
            table.setColumns(payload.grid.columns);
            table.setData(payload.grid.data);
            }

            // 3) Capture current columns & update modal form
            currentColumns = payload.grid.columns;
            populateColumnForm();
        });
    }

    // 5) Build the column-chooser form inside the modal
    function populateColumnForm() {
        columnForm.innerHTML = '';
        currentColumns.forEach(col => {
            // Tabulator's isColumnVisible api
            const isVisible = table?.getColumn(col.field)?.isVisible ?? true;
            const wrapper = document.createElement('div');
            wrapper.className = 'col-4 form-check';
            wrapper.innerHTML = `
            <input class='form-check-input'
                type='checkbox'
                id='col_${col.field}'
                value='${col.field}'
                ${isVisible ? 'checked' : ''}>
            <label class='form-check-label' for='col_${col.field}'>
                ${col.title}
            </label>
            `;
            columnForm.appendChild(wrapper); 
        });
    }

    // 6) Wire up events and inital load
    function init(){
        function getCookie(name) {
            let cookieValue = null;
            document.cookie.split(';').forEach(c => {
                c = c.trim();
                if (c.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(c.slice(name.length + 1));
                }
            });
            return cookieValue;
        }
        
        // When "Apply" is clicked, show/hide columns then close modal
        applyBtn.addEventListener('click', () => {
            const checkFields = Array.from(columnForm.querySelectorAll('input:checked'))
                                    .map(i=>i.value);
            
            currentColumns.forEach(col => {
                if (checkFields.includes(col.field)) {
                table.showColumn(col.field);
                } else {
                table.hideColumn(col.field);
                }
            });

            table.redraw(true);

            //bootstrap modal hide 
            const modalEl = document.getElementById('columnModal');
            bootstrap.Modal.getInstance(modalEl).hide();
        })

        // Whenever a filter checkbox or the base-toggle radio changes, re-fetch
        filterSidebar.addEventListener('change', updateView);
        baseRadios.forEach(r => r.addEventListener('change', updateView));

        // Delegate toggle and checkbox events
        updateView();
        }

        // run init() once the DOM is ready
        if(document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
        } else {
            init();
        }})();