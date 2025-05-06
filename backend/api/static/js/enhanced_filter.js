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
      
          // Build the badge
          const badge = document.createElement('span');
          badge.className = 'badge bg-secondary me-1';
          badge.textContent = `${field}: ${value}`;    // or use a nicer label if you read data-display
      
          // The “×” icon
          const x = document.createElement('i');
          x.className = 'fas fa-times ms-1';
          x.style.cursor = 'pointer';
      
          x.addEventListener('click', () => {
            // **re-query** the *current* checkbox in the sidebar
            const selector = `.filter-checkbox[value="${field}:${value}"]`;
            const cb = document.querySelector(selector);
            if (cb) {
              cb.checked = false;
              updateView();   // now gathers from the live inputs
            }
          });
      
          badge.appendChild(x);
          container.appendChild(badge);
        });
      }
      

    // 4) Core Function: gather filters, show badges, POST to Django, then update sidebar
    // and table
    function updateView() {
        const data = gatherFilters();

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

            const freshData = gatherFilters();

            renderActiveFilters(freshData);

            renderActiveFilters(data);
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

    // 6) Auto Grow Elements for large text boxes
    function auto_grow(el) {
        el.style.height = 'auto';
        el.style.height = el.scrollHeight + 'px';
    }

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

    async function uploadAttachment() {
        const fileInput = document.getElementById('attachment');
        if (!fileInput || fileInput.files.length === 0) {
            return null;
        }

        const file = fileInput.files[0];
        const fd = new FormData();
        fd.append('attachment', file);

        const response = await fetch('/api/upload-tmp', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrfToken'),
            },
            body: fd
        });

        if(!response.ok) {
            throw new Error('Upload failed');
        }
        return response.json();
    }

    // 7) Wire up events and inital load
    function init(){

        // Email Checker and confirmation system
        // Ensures no missing mandatory items and gives user confirmation box before sending
        const form = document.getElementById('emailForm');
        const sendBtn = document.getElementById('sendEmailBtn');
        const subjectEl = document.getElementById('subject');
        const bodyEl = document.getElementById('body');
        const cbs =  [
            {el: document.getElementById('personalEmail'), label: 'Personal Emails'},
            {el: document.getElementById('parishEmail'), label: 'Parish Emails'},
            {el: document.getElementById('diocesanEmail'), label: 'Diocesan Emails'},
        ];

        sendBtn.addEventListener('click', async (e) => {
            e.preventDefault();

            // trim and test mandatory items
            const subj = subjectEl.value.trim();
            const bdy = bodyEl.value.trim();
            const checked = cbs
                .filter(cb => cb.el.checked)
                .map(cb => cb.label);

            // gather missing
            const missing = [];
            if(!subj)   missing.push('Subject');
            if(!bdy)    missing.push('Body');
            if(!checked.length) missing.push('At least one recipient type');

            if (missing.length) {
                alert('Please provide: ' + missing.join(', '));
                return;
            }

            const summary =
            ` Please confirm before sending:\n\n` +
            `Subject: ${subj}\n` +
            `Recipients: ${checked.join(', ')}\n\n` +
            `Body:\n${bdy}`;

            if(!confirm(summary)) {
                // user cancelled
                return;
            }

            try {
                const uploadResult = await uploadAttachment();
                if (uploadResult && uploadResult.url) {
                    // inject hidden field with temp path
                    let hidden = form.querySelector('input[name="temp_attachment_path"]');
                    if (!hidden) {
                        hidden = document.createElement('input');
                        hidden.type = 'hidden';
                        hidden.name = 'temp_attachment_path';
                        form.appendChild(hidden);
                    }
                    hidden.value = uploadResult.url;
                }
            } catch (err) {
                alert('Failed to upload attachment: ' + err.message);
                return;
            }

            // all good actually submit
            form.submit();

        });

        // Used for auto growing the input box for email body.
        auto_grow(bodyEl)
        bodyEl.addEventListener('input', () => auto_grow(bodyEl));

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